################
#  kymera gui  #
################

import os
import subprocess
import tkinter as tk
from tkinter import ttk
from time import sleep
from sys import platform

from arkivist import Arkivist
from PIL import Image, ImageTk

VERSION = "1.0.0"


# utils
def check_path(path):
    if path.strip() == "":
        return False
    return os.path.exists(path)

class KymeraGui:
    def __init__(self):
        # https:/stackoverflow.com/a/23840010/4943299
        self.window = tk.Tk()
        self.window.title("Kymera GUI")
        if "nix" in platform:
            self.window.attributes("-zoomed", True)
        else:
            self.window.state("zoomed")
        
        self.screen_width = self.window.winfo_screenwidth()
        self.screen_height = self.window.winfo_screenheight()
        
        self.viewer = tk.Frame(master=self.window, width=int((self.screen_width * .66)), height=self.screen_height, bg="yellow")
        self.viewer.pack(fill=tk.BOTH, side=tk.LEFT)
        
        self.input_directory = tk.Entry(master=self.viewer)
        self.input_directory.config(font=("Consolas", 16))
        self.input_directory.insert(0, "path/to/pdf/directory")
        self.input_directory.place(x=10, y=10, width=int(((self.screen_width * .66) - 20)))
        
        self.gallery_max_width = int(((self.screen_width * .33) - 20))
        self.gallery_max_height = int(((self.screen_height * .75) - 50))
        
        image = image_loader("resources/banner.png", self.gallery_max_width)
        self.gallery = tk.Label(master=self.viewer, image=image, anchor=tk.CENTER)
        self.gallery.image = image
        self.gallery.place(x=10, y=50, width=self.gallery_max_width, height=int(((self.screen_height) - 150)))
        
        self.button_previous = tk.Button(text="Previous")
        self.button_previous.place(x=10, y=int((self.screen_height - 90)), width=100)
        
        self.button_next = tk.Button(text="Next")
        self.button_next.place(x=int((self.gallery_max_width - 90)), y=int((self.screen_height - 90)), width=100)
        
        self.input_ocr_data = tk.Text(master=self.viewer)
        self.input_ocr_data.config(font=("Consolas", 12), state=tk.DISABLED)
        # self.input_ocr_data.insert(0, "Lorem ipsum")
        self.input_ocr_data.place(x=int(self.gallery_max_width + 30), y=50, width=int((self.gallery_max_width)), height=self.gallery_max_height)
        
        self.label_file = tk.Label(master=self.viewer, text="File:", anchor="w")
        self.label_file.config(font=("Consolas", 10))
        self.label_file.place(x=int(self.gallery_max_width + 30), y=int((self.gallery_max_height + 55)), width=self.gallery_max_width)
        
        self.label_grade = tk.Label(master=self.viewer, text="Grade:")
        self.label_grade.config(font=("Consolas", 20))
        self.label_grade.place(x=int((self.gallery_max_width + 30)), y=int((self.screen_height - 140)), width=120)
        
        self.input_grade = tk.Entry(master=self.viewer)
        self.input_grade.config(font=("Consolas", 20), state=tk.DISABLED)
        self.input_grade.insert(0, "0")
        self.input_grade.place(x=int((self.gallery_max_width + 170)), y=int((self.screen_height - 140)), width=int((self.gallery_max_width - 140)))
        
        self.locked = tk.IntVar()
        self.check_locked = tk.Checkbutton(master=self.viewer, text="Skip during analysis", var=self.locked, anchor="w")
        self.check_locked.config(state=tk.DISABLED)
        self.check_locked.place(x=int((self.gallery_max_width + 30)), y=int((self.screen_height - 90)), width=self.gallery_max_width)
        self.locked.set(0)
        
        self.editor = tk.Frame(master=self.window, width=int((self.screen_width - (self.screen_width* .66))), height=self.screen_height, bg="blue")
        self.editor.pack(fill=tk.BOTH, side=tk.LEFT)
        
        self.input_answerkey = tk.Entry(master=self.editor)
        self.input_answerkey.config(font=("Consolas", 16))
        self.input_answerkey.insert(0, "path/to/answerkey.csv")
        self.input_answerkey.place(x=10, y=10, width=int(((self.screen_width * .33) - 10)))
        
        self.input_answerkey_data = tk.Text(master=self.editor)
        self.input_answerkey_data.config(font=("Consolas", 12), state=tk.DISABLED)
        # self.input_answerkey_data.insert(0, "Lorem ipsum")
        self.input_answerkey_data.place(x=10, y=50, width=int(((self.screen_width * .33) - 10)), height=int(((self.screen_height) - 110)))
        
        self.process = None

