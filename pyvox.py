import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox, font
import threading
import subprocess
import sys
import os
import re
import json
import time
from datetime import datetime
import speech_recognition as sr
import pyttsx3
import google.generativeai as genai
from queue import Queue
import tempfile

class VoicePythonIDE:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Voice-Activated Python IDE with Chat")
        self.root.geometry("1400x900")
        self.root.configure(bg='#2b2b2b')
        self.current_file = None
        self.is_listening = False
        self.voice_queue = Queue()
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.tts_engine = pyttsx3.init()
        self.tts_engine.setProperty('rate', 150)
        self.setup_gemini_api()
        self.setup_gui()
        self.setup_voice_recognition()
        self.voice_thread = threading.Thread(target=self.process_voice_commands, daemon=True)
        self.voice_thread.start()
    def setup_gemini_api(self):
        try:
            api_key = "AIzaSyBwepEkfaQqeTrKKhJuERytq-S2SLLl2Uk"
            genai.configure(api_key=api_key)
            self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
            self.gemini_available = True
        except Exception as e:
            self.gemini_available = False
            print(f"Gemini API setup failed: {e}")
    
    def setup_gui(self):
        style = ttk.Style()
        style.theme_use('clam')
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.setup_toolbar(main_frame)
        paned_window = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        left_panel = ttk.Frame(paned_window)
        paned_window.add(left_panel, weight=3)
        right_panel = ttk.Frame(paned_window)
        paned_window.add(right_panel, weight=1)
        self.setup_left_panel(left_panel)
        self.setup_right_panel(right_panel)
    def setup_toolbar(self, parent):
        toolbar = ttk.Frame(parent)
        toolbar.pack(fill=tk.X, pady=(0, 10))
        ttk.Button(toolbar, text="New", command=self.new_file).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar, text="Open", command=self.open_file).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar, text="Save", command=self.save_file).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar, text="Save As", command=self.save_as_file).pack(side=tk.LEFT, padx=(0, 5))   
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=10, fill=tk.Y)
        ttk.Button(toolbar, text="Run", command=self.run_code).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar, text="Clear Terminal", command=self.clear_terminal).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=10, fill=tk.Y)
        self.voice_status_label = ttk.Label(toolbar, text="Voice: Off", foreground="red")
        self.voice_status_label.pack(side=tk.LEFT, padx=(0, 10))
        self.start_voice_btn = ttk.Button(toolbar, text="Start Voice", command=self.start_voice_recognition)
        self.start_voice_btn.pack(side=tk.LEFT, padx=(0, 5))
        self.stop_voice_btn = ttk.Button(toolbar, text="Stop Voice", command=self.stop_voice_recognition, state=tk.DISABLED)
        self.stop_voice_btn.pack(side=tk.LEFT, padx=(0, 5))
    def setup_left_panel(self, parent):
        notebook = ttk.Notebook(parent)
        notebook.pack(fill=tk.BOTH, expand=True)
        editor_frame = ttk.Frame(notebook)
        notebook.add(editor_frame, text="Code Editor")
        editor_container = ttk.Frame(editor_frame)
        editor_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        line_frame = ttk.Frame(editor_container)
        line_frame.pack(side=tk.LEFT, fill=tk.Y)
        self.line_numbers = tk.Text(line_frame, width=4, padx=3, takefocus=0,
                                   border=0, state='disabled', wrap='none',
                                   bg='#3c3c3c', fg='#858585', font=('Consolas', 10))
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)
        self.code_editor = scrolledtext.ScrolledText(
            editor_container, wrap=tk.NONE, font=('Consolas', 11),
            bg='#2b2b2b', fg='#ffffff', insertbackground='white',
            selectbackground='#404040', selectforeground='white'
        )
        self.code_editor.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.code_editor.bind('<Key>', self.on_code_change)
        self.code_editor.bind('<Button-1>', self.on_code_change)
        terminal_frame = ttk.Frame(notebook)
        notebook.add(terminal_frame, text="Terminal")
        self.terminal = scrolledtext.ScrolledText(
            terminal_frame, wrap=tk.WORD, font=('Consolas', 10),
            bg='#1e1e1e', fg='#00ff00', insertbackground='green'
        )
        self.terminal.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.append_to_terminal("Python Voice IDE Terminal Ready\n")
        self.append_to_terminal("=" * 40 + "\n")
        
    def setup_right_panel(self, parent):

        chat_frame = ttk.LabelFrame(parent, text="AI Chat Assistant")
        chat_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.chat_display = scrolledtext.ScrolledText(
            chat_frame, wrap=tk.WORD, font=('Arial', 10),
            bg='#f0f0f0', fg='#333333', height=20
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        input_frame = ttk.Frame(chat_frame)
        input_frame.pack(fill=tk.X, padx=5, pady=(0, 5))
        
        self.chat_input = ttk.Entry(input_frame, font=('Arial', 10))
        self.chat_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.chat_input.bind('<Return>', self.send_chat_message)
        
        ttk.Button(input_frame, text="Send", command=self.send_chat_message).pack(side=tk.RIGHT)
        
        voice_frame = ttk.LabelFrame(parent, text="Voice Status")
        voice_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.voice_status_text = scrolledtext.ScrolledText(
            voice_frame, wrap=tk.WORD, font=('Arial', 9),
            bg='#fffacd', fg='#333333', height=8
        )
        self.voice_status_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.add_chat_message("Assistant", "Hello! I'm your AI coding assistant. ")
    def setup_voice_recognition(self):
        try:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
            self.voice_status_text.insert(tk.END, "Voice recognition initialized successfully.\n")
        except Exception as e:
            self.voice_status_text.insert(tk.END, f"Voice setup error: {e}\n")
    
    def on_code_change(self, event=None):
        def update_line_numbers():
            self.line_numbers.config(state='normal')
            self.line_numbers.delete('1.0', tk.END)
            lines = self.code_editor.get('1.0', tk.END).count('\n')
            line_numbers_string = "\n".join(str(i) for i in range(1, lines + 1))
            self.line_numbers.insert('1.0', line_numbers_string)
            self.line_numbers.config(state='disabled')
        self.root.after_idle(update_line_numbers)
    
    def new_file(self):
        if messagebox.askyesno("New File", "Clear current editor content?"):
            self.code_editor.delete('1.0', tk.END)
            self.current_file = None
            self.root.title("Voice-Activated Python IDE - New File")
    def open_file(self):
        file_path = filedialog.askopenfilename(
            title="Open Python File",
            filetypes=[("Python files", "*.py"), ("All files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    self.code_editor.delete('1.0', tk.END)
                    self.code_editor.insert('1.0', content)
                    self.current_file = file_path
                    self.root.title(f"Voice-Activated Python IDE - {os.path.basename(file_path)}")
                    self.add_chat_message("System", f"Opened file: {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not open file: {e}")
    
    def save_file(self):
        if self.current_file:
            try:
                content = self.code_editor.get('1.0', tk.END + '-1c')
                with open(self.current_file, 'w', encoding='utf-8') as file:
                    file.write(content)
                self.add_chat_message("System", f"Saved file: {os.path.basename(self.current_file)}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file: {e}")
        else:
            self.save_as_file()
    def save_as_file(self):
        file_path = filedialog.asksaveasfilename(
            title="Save Python File",
            defaultextension=".py",
            filetypes=[("Python files", "*.py"), ("All files", "*.*")]
        )
        if file_path:
            try:
                content = self.code_editor.get('1.0', tk.END + '-1c')
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(content)
                self.current_file = file_path
                self.root.title(f"Voice-Activated Python IDE - {os.path.basename(file_path)}")
                self.add_chat_message("System", f"Saved file as: {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file: {e}")
    
    def run_code(self):
        code = self.code_editor.get('1.0', tk.END + '-1c')
        if not code.strip():
            self.append_to_terminal("No code to run.\n")
            return
        self.append_to_terminal(f"\n{'='*40}\n")
        self.append_to_terminal(f"Running code at {datetime.now().strftime('%H:%M:%S')}\n")
        self.append_to_terminal(f"{'='*40}\n")
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
                temp_file.write(code)
                temp_file_path = temp_file.name
            threading.Thread(target=self._execute_code, args=(temp_file_path,), daemon=True).start()           
        except Exception as e:
            self.append_to_terminal(f"Error creating temporary file: {e}\n")
    def _execute_code(self, file_path):
        try:
            result = subprocess.run(
                [sys.executable, file_path],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.stdout:
                self.append_to_terminal(f"Output:\n{result.stdout}\n")
            if result.stderr:
                self.append_to_terminal(f"Errors:\n{result.stderr}\n")
            self.append_to_terminal(f"Process finished with return code: {result.returncode}\n")
        except subprocess.TimeoutExpired:
            self.append_to_terminal("Execution timed out (30 seconds limit).\n")
        except Exception as e:
            self.append_to_terminal(f"Execution error: {e}\n")
        finally:
            try:
                os.unlink(file_path)
            except:
                pass
    def clear_terminal(self):
        self.terminal.delete('1.0', tk.END)
        self.append_to_terminal("Terminal cleared.\n")

    def append_to_terminal(self, text):
        def _append():
            self.terminal.insert(tk.END, text)
            self.terminal.see(tk.END)
        
        self.root.after(0, _append)
    
    def start_voice_recognition(self):
        if not self.is_listening:
            self.is_listening = True
            self.start_voice_btn.config(state=tk.DISABLED)
            self.stop_voice_btn.config(state=tk.NORMAL)
            self.voice_status_label.config(text="Voice: Listening", foreground="green")

            threading.Thread(target=self.continuous_voice_recognition, daemon=True).start()
            self.voice_status_text.insert(tk.END, "Voice recognition started.\n")
    def stop_voice_recognition(self):
        self.is_listening = False
        self.start_voice_btn.config(state=tk.NORMAL)
        self.stop_voice_btn.config(state=tk.DISABLED)
        self.voice_status_label.config(text="Voice: Off", foreground="red")
        self.voice_status_text.insert(tk.END, "Voice recognition stopped.\n\n")
    
    def continuous_voice_recognition(self):
        while self.is_listening:
            try:
                with self.microphone as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=5)
                
                try:
                    text = self.recognizer.recognize_google(audio).lower()
                    if text:
                        self.voice_queue.put(text)
                        self.root.after(0, lambda: self.voice_status_text.insert(tk.END, f"Heard: {text}\n"))
                        
                except sr.UnknownValueError:
                    pass  
                except sr.RequestError as e:
                    self.root.after(0, lambda: self.voice_status_text.insert(tk.END, f"Recognition error: {e}\n"))
                    
            except sr.WaitTimeoutError:
                pass 
            except Exception as e:
                self.root.after(0, lambda: self.voice_status_text.insert(tk.END, f"Voice error: {e}\n"))
                time.sleep(1)
    
    def process_voice_commands(self):
        while True:
            try:
                if not self.voice_queue.empty():
                    command = self.voice_queue.get()
                    self.root.after(0, lambda cmd=command: self.handle_voice_command(cmd))
                time.sleep(0.1)
            except Exception as e:
                print(f"Voice processing error: {e}")
    
    def handle_voice_command(self, command):
        command = command.lower().strip()
        self.add_chat_message("You", command) 
        code_generation_phrases = [
            "write a program", "write code", "create a program", "generate code",
            "python code", "code for", "make a program", "develop a program",
            "script for", "show me code", "give me a function", "write a function",
            "program to", "how to write", "can you code", "build a script",
            "generate python", "write a script"
        ]

        # File operations
        if "run the file" in command or "execute the code" in command:
            self.run_code()
            self.add_chat_message("System", "Running the code...")
            
        elif "save the file" in command or "save file" in command:
            self.save_file()
            
        elif "open file" in command:
            self.open_file()
            
        elif "new file" in command:
            self.new_file()
            
        elif "clear terminal" in command:
            self.clear_terminal()

        elif any(phrase in command for phrase in code_generation_phrases):
            self.handle_code_generation_request(command)
        else:
            self.process_chat_command(command, is_voice_command=True) 
    
    def handle_code_generation_request(self, command):
        
        if self.gemini_available:
            try:
               
                prompt = f"""You are a Python code generator. The user said: "{command}" """
                response = self.gemini_model.generate_content(prompt)
                raw_code_output = response.text.strip()
                code = raw_code_output
                match = re.search(r"```(?:python)?\s*(.*?)(?:```|$)", raw_code_output, re.DOTALL)
                if match:
                    code = match.group(1).strip()
                else:
                    common_prefixes = ["here is the code:", "here's the code:", "python code:"]
                    for prefix in common_prefixes:
                        if code.lower().startswith(prefix):
                            code = code[len(prefix):].strip()
                self.code_editor.delete('1.0', tk.END)
                self.code_editor.insert('1.0', code)

                self.add_chat_message("Assistant", f"I've generated the code based on your request: '{command}'. The code has been added to the editor.")
                
            except Exception as e:
                self.add_chat_message("Assistant", f"Sorry, I couldn't generate the code using Gemini API. Error: {e}")
        else:
            self.add_chat_message("Assistant", "Gemini API is not configured. Falling back to template generation.")
    
    def process_chat_command(self, command, is_voice_command=False):
        command = command.lower().strip() 
        if not is_voice_command: 
            self.add_chat_message("You", command)

        code_generation_phrases = [
            "write a program", "write code", "create a program", "generate code",
            "python code", "code for", "make a program", "develop a program",
            "script for", "show me code", "give me a function", "write a function",
            "program to", "how to write", "can you code", "build a script",
            "generate python", "write a script"
        ]

        if "run the file" in command or "execute the code" in command:
            self.run_code()
            self.add_chat_message("System", "Running the code...")
            
        elif "save the file" in command or "save file" in command:
            self.save_file()
            
        elif "open file" in command:
            self.open_file()
            
        elif "new file" in command:
            self.new_file()
            
        elif "clear terminal" in command:
            self.clear_terminal()

        elif any(phrase in command for phrase in code_generation_phrases):
            self.handle_code_generation_request(command)
            
        else:

            if self.gemini_available:
                try:
                    prompt = f"""You are a helpful Python programming assistant. The user said: "{command}" ."""
                    response = self.gemini_model.generate_content(prompt)
                    self.add_chat_message("Assistant", response.text)
                except Exception as e:
                    self.add_chat_message("Assistant", f"Sorry, I encountered an error: {e}")
            else:
                responses = {
                    "hello": "Hello! I'm your Python coding assistant. How can I help you today?",
                    "help": "I can help you with Python programming. Try commands like 'write a hello world program' or ask programming questions.",
                    "what can you do": "I can generate Python code, run your programs, save files, and answer programming questions.",
                }
                response = "I'm here to help with Python programming. Ask me to write code or run your programs!"
                for key, value in responses.items():
                    if key in command:
                        response = value
                        break
                self.add_chat_message("Assistant", response)
    def send_chat_message(self, event=None):
        message = self.chat_input.get().strip()
        if message:
            self.chat_input.delete(0, tk.END)
            self.process_chat_command(message)
    
    def add_chat_message(self, sender, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.chat_display.insert(tk.END, f"[{timestamp}] {sender}: {message}\n\n")
        self.chat_display.see(tk.END)
    
    def run(self):
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
    
    def on_closing(self):
        self.is_listening = False
        self.root.quit()
        self.root.destroy()

if __name__ == "__main__":  
    print("Starting Voice-Activated Python IDE...")
    
    try:
        app = VoicePythonIDE()
        app.run()
    except Exception as e:
        print(f"Error starting application: {e}")
        input("Press Enter to exit...")