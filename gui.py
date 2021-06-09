################
#  kymera gui  #
################

import os
import tkinter as tk
from sys import platform

from PIL import Image, ImageTk



# utils
def check_path(path):
    if path.strip() == "":
        return False
    return os.path.exists(path)

class KymeraGui:
    def __init__(self):
        # https://stackoverflow.com/a/23840010/4943299
        self.window = tk.Tk()
        self.window.title("Kymera GUI")
        if "nix" in platform:
            self.window.attributes("-zoomed", True)
        else:
            self.window.state("zoomed")
        
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        
        self.viewer = tk.Frame(master=self.window, width=int((screen_width * .66)), height=screen_height, bg="yellow")
        self.viewer.pack(fill=tk.BOTH, side=tk.LEFT)
        
        self.input_directory = tk.Entry(master=self.viewer)
        self.input_directory.config(font=("Consolas", 16))
        self.input_directory.insert(0, "path/to/pdf/directory")
        self.input_directory.place(x=10, y=10, width=int(((screen_width * .66) - 20)))
        
        gallery_max_width = int(((screen_width * .33) - 20))
        gallery_max_height = int(((screen_height * .75) - 50))
        
        img_path = "resources/banner.png"
        image = Image.open(img_path)
        image_new_height = int((gallery_max_width / image.width) * image.height)
        image = image.resize((gallery_max_width, image_new_height), Image.LANCZOS)
        image = ImageTk.PhotoImage(image)
        self.gallery = tk.Label(master=self.viewer, image=image, anchor=tk.CENTER)
        self.gallery.image = image
        self.gallery.place(x=10, y=50, width=gallery_max_width, height=gallery_max_height)
        
        self.input_ocr_data = tk.Text(master=self.viewer)
        self.input_ocr_data.config(font=("Consolas", 12))
        # self.input_ocr_data.insert(0, "Lorem ipsum")
        self.input_ocr_data.place(x=int(gallery_max_width + 30), y=50, width=int((gallery_max_width)), height=gallery_max_height)
        
        self.button_previous = tk.Button(text="Previous", command=view_previous)
        self.button_previous.place(x=10, y=int((gallery_max_height + 60)), width=100)
        
        self.button_next = tk.Button(text="Next", command=view_previous)
        self.button_next.place(x=int((gallery_max_width - 90)), y=int((gallery_max_height + 60)), width=100)
        
        self.editor = tk.Frame(master=self.window, width=int((screen_width * .33)), height=screen_height, bg="blue")
        self.editor.pack(fill=tk.BOTH, side=tk.LEFT)
        
        self.input_answerkey = tk.Entry(master=self.editor)
        self.input_answerkey.config(font=("Consolas", 16))
        self.input_answerkey.insert(0, "path/to/answerkey.csv")
        self.input_answerkey.place(x=10, y=10, width=int(((screen_width * .33) - 20)))
        
        self.input_answerkey_data = tk.Text(master=self.editor)
        self.input_answerkey_data.config(font=("Consolas", 12))
        # self.input_answerkey_data.insert(0, "Lorem ipsum")
        self.input_answerkey_data.place(x=10, y=50, width=gallery_max_width, height=int(((screen_height) - 110)))

def reload(window):
    valid = True
    directory = window.input_directory.get().strip()
    if not check_path(directory):
        window.input_directory.delete(0, tk.END)
        window.input_directory.insert(0, "path/to/pdf/directory")
        valid = False
    
    answerkey = window.input_answerkey.get().strip()
    if not check_path(answerkey):
        window.input_answerkey.delete(0, tk.END)
        window.input_answerkey.insert(0, "path/to/answerkey.csv")
        valid = False
        
    if valid:
        state = Arkivist(f"{directory}/logs.json")

def view_previous():
    print("Hello, world!")

if __name__ == "__main__":
    root = KymeraGui()
    window = root.window
    window.bind('<Return>', (lambda x: reload(root)))
    window.tk.mainloop()