def image_loader(path, gallery_max_width):
    image = Image.open(path)
    image_new_height = int((gallery_max_width / image.width) * image.height)
    image = image.resize((gallery_max_width, image_new_height), Image.LANCZOS)
    return ImageTk.PhotoImage(image)

def validate(value, minimum, maximum, fallback):
    if not isinstance(value, int):
        print("KymeraWarning: Parameter must be an integer.")
        value = int(fallback)
    if not (minimum <= value <= maximum):
        print(f"KymeraWarning: Parameter must be an integer between {minimum}-{maximum}.")
        value = int(fallback)
    return value

def reload(window):
    if window.process is not None:
        if window.process.poll() is not None:
            window.process = None
        return
    
    valid = True
    directory = window.input_directory.get().strip()
    analysis = Arkivist(f"{directory}/kymera/analysis.json")
    if not check_path(directory):
        window.input_directory.delete(0, tk.END)
        window.input_directory.insert(0, "path/to/pdf/directory")
        
        
        image = image_loader("resources/banner.png", window.gallery_max_width)
        window.gallery.configure(image=image)
        window.gallery.image = image
        
        window.button_previous.config(state=tk.DISABLED)
        window.button_next.config(state=tk.DISABLED)
        window.input_grade.delete(0, tk.END)
        window.input_grade.insert(0, "0")
        window.input_grade.config(state=tk.DISABLED)
        window.check_locked.config(state=tk.DISABLED)
        window.input_ocr_data.delete("1.0", tk.END)
        window.input_ocr_data.config(state=tk.DISABLED)
        valid = False
    else:
        if analysis.is_empty():
            valid = False
            window.button_previous.config(state=tk.DISABLED)
            window.button_next.config(state=tk.DISABLED)
            window.label_file["text"] = "File:"
            window.input_grade.delete(0, tk.END)
            window.input_grade.insert(0, "0")
            window.input_grade.config(state=tk.DISABLED)
            window.check_locked.config(state=tk.DISABLED)
            window.input_ocr_data.delete("1.0", tk.END)
            window.input_ocr_data.config(state=tk.DISABLED)
            window.locked.set(0)
            if window.process is None:
                image = image_loader("resources/banner.png", window.gallery_max_width)
                window.gallery.configure(image=image)
                window.gallery.image = image
                window.process = subprocess.Popen(["py", "kymera.py", "-d", directory, "-z", "1", "-w", "1"])
        else:
            window.button_previous.config(state=tk.NORMAL)
            window.button_next.config(state=tk.NORMAL)
            window.input_ocr_data.config(state=tk.NORMAL)
            window.input_grade.config(state=tk.NORMAL)
            window.check_locked.config(state=tk.NORMAL)
    
    answerkey = window.input_answerkey.get().strip()
    window.input_answerkey_data.config(state=tk.NORMAL)
    if not check_path(answerkey):
        window.input_answerkey.delete(0, tk.END)
        window.input_answerkey.insert(0, "path/to/answerkey.csv")
        window.input_answerkey_data.delete("1.0", tk.END)
        
        window.input_answerkey_data.config(state=tk.DISABLED)
    
    if valid:
        grade = 0
        try:
            grade = int(window.input_grade.get().strip())
        except:
            pass
        grade = validate(grade, 0, 100, 0)
        file = window.label_file["text"]
        if check_path(f"{directory}/{file}"):
            file_data = analysis.get(file, {})
            file_data.update({"grade": grade})
            analysis.set(file, file_data)
        navigate(window)
    
    # if process is not None:
    #    progress = ttk.Progressbar(master=window.viewer, orient=tk.HORIZONTAL, length=100, mode="indeterminate")
    #    progress.place(x=0, y=0, width=int((window.screen_width * .66)))
    #    progress["value"] = 30
    #    progress["value"] = 100
    #    progress.destroy()
    #    return reload(window)

