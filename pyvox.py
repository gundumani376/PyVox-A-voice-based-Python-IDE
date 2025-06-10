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
    mainWindow.geometry("1100x800")
    mainWindow.configure(bg="#070707")
    toolBar = tk.Frame(mainWindow, bg="#070707", bd=0)
    toolBar.pack(side=tk.TOP, fill=tk.X)
    
    # Main text area with line numbers
    textFrame = tk.Frame(mainWindow, bg="#070707")
    textFrame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)
    lineNumberAreaText = tk.Text(textFrame, bg="#070707", fg="gray", font=("Courier", 12), width=4, wrap="none", borderwidth=0, highlightthickness=0, state=tk.DISABLED)
    lineNumberAreaText.pack(side=tk.LEFT, fill=tk.Y)
    textArea = tk.Text(textFrame, bg="#070707", fg="white", insertbackground="white", font=("Courier", 12), wrap="word", borderwidth=0, highlightthickness=0)
    textArea.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    outputArea = tk.Text(mainWindow, bg="#070707", fg="white", font=("Courier", 12), wrap="word", borderwidth=0, highlightthickness=0, height=8)
    outputArea.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
    outputArea.config(state=tk.DISABLED)
    terminalFrame = tk.Frame(mainWindow, bg="#070707")
    terminalFrame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
    
    # Terminal area with line numbers
    lineNumberAreaTerminal = tk.Text(terminalFrame, bg="#070707", fg="gray", font=("Courier", 12), width=4, wrap="none", borderwidth=0, highlightthickness=0, state=tk.DISABLED)
    lineNumberAreaTerminal.pack(side=tk.LEFT, fill=tk.Y)
    terminalArea = tk.Text(terminalFrame, bg="#070707", fg="white", insertbackground="white", font=("Courier", 12), wrap="word", borderwidth=0, highlightthickness=0, height=5)
    terminalArea.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    consoleVars = {}
    console = code.InteractiveConsole(locals=consoleVars)
    terminalArea.insert(tk.END, ">>> ")
    terminalArea.config(state=tk.NORMAL)

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

    def voiceActivation():
        import pyttsx3
        engine = pyttsx3.init()
        mainModule = importlib.import_module("main")
        while True:
            try:
                wakeWord = mainModule.recognizeSpeech()
                if wakeWord and wakeWord.lower().strip() == "python":
                    engine.say("I'm listening")
                    engine.runAndWait()
                    query = mainModule.recognizeSpeech()
                    if query:
                        queryLower = query.lower().strip()
                        if "run the code" in queryLower:
                            def runCodeWrapper():
                                runCode()
                            mainWindow.after(0, runCodeWrapper)
                            engine.say("Running the code.")
                            engine.runAndWait()
                        elif "open saajan" in queryLower:
                            def openSaajanWrapper():
                                search_path = os.path.expanduser("~")  # Start from home directory
                                filePath = search_file("saajan.py", search_path)
                                if filePath:
                                    try:
                                        with open(filePath, 'r') as f:
                                            content = f.read()
                                        textArea.delete(1.0, tk.END)
                                        textArea.insert(tk.END, content)
                                        currentFile[0] = filePath
                                        engine.say("File saajan.py opened.")
                                    except Exception as e:
                                        engine.say(f"Failed to open file: {str(e)}")
                                else:
                                    engine.say("File saajan.py not found on your computer.")
                            mainWindow.after(0, openSaajanWrapper)
                            engine.runAndWait()
                        elif "open" in queryLower and "file" in queryLower:
                            match = re.search(r'open\s+(.+?)\s+file', queryLower, re.IGNORECASE)
                            if match:
                                fileName = match.group(1).strip()
                                def openFileWrapper():
                                    filePath = fileName if os.path.exists(fileName) else filedialog.askopenfilename(filetypes=[("Python files", "*.py"), ("All files", "*.*")], initialfile=fileName)
                                    if filePath:
                                        try:
                                            with open(filePath, 'r') as f:
                                                content = f.read()
                                            textArea.delete(1.0, tk.END)
                                            textArea.insert(tk.END, content)
                                            currentFile[0] = filePath
                                            engine.say(f"File {fileName} opened.")
                                        except Exception as e:
                                            engine.say(f"Failed to open file: {str(e)}")
                                    else:
                                        engine.say("No file selected.")
                                mainWindow.after(0, openFileWrapper)
                            else:
                                engine.say("Please specify a valid file name.")
                                engine.runAndWait()
                        elif "rewrite line number" in queryLower:
                            match = re.search(r'rewrite line number (\d+)', queryLower, re.IGNORECASE)
                            if match:
                                lineNum = int(match.group(1))
                                # Extract the new content from the query (e.g., "to something else")
                                newContentMatch = re.search(r'to\s+(.+)', queryLower, re.IGNORECASE)
                                newContent = newContentMatch.group(1).strip() if newContentMatch else ""
                                def rewriteLine():
                                    lines = textArea.get(1.0, tk.END).split('\n')
                                    if 1 <= lineNum <= len(lines):
                                        lines[lineNum - 1] = newContent
                                        textArea.delete(1.0, tk.END)
                                        textArea.insert(tk.END, '\n'.join(lines).rstrip('\n'))
                                        updateLineNumbersText()
                                        engine.say(f"Line {lineNum} has been rewritten.")
                                    else:
                                        engine.say(f"Line number {lineNum} is out of range.")
                                mainWindow.after(0, rewriteLine)
                                engine.runAndWait()
                            else:
                                engine.say("Please specify a valid line number.")
                                engine.runAndWait()
                        elif "save the file" in queryLower:
                            def saveFileWrapper():
                                saveFile()
                            mainWindow.after(0, saveFileWrapper)
                            engine.runAndWait()
                        elif "close pyvox" in queryLower:
                            def closeWindow():
                                mainWindow.destroy()
                            mainWindow.after(0, closeWindow)
                            engine.say("Closing PyVox.")
                            engine.runAndWait()
                            break  
                        else:
                            keyWords = ["code", "program", "write", "script", "function", "class", "method", "generate"]
                            if any(word in queryLower for word in keyWords):
                                codeResponse = mainModule.geminiResponse(query)
                                codeBlocks = re.findall(r'```(?:\w*\n)?(.*?)```', codeResponse, re.DOTALL)
                                code = codeBlocks[0].strip() if codeBlocks else codeResponse.strip()
                                def insertCode():
                                    textArea.delete(1.0, tk.END)
                                    textArea.insert(tk.END, code)
                                mainWindow.after(0, insertCode)
                                engine.say("Code has been written in the editor.")
                                engine.runAndWait()
                            else:
                                response = mainModule.geminiResponse(query)
                                def openChatAndRespond():
                                    chatDialog = tk.Toplevel(mainWindow)
                                    chatDialog.title("Chat with Gemini")
                                    chatDialog.geometry("700x500")
                                    chatDialog.configure(bg="#070707")
                                    tk.Label(chatDialog, text="Gemini Chat", bg="#070707", fg="white", font=("Courier", 14)).pack(pady=5)
                                    chatHistory = tk.Text(chatDialog, height=15, bg="white", fg="black", font=("Courier", 12), wrap="word", state=tk.NORMAL)
                                    chatHistory.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
                                    chatHistory.insert(tk.END, f"You: {query}\n")
                                    chatHistory.insert(tk.END, f"Gemini: {response}\n\n")
                                    chatHistory.config(state=tk.DISABLED)
                                mainWindow.after(0, openChatAndRespond)
                                engine.say(response)
                                engine.runAndWait()
            except Exception as e:
                print(f"Voice activation error: {e}")        

    threading.Thread(target=voiceActivation, daemon=True).start()

    def microphoneCommand():
        import pyttsx3
        engine = pyttsx3.init()
        engine.say("Please speak")
        engine.runAndWait()
        try:
            mainModule = importlib.import_module("main")
            if hasattr(mainModule, "recognizeSpeech") and hasattr(mainModule, "geminiResponse"):
                query = mainModule.recognizeSpeech()
                if query:
                    keyWords = ["code", "program", "write", "script", "function", "class", "method", "generate"]
                    if any(word in query.lower() for word in keyWords):
                        codeResponse = mainModule.geminiResponse(query)
                        import re
                        codeBlocks = re.findall(r'```(?:\w*\n)?(.*?)```', codeResponse, re.DOTALL)
                        code = codeBlocks[0].strip() if codeBlocks else codeResponse.strip()
                        if code and code != "No code found":
                            textArea.delete(1.0, tk.END)
                            textArea.insert(tk.END, code)
                            engine.say("Code has been written in the editor.")
                            engine.runAndWait()
                        else:
                            messagebox.showinfo("Info", "No code found in Gemini response.")
                    else:
                        response = mainModule.geminiResponse(query)
                        engine.say(response)
                        engine.runAndWait()
                        messagebox.showinfo("Gemini Response", response)
                else:
                    messagebox.showinfo("Info", "No speech detected.")
            else:
                messagebox.showerror("Error", "main.py does not have the required functions.")
        except Exception as e:
            messagebox.showerror("Error", f"Microphone command failed:\n{e}")

    def chatWithGemini():
        try:
            mainModule = importlib.import_module("main")
            if hasattr(mainModule, "geminiResponse"):
                chatDialog = tk.Toplevel(mainWindow)
                chatDialog.title("Chat with Gemini")
                chatDialog.geometry("700x500")
                chatDialog.configure(bg="#070707")
                tk.Label(chatDialog, text="Gemini Chat", bg="#070707", fg="white", font=("Courier", 14)).pack(pady=5)
                chatHistory = tk.Text(chatDialog, height=20, bg="#2E2E2E", fg="white", font=("Courier", 12), wrap="word", state=tk.DISABLED)
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
    whiteArea = tk.Frame(mainWindow, bg="#FAF7F7", width=1100, height=100)
    whiteArea.place(x=0, y=800-100)
    whiteArea.pack_propagate(False)
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
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create file:\n{e}")

    def saveFile():
        if currentFile[0]:
            try:
                with open(currentFile[0], 'w') as f:
                    f.write(textArea.get(1.0, tk.END).rstrip('\n') + '\n')
                messagebox.showinfo("Success", f"File saved at:\n{currentFile[0]}")
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
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open file:\n{e}")

    def runCode():
        if not currentFile[0]:
            messagebox.showwarning("Save Required", "Please save the file before running the code.")
            return
        oldStdout = sys.stdout
        redirectedOutput = StringIO()
        sys.stdout = redirectedOutput
        try:
            codeStr = textArea.get(1.0, tk.END).rstrip('\n')
            exec(codeStr, {})
            output = redirectedOutput.getvalue()
            if not output:
                output = "Code executed successfully. No output."
        except Exception as e:
            output = f"Error: {str(e)}"
        finally:
            sys.stdout = oldStdout
            redirectedOutput.close()
        outputWindow = tk.Toplevel()
        outputWindow.title("PyVox - Output")
        outputWindow.geometry("700x400")
        outputWindow.configure(bg="#070707")
        outputText = tk.Text(outputWindow, bg="#070707", fg="white", font=("Courier", 12), wrap="word", borderwidth=0, highlightthickness=0)
        outputText.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
        outputText.insert(tk.END, output)
        outputText.config(state=tk.DISABLED)

    runButton = tk.Button(toolBar, text="Run", command=runCode, bg="#2E2E2E", fg="white", activebackground="#3E3E3E", relief="flat", padx=10, pady=5)
    runButton.pack(side=tk.LEFT, padx=5)
    saveButton = tk.Button(toolBar, text="Save", command=saveFile, bg="#2E2E2E", fg="white", activebackground="#3E3E3E", relief="flat", padx=10, pady=5)
    saveButton.pack(side=tk.LEFT, padx=5)
    openFileButton = tk.Button(toolBar, text="Open File", command=openFile, bg="#2E2E2E", fg="white", activebackground="#3E3E3E", relief="flat", padx=10, pady=5)
    openFileButton.pack(side=tk.LEFT, padx=5)
    newFileButton = tk.Button(toolBar, text="New File", command=createNewFile, bg="#2E2E2E", fg="white", activebackground="#3E3E3E", relief="flat", padx=10, pady=5)
    newFileButton.pack(side=tk.LEFT, padx=5)
    chatButton = tk.Button(toolBar, text="Chat", command=chatWithGemini, bg="#2E2E2E", fg="white", activebackground="#3E3E3E", relief="flat", padx=10, pady=5)
    chatButton.pack(side=tk.LEFT, padx=5)
    aboutButton = tk.Button(toolBar, text="About", command=lambda: messagebox.showinfo("About", "PyVox - A simple voice app\nVersion 1.0"), bg="#2E2E2E", fg="white", activebackground="#3E3E3E", relief="flat", padx=10, pady=5)
    aboutButton.pack(side=tk.LEFT, padx=5)
    micImg = Image.open("mic.png")
    micImg = micImg.resize((50, 50))
    micImage = ImageTk.PhotoImage(micImg)
    mainWindow.micImage = micImage
    micButton = tk.Button(mainWindow, image=micImage, command=microphoneCommand, bg="#070707", fg="white", activebackground="#080808", relief="raised", padx=5, pady=5)
    micButton.place(relx=0.5, rely=0.97, anchor=tk.CENTER)
    mainWindow.mainloop()

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
    print("Error:", e)
splash.after(4000, mainApp)
splash.mainloop()