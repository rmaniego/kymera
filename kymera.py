"""
    (c) 2020 Rodney Maniego Jr.
    File analysis tool
    MIT License
"""

VERSION = "1.1.0"

print(f"\nKymera v{VERSION}")

print("\nLoading requirements...")
print("Please wait...")

import os
import sys
import argparse

import cv2
import fitz
import operator
import pytesseract
from PIL import Image
from arkivist import Arkivist
from maguro import Maguro

import re
import numpy as np
import textdistance
import pandas as pd
from collections import Counter

print("Done.")

# utils
def check_path(path):
    if path.strip() == "":
        return False
    return os.path.exists(path)

def get_filenames(path, extensions=[]):
    filenames = []
    for filepath in os.listdir(path):
        if filepath.split(".")[-1].lower() in extensions:
            filenames.append(filepath)
    return filenames

def pdf_parse(directory, tesseract, answerkey=None, zoomfactor=1, spellcheck=0, threshold=80):
    
    if not isinstance(directory, str):
        print("KymeraError: 'directory' parameter must be a string.")
        return
    
    validate(threshold, 1, 100, 80)
    validate(zoomfactor, 1, 5, 1)
    validate(spellcheck, 0, 1, 0)
    
    print("\nParsing PDF files...")
    
    if not check_path(f"{directory}/img"):
        os.makedirs(f"{directory}/img")
    
    prev = ""
    path = os.getcwd()
    extensions = ["pdf"]
    lint = AutoCorrect()
    analysis = Arkivist(f"{directory}/analysis.json")
    filenames = get_filenames(directory, extensions)
    for index, filename in enumerate(filenames):
        fullpath = f"{directory}\{filename}"
        
        with fitz.Document(fullpath) as doc:
            print(f" - {fullpath}")
            
            text = ""
            for i, page in enumerate(doc):
                temp = page.getText()
                if temp != "":
                    text += temp
                else:
                    matrix = fitz.Matrix(zoomfactor, zoomfactor)  # zoom factor
                    pixels = page.getPixmap(matrix=matrix)
                    pixels.writePNG(f"{directory}\img\{filename[:-4]}-{i}.png")
                    img_path = f"{directory}\img\{filename[:-4]}-{i}.png"
                    text += lint.autocorrect(ocr_api2(img_path, tesseract), spellcheck=spellcheck)
        analysis.set(filename, {"text": text})

def ocr_api2(path, tesseract):
    try:
        pytesseract.pytesseract.tesseract_cmd = tesseract
        return pytesseract.image_to_string(Image.open(path))
    except Exception as e:
        print(" - Error while using PyTesseract.\n\t", e)
        return ""

class AutoCorrect:
    def __init__(self):
        self.jargons = Maguro("data/en20k.txt", "\n")    
        with open("data/python.txt", "r", encoding="utf8") as file:
            self.jargons.extend(re.findall('\w+', file.read().lower()))
        with open("data/custom.txt", "r", encoding="utf8") as file:
            self.jargons.extend(re.findall('\w+', file.read().lower()))
        
        self.vocabulary = set(self.jargons.unpack())
        
        self.frequency = dict(Counter(self.jargons.unpack()))
        for item in Maguro("data/enwiki-20190320-words-frequency.txt", "\n").items():
            if " " in item:
                word, frequency = item.split(" ")
                frequency = self.frequency.get(str(word), 0) + int(frequency)
                self.frequency.update({str(word): frequency})
        
        self.frequency = dict(sorted(self.frequency.items(), key=operator.itemgetter(1),reverse=True))
        self.frequency = {k: self.frequency[k] for k in list(self.frequency)[:10000]}
        
        self.probability = {}
        total = sum(self.frequency.values()) 
        for item in self.frequency.keys():
            self.probability[item] = self.frequency[item]/total

    def autocorrect(self, content, spellcheck=0):
        if spellcheck != 1:
            return content
            
        autocorrected = []
        for line in pad(content).split("\n"):
            for word in line.split(" "):
                if word.strip() != "":
                    temp = word.lower()
                    if temp in self.vocabulary:
                        autocorrected.append(word)
                    else:
                        try:
                            # https://predictivehacks.com/how-to-build-an-autocorrect-in-python/
                            df = pd.DataFrame.from_dict(self.probability, orient="index").reset_index()
                            df = df.rename(columns={"index": "Word", 0: "Probability"})
                            df['Similarity'] = [1-(textdistance.Jaccard(qval=2).distance(w, temp)) for w in self.vocabulary]
                            output = df.sort_values(['Similarity'], ascending=False).head()
                            autocorrected.append(output['Word'].iloc[0])
                        except:
                            autocorrected.append(word)
                autocorrected.append(" ")
            autocorrected.append("\n")
        return "".join(autocorrected)

