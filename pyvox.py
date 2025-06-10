import tkinter as tk
import time
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import os, sys
import code
from io import StringIO
import io
import importlib
import threading
import re

def mainApp():
    splash.destroy()
    mainWindow = tk.Tk()
    mainWindow.title("PyVox")
    mainWindow.geometry("1200x900")
    mainWindow.configure(bg="#070707")
    
    # Create main container with horizontal panes
    mainContainer = tk.PanedWindow(mainWindow, orient=tk.HORIZONTAL, bg="#070707", sashwidth=5, sashrelief=tk.RAISED)
    mainContainer.pack(fill=tk.BOTH, expand=True)
    
    # Left pane for code editor (75% width)
    leftPane = tk.Frame(mainContainer, bg="#070707")
    mainContainer.add(leftPane, width=900)
    
    # Right pane for chat area (25% width)
    rightPane = tk.Frame(mainContainer, bg="#404040")
    mainContainer.add(rightPane, width=300)
    
    # Tool bar in left pane
    toolBar = tk.Frame(leftPane, bg="#070707", bd=0)
    toolBar.pack(side=tk.TOP, fill=tk.X)
    
    # Main text area with line numbers in left pane
    textFrame = tk.Frame(leftPane, bg="#070707")
    textFrame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)
    lineNumberAreaText = tk.Text(textFrame, bg="#070707", fg="gray", font=("Courier", 12), width=4, wrap="none", borderwidth=0, highlightthickness=0, state=tk.DISABLED)
    lineNumberAreaText.pack(side=tk.LEFT, fill=tk.Y)
    textArea = tk.Text(textFrame, bg="#070707", fg="white", insertbackground="white", font=("Courier", 12), wrap="word", borderwidth=0, highlightthickness=0)
    textArea.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    # Output area in left pane
    outputFrame = tk.Frame(leftPane, bg="#070707")
    outputFrame.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)
    outputLabel = tk.Label(outputFrame, text="Output:", bg="#070707", fg="white", font=("Courier", 10, "bold"), anchor="w")
    outputLabel.pack(side=tk.TOP, fill=tk.X)
    outputArea = tk.Text(outputFrame, bg="#1a1a1a", fg="#00ff00", font=("Courier", 10), wrap="word", borderwidth=1, highlightthickness=0, height=8)
    outputArea.pack(side=tk.TOP, fill=tk.X)
    outputArea.config(state=tk.DISABLED)
    
    # Terminal area in left pane
    terminalFrame = tk.Frame(leftPane, bg="#070707")
    terminalFrame.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)
    terminalLabel = tk.Label(terminalFrame, text="Python Console:", bg="#070707", fg="white", font=("Courier", 10, "bold"), anchor="w")
    terminalLabel.pack(side=tk.TOP, fill=tk.X)
    terminalSubFrame = tk.Frame(terminalFrame, bg="#070707")
    terminalSubFrame.pack(side=tk.TOP, fill=tk.X)
    lineNumberAreaTerminal = tk.Text(terminalSubFrame, bg="#070707", fg="gray", font=("Courier", 10), width=4, wrap="none", borderwidth=0, highlightthickness=0, state=tk.DISABLED)
    lineNumberAreaTerminal.pack(side=tk.LEFT, fill=tk.Y)
    terminalArea = tk.Text(terminalSubFrame, bg="#0d1117", fg="white", insertbackground="white", font=("Courier", 10), wrap="word", borderwidth=1, highlightthickness=0, height=4)
    terminalArea.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    consoleVars = {}
    console = code.InteractiveConsole(locals=consoleVars)
    terminalArea.insert(tk.END, ">>> ")
    terminalArea.config(state=tk.NORMAL)
    
    # Chat area in right pane (grey colored)
    chatLabel = tk.Label(rightPane, text="AI Chat & Voice Commands", bg="#404040", fg="white", font=("Courier", 12, "bold"))
    chatLabel.pack(side=tk.TOP, fill=tk.X, pady=5)
    
    # Status indicator for voice activation
    statusFrame = tk.Frame(rightPane, bg="#404040")
    statusFrame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=2)
    voiceStatusLabel = tk.Label(statusFrame, text="🎤 Voice: Listening", bg="#404040", fg="#00ff00", font=("Courier", 9))
    voiceStatusLabel.pack(side=tk.LEFT)
    
    chatFrame = tk.Frame(rightPane, bg="#404040")
    chatFrame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    # Chat display area
    chatDisplayFrame = tk.Frame(chatFrame, bg="#404040")
    chatDisplayFrame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
    chatScrollbar = tk.Scrollbar(chatDisplayFrame, orient=tk.VERTICAL)
    chatScrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    chatDisplay = tk.Text(chatDisplayFrame, bg="#2d2d2d", fg="white", font=("Courier", 10), wrap="word", borderwidth=1, highlightthickness=0, yscrollcommand=chatScrollbar.set, state=tk.DISABLED)
    chatDisplay.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    chatScrollbar.config(command=chatDisplay.yview)
    
    # Chat input area
    chatInputFrame = tk.Frame(chatFrame, bg="#404040")
    chatInputFrame.pack(side=tk.BOTTOM, fill=tk.X, pady=5)
    chatInputLabel = tk.Label(chatInputFrame, text="Type command:", bg="#404040", fg="white", font=("Courier", 9))
    chatInputLabel.pack(side=tk.TOP, anchor="w")
    chatInput = tk.Entry(chatInputFrame, bg="#2d2d2d", fg="white", insertbackground="white", font=("Courier", 10))
    chatInput.pack(side=tk.TOP, fill=tk.X, pady=2)
    
    # Add initial message to chat
    def addChatMessage(sender, message, color="#white"):
        chatDisplay.config(state=tk.NORMAL)
        chatDisplay.insert(tk.END, f"{sender}: {message}\n", (sender.lower(),))
        chatDisplay.tag_config("system", foreground="#ffff00")
        chatDisplay.tag_config("user", foreground="#00ffff")
        chatDisplay.tag_config("ai", foreground="#ff9900")
        chatDisplay.tag_config("voice", foreground="#00ff00")
        chatDisplay.config(state=tk.DISABLED)
        chatDisplay.see(tk.END)
    
    addChatMessage("System", "PyVox initialized. Say 'python' to activate voice commands.", "#ffff00")

    def updateLineNumbersText(event=None):
        lineNumberAreaText.config(state=tk.NORMAL)
        lineNumberAreaText.delete(1.0, tk.END)
        lineCount = len(textArea.get(1.0, tk.END).split('\n'))
        for i in range(1, lineCount + 1):
            lineNumberAreaText.insert(tk.END, f"{i}\n")
        lineNumberAreaText.config(state=tk.DISABLED)
        lineNumberAreaText.yview_moveto(textArea.yview()[0])

    def updateLineNumbersTerminal(event=None):
        lineNumberAreaTerminal.config(state=tk.NORMAL)
        lineNumberAreaTerminal.delete(1.0, tk.END)
        lineCount = len(terminalArea.get(1.0, tk.END).split('\n'))
        for i in range(1, lineCount + 1):
            lineNumberAreaTerminal.insert(tk.END, f"{i}\n")
        lineNumberAreaTerminal.config(state=tk.DISABLED)
        lineNumberAreaTerminal.yview_moveto(terminalArea.yview()[0])

    def syncScrollText(*args):
        lineNumberAreaText.yview_moveto(textArea.yview()[0])

    def syncScrollTerminal(*args):
        lineNumberAreaTerminal.yview_moveto(terminalArea.yview()[0])

    textArea.bind("<<Modified>>", updateLineNumbersText)
    textArea.bind("<MouseWheel>", syncScrollText)
    textArea.bind("<Button-4>", syncScrollText)
    textArea.bind("<Button-5>", syncScrollText)
    terminalArea.bind("<<Modified>>", updateLineNumbersTerminal)
    terminalArea.bind("<MouseWheel>", syncScrollTerminal)
    terminalArea.bind("<Button-4>", syncScrollTerminal)
    terminalArea.bind("<Button-5>", syncScrollTerminal)
    updateLineNumbersText()
    updateLineNumbersTerminal()

    def search_file(filename, search_path):
        for root, _, files in os.walk(search_path):
            if filename in files:
                return os.path.join(root, filename)
        return None

    def displayOutput(output_text):
        """Display output in the output area"""
        outputArea.config(state=tk.NORMAL)
        outputArea.delete(1.0, tk.END)
        outputArea.insert(tk.END, output_text)
        outputArea.config(state=tk.DISABLED)

    def processCommand(query, fromVoice=False):
        queryLower = query.lower().strip()
        feedback = ""
        
        # Add command to chat
        sender = "Voice" if fromVoice else "User"
        addChatMessage(sender, query)
        
        if "run the code" in queryLower or "execute code" in queryLower:
            runCode()
            feedback = "Running the code."
        elif "open saajan" in queryLower:
            search_path = os.path.expanduser("~")
            filePath = search_file("saajan.py", search_path)
            if filePath:
                try:
                    with open(filePath, 'r') as f:
                        content = f.read()
                    textArea.delete(1.0, tk.END)
                    textArea.insert(tk.END, content)
                    currentFile[0] = filePath
                    feedback = "File saajan.py opened."
                except Exception as e:
                    feedback = f"Failed to open file: {str(e)}"
            else:
                feedback = "File saajan.py not found on your computer."
        elif "open" in queryLower and "file" in queryLower:
            match = re.search(r'open\s+(.+?)\s+file', queryLower, re.IGNORECASE)
            if match:
                fileName = match.group(1).strip()
                filePath = fileName if os.path.exists(fileName) else filedialog.askopenfilename(filetypes=[("Python files", "*.py"), ("All files", "*.*")], initialfile=fileName)
                if filePath:
                    try:
                        with open(filePath, 'r') as f:
                            content = f.read()
                        textArea.delete(1.0, tk.END)
                        textArea.insert(tk.END, content)
                        currentFile[0] = filePath
                        feedback = f"File {fileName} opened."
                    except Exception as e:
                        feedback = f"Failed to open file: {str(e)}"
                else:
                    feedback = "No file selected."
            else:
                feedback = "Please specify a valid file name."
        elif "rewrite line number" in queryLower:
            match = re.search(r'rewrite line number (\d+)', queryLower, re.IGNORECASE)
            if match:
                lineNum = int(match.group(1))
                newContentMatch = re.search(r'to\s+(.+)', queryLower, re.IGNORECASE)
                newContent = newContentMatch.group(1).strip() if newContentMatch else ""
                lines = textArea.get(1.0, tk.END).split('\n')
                if 1 <= lineNum <= len(lines):
                    lines[lineNum - 1] = newContent
                    textArea.delete(1.0, tk.END)
                    textArea.insert(tk.END, '\n'.join(lines).rstrip('\n'))
                    updateLineNumbersText()
                    feedback = f"Line {lineNum} has been rewritten."
                else:
                    feedback = f"Line number {lineNum} is out of range."
            else:
                feedback = "Please specify a valid line number."
        elif "save the file" in queryLower:
            if saveFile():
                feedback = "File saved successfully."
            else:
                feedback = "Failed to save file."
        elif "clear code" in queryLower or "clear editor" in queryLower:
            textArea.delete(1.0, tk.END)
            feedback = "Code editor cleared."
        elif "close pyvox" in queryLower:
            mainWindow.destroy()
            feedback = "Closing PyVox."
        else:
            # Check for code-related keywords
            keyWords = ["code", "program", "write", "script", "function", "class", "method", "generate", "create"]
            try:
                mainModule = importlib.import_module("main")
                if any(word in queryLower for word in keyWords):
                    # Generate code and display in editor
                    if hasattr(mainModule, "geminiResponse"):
                        codeResponse = mainModule.geminiResponse(query)
                        codeBlocks = re.findall(r'```(?:\w*\n)?(.*?)```', codeResponse, re.DOTALL)
                        if codeBlocks:
                            code = codeBlocks[0].strip()
                            textArea.delete(1.0, tk.END)
                            textArea.insert(tk.END, code)
                            feedback = "Code has been generated and added to the editor."
                            displayOutput("Code generated successfully. Click 'Run' to execute.")
                        else:
                            # If no code blocks, treat as regular response
                            textArea.delete(1.0, tk.END)
                            textArea.insert(tk.END, codeResponse.strip())
                            feedback = "Response has been written in the editor."
                    else:
                        feedback = "Code generation not available. Please check main.py file."
                else:
                    # Regular chat response
                    if hasattr(mainModule, "geminiResponse"):
                        response = mainModule.geminiResponse(query)
                        feedback = response
                    else:
                        feedback = "AI response not available. Please check main.py file."
            except ImportError:
                feedback = "main.py module not found. Please ensure it exists and contains geminiResponse function."
            except Exception as e:
                feedback = f"Error processing command: {str(e)}"
        
        # Add AI response to chat
        addChatMessage("AI", feedback)
        return feedback

    def voiceActivation():
        try:
            import pyttsx3
            engine = pyttsx3.init()
            # Set voice properties
            voices = engine.getProperty('voices')
            if voices:
                engine.setProperty('voice', voices[0].id)  # Use first available voice
            engine.setProperty('rate', 150)  # Adjust speech rate
        except ImportError:
            print("pyttsx3 not available. Voice feedback disabled.")
            engine = None
        
        mainModule = None
        try:
            mainModule = importlib.import_module("main")
            if not hasattr(mainModule, "recognizeSpeech"):
                print("main.py does not have recognizeSpeech function")
                mainModule = None
        except ImportError:
            print("main.py module not found for voice recognition")
        
        while True:
            try:
                if mainModule and hasattr(mainModule, "recognizeSpeech"):
                    # Update status
                    mainWindow.after(0, lambda: voiceStatusLabel.config(text="🎤 Voice: Listening", fg="#00ff00"))
                    
                    wakeWord = mainModule.recognizeSpeech()
                    if wakeWord and wakeWord.lower().strip() == "python":
                        # Update status
                        mainWindow.after(0, lambda: voiceStatusLabel.config(text="🎤 Voice: Activated", fg="#ffff00"))
                        
                        if engine:
                            engine.say("I'm listening")
                            engine.runAndWait()
                        
                        query = mainModule.recognizeSpeech()
                        if query:
                            def processVoiceCommand():
                                feedback = processCommand(query, fromVoice=True)
                                if feedback and "close pyvox" not in query.lower():
                                    if engine:
                                        engine.say(feedback)
                                        engine.runAndWait()
                                # Reset status
                                voiceStatusLabel.config(text="🎤 Voice: Listening", fg="#00ff00")
                            
                            mainWindow.after(0, processVoiceCommand)
                else:
                    time.sleep(1)  # Wait before retrying if module not available
            except Exception as e:
                print(f"Voice activation error: {e}")
                time.sleep(1)

    # Start voice activation in background thread
    voiceThread = threading.Thread(target=voiceActivation, daemon=True)
    voiceThread.start()

    def handleChatInput(event):
        command = chatInput.get().strip()
        if command:
            chatInput.delete(0, tk.END)
            feedback = processCommand(command, fromVoice=False)
        return "break"

    chatInput.bind("<Return>", handleChatInput)

    def chatWithGemini():
        try:
            mainModule = importlib.import_module("main")
            if hasattr(mainModule, "geminiResponse"):
                chatDialog = tk.Toplevel(mainWindow)
                chatDialog.title("Extended Chat with Gemini")
                chatDialog.geometry("800x600")
                chatDialog.configure(bg="#070707")
                tk.Label(chatDialog, text="Gemini Extended Chat", bg="#070707", fg="white", font=("Courier", 14)).pack(pady=5)
                chatHistory = tk.Text(chatDialog, height=25, bg="#2E2E2E", fg="white", font=("Courier", 11), wrap="word", state=tk.DISABLED)
                chatHistory.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
                inputFrame = tk.Frame(chatDialog, bg="#070707")
                inputFrame.pack(fill=tk.X, padx=10, pady=10)
                userInput = tk.Entry(inputFrame, font=("Courier", 12), bg="#2E2E2E", fg="white", insertbackground="white")
                userInput.pack(side=tk.LEFT, fill=tk.X, expand=True)
                
                def submitQuery(event=None):
                    query = userInput.get().strip()
                    if query:
                        chatHistory.config(state=tk.NORMAL)
                        chatHistory.insert(tk.END, f"You: {query}\n")
                        chatHistory.config(state=tk.DISABLED)
                        chatHistory.see(tk.END)
                        userInput.delete(0, tk.END)
                        response = mainModule.geminiResponse(query)
                        if response:
                            chatHistory.config(state=tk.NORMAL)
                            chatHistory.insert(tk.END, f"Gemini: {response}\n\n")
                            chatHistory.config(state=tk.DISABLED)
                            chatHistory.see(tk.END)
                        else:
                            chatHistory.config(state=tk.NORMAL)
                            chatHistory.insert(tk.END, "Gemini: No response.\n\n")
                            chatHistory.config(state=tk.DISABLED)
                            chatHistory.see(tk.END)
                    return "break"
                
                sendButton = tk.Button(inputFrame, text="Send", command=submitQuery, bg="#2E2E2E", fg="white", activebackground="#3E3E3E", relief="flat", padx=10, pady=5)
                sendButton.pack(side=tk.RIGHT, padx=5)
                userInput.bind("<Return>", submitQuery)
            else:
                messagebox.showerror("Error", "main.py does not have the geminiResponse function.")
        except Exception as e:
            messagebox.showerror("Error", f"Chat failed:\n{e}")

    def handleTerminalInput(event):
        if event.keysym == "Return":
            terminalArea.config(state=tk.NORMAL)
            content = terminalArea.get(1.0, tk.END).rstrip().split('\n')
            lastPromptIndex = -1
            for i in range(len(content)-1, -1, -1):
                if content[i].startswith(">>> ") or content[i].startswith("... "):
                    lastPromptIndex = i
                    break
            if lastPromptIndex == -1:
                lastPromptIndex = 0
            commandLines = content[lastPromptIndex:]
            command = "\n".join(line.replace(">>> ", "").replace("... ", "") for line in commandLines if line.strip()).strip()
            if command:
                oldStdout = sys.stdout
                redirectedOutput = io.StringIO()
                sys.stdout = redirectedOutput
                try:
                    more = console.push(command)
                    output = redirectedOutput.getvalue()
                    if output:
                        terminalArea.insert(tk.END, output)
                    if more:
                        terminalArea.insert(tk.END, "... ")
                    else:
                        terminalArea.insert(tk.END, "\n>>> ")
                    updateLineNumbersTerminal()
                except Exception as e:
                    terminalArea.insert(tk.END, f"Error: {str(e)}\n>>> ")
                    updateLineNumbersTerminal()
                finally:
                    sys.stdout = oldStdout
                    redirectedOutput.close()
            else:
                terminalArea.insert(tk.END, "\n>>> ")
                updateLineNumbersTerminal()
            terminalArea.see(tk.END)
            return "break"

    terminalArea.bind("<Return>", handleTerminalInput)
    currentFile = [None]

    def createNewFile():
        filePath = filedialog.asksaveasfilename(defaultextension=".py", filetypes=[("Python files", "*.py"), ("All files", "*.*")], title="Create New Python File")
        if filePath:
            try:
                with open(filePath, 'w') as f:
                    f.write("# New Python Script\n\n")
                textArea.delete(1.0, tk.END)
                textArea.insert(tk.END, "# New Python Script\n\n")
                currentFile[0] = filePath
                messagebox.showinfo("Success", f"New file created at:\n{filePath}")
                addChatMessage("System", f"New file created: {os.path.basename(filePath)}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create file:\n{e}")

    def saveFile():
        if currentFile[0]:
            try:
                with open(currentFile[0], 'w') as f:
                    f.write(textArea.get(1.0, tk.END).rstrip('\n') + '\n')
                messagebox.showinfo("Success", f"File saved at:\n{currentFile[0]}")
                addChatMessage("System", f"File saved: {os.path.basename(currentFile[0])}")
                return True
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file:\n{e}")
                return False
        else:
            filePath = filedialog.asksaveasfilename(defaultextension=".py", filetypes=[("Python files", "*.py"), ("All files", "*.*")], title="Save Python File")
            if filePath:
                try:
                    with open(filePath, 'w') as f:
                        f.write(textArea.get(1.0, tk.END).rstrip('\n') + '\n')
                    currentFile[0] = filePath
                    messagebox.showinfo("Success", f"File saved at:\n{filePath}")
                    addChatMessage("System", f"File saved: {os.path.basename(filePath)}")
                    return True
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to save file:\n{e}")
                    return False
        return False

    def openFile():
        filePath = filedialog.askopenfilename(filetypes=[("Python files", "*.py"), ("All files", "*.*")], title="Open Python File")
        if filePath:
            try:
                with open(filePath, 'r') as f:
                    content = f.read()
                textArea.delete(1.0, tk.END)
                textArea.insert(tk.END, content)
                currentFile[0] = filePath
                messagebox.showinfo("Success", f"File opened:\n{filePath}")
                addChatMessage("System", f"File opened: {os.path.basename(filePath)}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open file:\n{e}")

    def runCode():
        oldStdout = sys.stdout
        redirectedOutput = StringIO()
        sys.stdout = redirectedOutput
        try:
            codeStr = textArea.get(1.0, tk.END).rstrip('\n')
            if not codeStr.strip():
                output = "No code to execute."
            else:
                exec(codeStr, {})
                output = redirectedOutput.getvalue()
                if not output:
                    output = "Code executed successfully. No output produced."
        except Exception as e:
            output = f"Error: {str(e)}"
        finally:
            sys.stdout = oldStdout
            redirectedOutput.close()
        
        # Display output in the output area
        displayOutput(output)
        addChatMessage("System", "Code executed. Check output area below.")

    # Toolbar buttons
    runButton = tk.Button(toolBar, text="▶ Run", command=runCode, bg="#2E2E2E", fg="white", activebackground="#3E3E3E", relief="flat", padx=15, pady=8, font=("Courier", 10, "bold"))
    runButton.pack(side=tk.LEFT, padx=2)
    saveButton = tk.Button(toolBar, text="💾 Save", command=saveFile, bg="#2E2E2E", fg="white", activebackground="#3E3E3E", relief="flat", padx=15, pady=8, font=("Courier", 10))
    saveButton.pack(side=tk.LEFT, padx=2)
    openFileButton = tk.Button(toolBar, text="📁 Open", command=openFile, bg="#2E2E2E", fg="white", activebackground="#3E3E3E", relief="flat", padx=15, pady=8, font=("Courier", 10))
    openFileButton.pack(side=tk.LEFT, padx=2)
    newFileButton = tk.Button(toolBar, text="📄 New", command=createNewFile, bg="#2E2E2E", fg="white", activebackground="#3E3E3E", relief="flat", padx=15, pady=8, font=("Courier", 10))
    newFileButton.pack(side=tk.LEFT, padx=2)
    chatButton = tk.Button(toolBar, text="💬 Extended Chat", command=chatWithGemini, bg="#2E2E2E", fg="white", activebackground="#3E3E3E", relief="flat", padx=15, pady=8, font=("Courier", 10))
    chatButton.pack(side=tk.LEFT, padx=2)
    aboutButton = tk.Button(toolBar, text="ℹ About", command=lambda: messagebox.showinfo("About", "PyVox - AI-Powered Voice Code Editor\nVersion 2.0\n\nFeatures:\n• Voice activation with 'python' keyword\n• AI code generation\n• Integrated chat interface\n• Python console\n• Real-time output display"), bg="#2E2E2E", fg="white", activebackground="#3E3E3E", relief="flat", padx=15, pady=8, font=("Courier", 10))
    aboutButton.pack(side=tk.RIGHT, padx=2)
    
    mainWindow.mainloop()

# Splash screen
splash = tk.Tk()
splash.title("PyVox")
windowWidth = 675
windowHeight = 672
screenWidth = splash.winfo_screenwidth()
screenHeight = splash.winfo_screenheight()
x = int((screenWidth/2) - (windowWidth/2))
y = int((screenHeight/2) - (windowHeight/2))
splash.geometry(f"{windowWidth}x{windowHeight}+{x}+{y}")
splash.overrideredirect(True)
splashFrame = ttk.Frame(splash)
splashFrame.pack(expand=True, fill=tk.BOTH)

try:
    img = Image.open("banner.png")
    img = img.resize((windowWidth, windowHeight))
    bannerImage = ImageTk.PhotoImage(img)
    splash.bannerImage = bannerImage
    bannerLabel = tk.Label(splashFrame, image=bannerImage)
    bannerLabel.pack(expand=True)
except Exception as e:
    # Create a simple text splash if banner image not found
    splashLabel = tk.Label(splashFrame, text="PyVox\nAI-Powered Voice Code Editor\n\nLoading...", 
                          font=("Courier", 20, "bold"), bg="#070707", fg="white")
    splashLabel.pack(expand=True)
    splash.configure(bg="#070707")

splash.after(4000, mainApp)
splash.mainloop()