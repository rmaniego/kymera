# kymera v1.1.0
PDF submissions auto-checker for teachers.

## Requirements
- [Pillow](https://pypi.org/project/Pillow/) `pip install Pillow`
- [PyMuPDF](https://pypi.org/project/PyMuPDF/) `pip install PyMuPDF`
- [Tesseract](https://github.com/tesseract-ocr/tesseract) version 5.0.0.x or later, download appropriate [binary file](https://tesseract-ocr.github.io/tessdoc/Home.html).
- [Python-tesseract](https://pypi.org/project/pytesseract/) `pip install pytesseract`
- [Arkivist](https://pypi.org/project/arkivist/) `pip install arkivist`
- [Maguro](https://pypi.org/project/maguro/) `pip install maguro`

## Lexicon
[W3Schools / Python](https://www.w3schools.com/python/)
[Python 3.9.5 Documentation](https://docs.python.org/3/download.html)
[first20hours / google-10000-english](https://github.com/first20hours/google-10000-english)
[Wikipedia Word Frequency](https://raw.githubusercontent.com/IlyaSemenov/wikipedia-word-frequency/master/results/enwiki-20190320-words-frequency.txt)

## Usage
```bash
$ py kymera.py -d "<path_to_pdf_files>" -t "<path_to_tesseract.exe>" -a "<path_to_answerkey.csv> -z 2 -s 1"
```

**1.** `-d <path>` - Full path of the dirctory containing the PDF files to analyze. 
**2.** `-t <*.exe>` - Full path of the tesseract executable file.
**3.** `-a <*.csv>` - Full path to the answer key file, must be in csv format.
**4.** `-z <1>` - Zoom factor (1-5; default = 1), affects the quality of the OCR results. Higher value means higher quality, but may slow down the analysis.
**5.** `-s <0>` - Spell check (0-1; default = 0), autocorrects mispellings on the OCR results.

## Answer Key format
```csv
"answer, enclosed in double quotes", score
"abcde", 1
"12345", 1
"hello", 1
...
"5 + 2 = 7", 5
```

## Features
- [x] OCR, quality = low
- [ ] Spellcheck, ongoing 
- [ ] Grader, pending

## Status
- Accuracy = 0%