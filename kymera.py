"""
    (c) 2020 Rodney Maniego Jr.
    File analysis tool
    MIT License
"""

VERSION = "1.2.0"

print(f"\nKymera v{VERSION}")

print("\nLoading requirements...")
print("Please wait...")

import os
import sys
import argparse
from random import randint

import cv2
import fitz
import operator
import pytesseract
from PIL import Image
from arkivist import Arkivist
from sometime import Sometime
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

def pdf_parse(directory, tesseract, answerkey=None, zoomfactor=1, spellcheck=0, threshold=80, write=0, gather=0):
    
    if not isinstance(directory, str):
        print("KymeraError: 'directory' parameter must be a string.")
        return
    
    threshold = validate(threshold, 1, 100, 80)
    zoomfactor = validate(zoomfactor, 1, 5, 1)
    spellcheck = validate(spellcheck, 0, 1, 0)
    write = validate(write, 0, 1, 0)
    gather = validate(gather, 0, 1, 0)
    
    print("\nParsing PDF files...")
    
    if not check_path(f"{directory}/img"):
        os.makedirs(f"{directory}/img")

    if not check_path(f"{directory}/text") and write == 1:
        os.makedirs(f"{directory}/text")
    
    if not check_path("dataset"):
        os.makedirs("dataset")
    
    prev = ""
    path = os.getcwd()
    extensions = ["pdf"]
    lint = AutoCorrect()
    analysis = Arkivist(f"{directory}/analysis.json")
    filenames = get_filenames(directory, extensions)
    for index, filename in enumerate(filenames):
        fullpath = f"{directory}/{filename}"
        
        text = ""
        with fitz.Document(fullpath) as doc:
            print(f" - {fullpath}")
            for i, page in enumerate(doc):
                matrix = fitz.Matrix(zoomfactor, zoomfactor)  # zoom factor
                pixels = page.getPixmap(matrix=matrix)
                pixels.writePNG(f"{directory}/img/{filename[:-4]}-{i}.png")
                img_path = f"{directory}/img/{filename[:-4]}-{i}.png"
                text += lint.autocorrect(ocr_api2(img_path, tesseract), spellcheck=spellcheck)
                if gather == 1:
                    handwriting(img_path, )
        if write == 1:
            text_filename = ".".join(list(filename.split("."))[:-1])
            with open(f"{directory}/text/{text_filename}.txt", "w+", encoding="utf-8") as file:
                file.write(text)
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
        self.jargons = Maguro("resources/en20k.txt", "\n")    
        with open("resources/python.txt", "r", encoding="utf8") as file:
            self.jargons.extend(re.findall('\w+', file.read().lower()))
        with open("resources/custom.txt", "r", encoding="utf8") as file:
            self.jargons.extend(re.findall('\w+', file.read().lower()))
        
        self.vocabulary = set(self.jargons.unpack())
        
        self.frequency = dict(Counter(self.jargons.unpack()))
        for item in Maguro("resources/enwiki-20190320-words-frequency.txt", "\n").items():
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
    dataset = Maguro("dataset/files.txt", "\n")

    img = cv2.imread(path)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # cv2.imshow("gray", gray)

    ret, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU)
    # cv2.imshow("thresh", thresh)

    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=lambda contour: cv2.boundingRect(contour)[0])

    for i, contour in enumerate(contours):
        x, y, w, h = cv2.boundingRect(contour)
        cropped = img[y:y + h, x:x + w].copy()
        ts = Sometime().timestamp()
        uid1 = str(randint(1, 99999)).zfill(5)
        uid2 = str(randint(1, 99999)).zfill(5)
        filename = f"dataset/{ts}_{uid1}_{uid2}.png"
        dataset.append(filename)
        cv2.imwrite(filename, resize(cropped))

def resize(img):
    # https://stackoverflow.com/a/65314036/4943299
    h, w = img.shape[:2]
    size = max((h, w))
    min_size = np.amin([h,w])
    crop_img = img[int(h/2-min_size/2):int(h/2+min_size/2), int(w/2-min_size/2):int(w/2+min_size/2)]
    return cv2.resize(crop_img, (size, size), interpolation=cv2.INTER_AREA)
        

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

def default(value, minimum, maximum, fallback):
    if value is not None:
        if not (minimum <= value <= maximum):
            return fallback
        return value
    return fallback



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

parser.add_argument("-o",
                    "--ocr",
                    metavar="ocr",
                    type=str,
                    help="Filepath of the Tesseract executible file.")

parser.add_argument("-x",
                    "--threshold",
                    metavar="threshold",
                    type=int,
                    help="Tolerance level for grading.")

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

parser.add_argument("-w",
                    "--write",
                    metavar="write",
                    type=int,
                    help="Dump OCR results to plain text file.")

parser.add_argument("-g",
                    "--gather",
                    metavar="gather",
                    type=int,
                    help="Collect character data from documents.")

args = parser.parse_args()

# get PDF directory
directory = args.directory
if not check_path(directory):
    print(f"\nKymeraError: The directory was not found: {directory}")
    sys.exit(0)


# set tesseract location
if not check_path("data"):
    os.makedirs("data")

settings = Arkivist("resources/settings.json")
tesseract = args.ocr
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

# if answerkey is None:
#    print("\nKymeraWarning: Answer Key CSV file was not found, skipping grading feature.")

# set the zoom factor
threshold = default(args.threshold, 1, 100, 80)

# set the zoom factor
zoomfactor = default(args.zoomfactor, 1, 5, 1)

# set the spell check flag
spellcheck = default(args.spellcheck, 0, 1, 0)

# set the write to file flag
write = default(args.write, 0, 1, 0)

# set the gather to file flag
gather = default(args.gather, 0, 1, 0)

pdf_parse(directory, tesseract, answerkey=answerkey, zoomfactor=zoomfactor, spellcheck=spellcheck, threshold=80, write=write, gather=gather)