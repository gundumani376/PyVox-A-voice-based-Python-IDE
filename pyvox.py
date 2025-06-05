import tkinter as tk
import time
from tkinter import ttk
from tkinter import messagebox
from PIL import Image, ImageTk

def mainapp():
    splash.destroy()
    mainwindow = tk.Tk()
    mainwindow.title("PyVox")
    mainwindow.geometry("1100x800")

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
    micbutton.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

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