import tkinter as tk
import time
from tkinter import ttk

def mainapp():
    splash.destroy()
    mainwindow= tk.Tk()
    mainwindow.title("PyVox")
    mainwindow.geometry("1100x800")

    mainwindow.mainloop()

splash = tk.Tk()
splash.title("PyVox")
windowwidth=675
windowheight=672
screenwidth = splash.winfo_screenwidth()
screenheight = splash.winfo_screenheight()
x=int((screenwidth/2) - (windowwidth/2))
y=int((screenheight/2) - (windowheight/2))
splash.geometry(f"{windowwidth}x{windowheight}+{x}+{y}")

splash.overrideredirect(True)
splashframe = ttk.Frame(splash)
splashframe.pack(expand=True, fill=tk.BOTH)

try:
    banner_image = tk.PhotoImage(file="banner.png")
    bannerlabel=tk.Label(splashframe, image=banner_image)
    bannerlabel.pack(expand=True, fill=tk.BOTH)
except: 
    print("Error")
splash.after(4000, mainapp)
splash.mainloop()