def navigate(window, step=0):
    directory = window.input_directory.get().strip()
    if check_path(directory):
        analysis = Arkivist(f"{directory}/kymera/analysis.json")
        if not analysis.is_empty():
            files = list(analysis.keys())
            state = Arkivist(f"{directory}/kymera/state.json")
            
            file = state.get("file", "")
            index = int(state.get("index", 0))
            page = int(state.get("page", 0))
            
            pages = ["resources/banner.png"]
            file = files[index]
            file_data = analysis.get(file, {})
            if len(file_data) > 0:
                pages = file_data.get("pages", pages)
            
            page += step
            if page < 0:
                index -= 1
                page = 0
            if page > (len(pages)-1):
                index += 1
                page = 0
                if index > (len(files)-1):
                    index = (len(files)-1)
                    file = files[index]
                    file_data = analysis.get(file, {})
                    if len(file_data) > 0:
                        pages = file_data.get("pages", pages)
                    page = (len(pages)-1)
            if index < 0:
                index = 0
            
            if index == 0 and page == 0:
                window.button_previous.config(state=tk.DISABLED)
            else:
                window.button_previous.config(state=tk.NORMAL)
            
            if index == (len(files)-1) and page == (len(pages)-1):
                window.button_next.config(state=tk.DISABLED)
            else:
                window.button_next.config(state=tk.NORMAL)
            
            state.set("index", index)
            state.set("page", page)
            file = files[index]
            file_data = analysis.get(file, {})
            
            window.locked.set(file_data.get("locked", 0))
            
            ocr_result = file_data.get("text", "")
            window.input_ocr_data.delete("1.0", tk.END)
            window.input_ocr_data.insert(tk.INSERT, ocr_result)
            
            window.label_file["text"] = file
            grade = file_data.get("grade", 0)

            window.input_grade.delete(0, tk.END)
            window.input_grade.insert(0, grade)
            
            page_img_link = "resources/banner.png"
            if len(file_data) > 0:
                pages = file_data.get("pages", [])
                if len(pages) > 1 and page <= (len(pages)-1):
                    page_img_link = pages[page]

            try:
                image = image_loader(page_img_link, window.gallery_max_width)
            except:
                image = image_loader("resources/banner.png", window.gallery_max_width)
            window.gallery.configure(image=image)
            window.gallery.image = image

def lock_data(window):
    directory = window.input_directory.get().strip()
    if check_path(directory):
        file = window.label_file["text"]
        locked = 1
        if window.locked.get() == 1:
            locked = 0
        analysis = Arkivist(f"{directory}/kymera/analysis.json")
        file_data = analysis.get(file, {})
        file_data.update({"locked": locked})
        analysis.set(file, file_data)

def modify_ocr(window):
    directory = window.input_directory.get().strip()
    if check_path(directory):
        file = window.label_file["text"]
        modified = window.input_ocr_data.get("1.0", tk.END)
        analysis = Arkivist(f"{directory}/kymera/analysis.json")
        file_data = analysis.get(file, {})
        file_data.update({"text": modified})
        analysis.set(file, file_data)

if __name__ == "__main__":
    root = KymeraGui()
    window = root.window
    window.bind("<Return>", (lambda x: reload(root)))
    root.button_previous.bind("<Button-1>", (lambda x: navigate(root, -1)))
    root.button_next.bind("<Button-1>", (lambda x: navigate(root, 1)))
    root.check_locked.bind("<Button-1>", (lambda x: lock_data(root)))
    root.input_ocr_data.bind("<KeyRelease>", (lambda x: modify_ocr(root)))
    window.tk.mainloop()