"""
    (c) 2020 Rodney Maniego Jr.
    File analysis tool
    MIT License
"""

print("\nKymera")
print("")
print("Loading requirements...")
print("Please wait...")

import os
import sys
import argparse

import fitz
import pytesseract
from PIL import Image
from arkivist import Arkivist

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

def pdf_parse(directory, tesseract, threshold=80):
    # do not change
    extension = "pdf"
    
    if not isinstance(directory, str):
        print("KymeraError: 'directory' parameter must be a string.")
        return

    if not isinstance(threshold, int):
        print("KymeraWarning: 'threshold' parameter must be an integer.")
        threshold = 80

    if not (1 <= threshold <= 100):
        print("KymeraWarning: 'threshold' parameter must be an integer between 1-100.")
        threshold = 80
    
    print("\nParsing PDF files...")
    
    if not check_path(f"{directory}/img"):
        os.makedirs(f"{directory}/img")
    
    prev = ""
    path = os.getcwd()
    extensions = (extension)
    analysis = Arkivist(f"{directory}/analysis.json")
    filenames = get_filenames(directory, extensions)
    for index, filename in enumerate(filenames):
        fullpath = f"{directory}\{filename}"
        doc = fitz.Document(fullpath)
        print(f" - {fullpath}")
        
        text = ""
        for i in range(doc.page_count):
            page = doc.loadPage(i)
            pixels = page.getPixmap()
            pixels.writePNG(f"{directory}\img\{filename[:-4]}-{i}.png")
            img_path = f"{directory}\img\{filename[:-4]}-{i}.png"
            abc = ocr_api2(img_path, tesseract)
            text += abc
        analysis.set(filename, {"text": text})

def ocr_api2(path, tesseract):
    try:
        pytesseract.pytesseract.tesseract_cmd = tesseract
        return pytesseract.image_to_string(Image.open(path))
    except Exception as e:
        print(" - Error while using PyTesseract.\n\t", e)
        return ""


# kymera logic
parser = argparse.ArgumentParser(prog="kymera",
                                 usage="%(prog)s [options] path",
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

args = parser.parse_args()

# get PDF directory
directory = args.directory
if not check_path(directory):
    print(f"\nKymeraError: The directory was not found: {directory}")
    sys.exit(0)


# set tesseract location
settings = Arkivist("settings.json")
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
    if not check_path(answerkey):
        answerkey = None

if answerkey is not None:
    if len(answerkey) >= 5:
        if answerkey[-3:] != "csv":
            answerkey = None
    else:
        answerkey = None

if answerkey is None:
    print("\nKymeraWarning: Answer Key CSV file was not found, skipping grading feature.")

pdf_parse(directory, tesseract, threshold=80)