import tkinter as tk
import time
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
from PIL import Image, ImageTk
import os
import sys
from io import StringIO
import code
import io

def mainapp():
    splash.destroy()
    mainwindow = tk.Tk()
    mainwindow.title("PyVox")
    mainwindow.geometry("1100x800")
    mainwindow.configure(bg="#070707")

    toolbar = tk.Frame(mainwindow, bg="#070707", bd=0)
    toolbar.pack(side=tk.TOP, fill=tk.X)

    text_area = tk.Text(
        mainwindow,
        bg="#070707",
        fg="white",
        insertbackground="white",
        font=("Courier", 12),
        wrap="word",
        borderwidth=0,
        highlightthickness=0
    )
    text_area.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)

    output_area = tk.Text(
        mainwindow,
        bg="#070707",
        fg="white",
        font=("Courier", 12),
        wrap="word",
        borderwidth=0,
        highlightthickness=0,
        height=8
    )
    output_area.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
    output_area.config(state=tk.DISABLED)
    terminal_frame = tk.Frame(mainwindow, bg="#070707")
    terminal_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

    terminal_area = tk.Text(
        terminal_frame,
        bg="#070707",
        fg="white",
        insertbackground="white",
        font=("Courier", 12),
        wrap="word",
        borderwidth=0,
        highlightthickness=0,
        height=5
    )
    terminal_area.pack(side=tk.TOP, fill=tk.X)
    console_vars = {}  
    console = code.InteractiveConsole(locals=console_vars)
    terminal_area.insert(tk.END, ">>> ")
    terminal_area.config(state=tk.NORMAL)

    def handle_terminal_input(event):
        if event.keysym == "Return":
            terminal_area.config(state=tk.NORMAL)
            lines = terminal_area.get(1.0, tk.END).rstrip().split('\n')
            command = lines[-1].replace(">>> ", "").strip()
            
            if command:
                old_stdout = sys.stdout
                redirected_output = io.StringIO()
                sys.stdout = redirected_output
                try:
                    more = console.push(command)
                    output = redirected_output.getvalue()
                    if output:
                        terminal_area.insert(tk.END, output)
                    if more:
                        terminal_area.insert(tk.END, "... ")
                    else:
                        terminal_area.insert(tk.END, ">>> ")
                except Exception as e:
                    terminal_area.insert(tk.END, f"Error: {str(e)}\n>>> ")
                finally:
                    sys.stdout = old_stdout
                    redirected_output.close()
            return "break"

    terminal_area.bind("<Return>", handle_terminal_input)

    whitearea = tk.Frame(mainwindow, bg="#FAF7F7", width=1100, height=100)
    whitearea.place(x=0, y=800-100)
    whitearea.pack_propagate(False)

    current_file = [None]

    def create_new_file():
        file_path = filedialog.asksaveasfilename(
            defaultextension=".py",
            filetypes=[("Python files", "*.py"), ("All files", "*.*")],
            title="Create New Python File"
        )
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    f.write("# New Python Script\n\n")
                text_area.delete(1.0, tk.END)
                text_area.insert(tk.END, "# New Python Script\n\n")
                current_file[0] = file_path
                messagebox.showinfo("Success", f"New file created at:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create file:\n{e}")

    def save_file():
        if current_file[0]:
            try:
                with open(current_file[0], 'w') as f:
                    f.write(text_area.get(1.0, tk.END).rstrip('\n') + '\n')
                messagebox.showinfo("Success", f"File saved at:\n{current_file[0]}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file:\n{e}")
        else:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".py",
                filetypes=[("Python files", "*.py"), ("All files", "*.*")],
                title="Save Python File"
            )
            if file_path:
                try:
                    with open(file_path, 'w') as f:
                        f.write(text_area.get(1.0, tk.END).rstrip('\n') + '\n')
                    current_file[0] = file_path
                    messagebox.showinfo("Success", f"File saved at:\n{file_path}")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to save file:\n{e}")

    def open_file():
        file_path = filedialog.askopenfilename(
            filetypes=[("Python files", "*.py"), ("All files", "*.*")],
            title="Open Python File"
        )
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                text_area.delete(1.0, tk.END)
                text_area.insert(tk.END, content)
                current_file[0] = file_path
                messagebox.showinfo("Success", f"File opened:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open file:\n{e}")

    def run_code():
        if not current_file[0]:
            messagebox.showwarning("Save Required", "Please save the file before running the code.")
            return
        old_stdout = sys.stdout
        redirected_output = StringIO()
        sys.stdout = redirected_output
        try:
            code_str = text_area.get(1.0, tk.END).rstrip('\n')
            exec(code_str, {})
            output = redirected_output.getvalue()
            if not output:
                output = "Code executed successfully. No output."
        except Exception as e:
            output = f"Error: {str(e)}"
        finally:
            sys.stdout = old_stdout
            redirected_output.close()

        output_window = tk.Toplevel()
        output_window.title("PyVox - Output")
        output_window.geometry("700x400")
        output_window.configure(bg="#070707")

        output_text = tk.Text(
            output_window,
            bg="#070707",
            fg="white",
            font=("Courier", 12),
            wrap="word",
            borderwidth=0,
            highlightthickness=0
        )
        output_text.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
        output_text.insert(tk.END, output)
        output_text.config(state=tk.DISABLED)

    run_button = tk.Button(
        toolbar,
        text="Run",
        command=run_code,
        bg="#2E2E2E",
        fg="white",
        activebackground="#3E3E3E",
        relief="flat",
        padx=10,
        pady=5
    )
    run_button.pack(side=tk.LEFT, padx=5)

    save_button = tk.Button(
        toolbar,
        text="Save",
        command=save_file,
        bg="#2E2E2E",
        fg="white",
        activebackground="#3E3E3E",
        relief="flat",
        padx=10,
        pady=5
    )
    save_button.pack(side=tk.LEFT, padx=5)
    
    open_file_button = tk.Button(
        toolbar,
        text="Open File",
        command=open_file,
        bg="#2E2E2E",
        fg="white",
        activebackground="#3E3E3E",
        relief="flat",
        padx=10,
        pady=5
    )
    open_file_button.pack(side=tk.LEFT, padx=5)
    
    new_file_button = tk.Button(
        toolbar,
        text="New File",
        command=create_new_file,
        bg="#2E2E2E",
        fg="white",
        activebackground="#3E3E3E",
        relief="flat",
        padx=10,
        pady=5
    )
    new_file_button.pack(side=tk.LEFT, padx=5)

    about_button = tk.Button(
        toolbar,
        text="About",
        command=lambda: messagebox.showinfo("About", "PyVox - A simple voice app\nVersion 1.0"),
        bg="#2E2E2E",
        fg="white",
        activebackground="#3E3E3E",
        relief="flat",
        padx=10,
        pady=5
    )
    about_button.pack(side=tk.LEFT, padx=5)

    mic_img = Image.open("mic.png")
    mic_img = mic_img.resize((50, 50), Image.LANCZOS)  
    micimage = ImageTk.PhotoImage(mic_img)
   
    mainwindow.micimage = micimage

    micbutton = tk.Button(
        mainwindow,
        image=micimage,
        command=lambda: messagebox.showinfo("Microphone", "Speak now!"),
        bg="#070707",
        fg="white",
        activebackground="#080808",
        relief="raised",
        padx=5,  
        pady=5   
    )
    micbutton.place(relx=0.5, rely=0.97, anchor=tk.CENTER)



    mainwindow.mainloop()

splash = tk.Tk()
splash.title("PyVox")
windowwidth = 675
windowheight = 672
screenwidth = splash.winfo_screenwidth()
screenheight = splash.winfo_screenheight()
x = int((screenwidth / 2) - (windowwidth / 2))
y = int((screenheight / 2) - (windowheight / 2))
splash.geometry(f"{windowwidth}x{windowheight}+{x}+{y}")

splash.overrideredirect(True)
splashframe = ttk.Frame(splash)
splashframe.pack(expand=True, fill=tk.BOTH)

try:
    img = Image.open("banner.png")
    img = img.resize((windowwidth, windowheight), Image.LANCZOS)
    banner_image = ImageTk.PhotoImage(img)
    splash.banner_image = banner_image
    bannerlabel = tk.Label(splashframe, image=banner_image, borderwidth=0, highlightthickness=0)
    bannerlabel.pack(expand=True, fill=tk.BOTH)
except Exception as e:
    print("Error:", e)

splash.after(4000, mainapp)
splash.mainloop()