def handwriting(path):
    img = cv2.imread(path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    _, contours, _  = cv2.findContours(gray.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

def validate(value, minimum, maximum, fallback):
    if not isinstance(value, int):
        print("KymeraWarning: 'value' parameter must be an integer.")
        value = int(fallback)
    if not (minimum <= value <= maximum):
        print(f"KymeraWarning: 'value' parameter must be an integer between {minimum}-{maximum}.")
        value = int(fallback)
    return value

def pad(string):
    """ Decongest statements """
    padded = string.replace("\r", "").replace("\t", " ")
    symbols = ["#", "%", "*", ")", "+", "-", "=", ":",
                "{", "}", "]", "\"", "'", "<", ">" ]
    for item in symbols:
        padded = padded.replace(item, f" {item} ")
    return padded.replace("(", "( ")



################
# kymera logic #
################
parser = argparse.ArgumentParser(prog="kymera",
                                 description="Analyze PDF files")
parser.add_argument("-d",
                    "--directory",
                    metavar="directory",
                    type=str,
                    help="Directory of the PDF files.",
                    required=True)

parser.add_argument("-a",
                    "--answerkey",
                    metavar="answerkey",
                    type=str,
                    help="Filepath of the answer key csv file.")

parser.add_argument("-t",
                    "--tesseract",
                    metavar="tesseract",
                    type=str,
                    help="Filepath of the Tesseract executible file.")

parser.add_argument("-z",
                    "--zoomfactor",
                    metavar="zoomfactor",
                    type=int,
                    help="Zoom factor for images, affects the quality of OCR results.")

parser.add_argument("-s",
                    "--spellcheck",
                    metavar="spellcheck",
                    type=int,
                    help="Autocorrect misspellings on the OCR results.")

args = parser.parse_args()

# get PDF directory
directory = args.directory
if not check_path(directory):
    print(f"\nKymeraError: The directory was not found: {directory}")
    sys.exit(0)


# set tesseract location
if not check_path("data"):
    os.makedirs("data")

settings = Arkivist("data/settings.json")
tesseract = args.tesseract
if tesseract is None:
    tesseract = settings.get("tesseract", None)

if tesseract is not None:
    if check_path(tesseract) and "tesseract.exe" in tesseract:
        settings.set("tesseract", tesseract)
    else:
        tesseract = None

if tesseract is None:
    print(f"\nKymeraError: The Tesseract executable file was not found.")
    sys.exit(0)

# set answer key file
answerkey = args.answerkey
if answerkey is not None:
    if len(answerkey) >= 5:
        if answerkey[-3:] != "csv":
            answerkey = None
    else:
        answerkey = None
    if answerkey is not None:
        if not check_path(answerkey):
            answerkey = None

if answerkey is None:
    print("\nKymeraWarning: Answer Key CSV file was not found, skipping grading feature.")

# set the zoom factor
zoomfactor = args.zoomfactor
if zoomfactor is not None:
    if not (1 <= zoomfactor <= 5):
        zoomfactor = 2

# set the spell check flag
spellcheck = args.spellcheck
if spellcheck is not None:
    if not (0 <= spellcheck <= 1):
        spellcheck = 0

pdf_parse(directory, tesseract, answerkey=answerkey, zoomfactor=zoomfactor, spellcheck=spellcheck, threshold=80)