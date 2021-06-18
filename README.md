![](/resources/banner.png)

# kymera v1.2.0
PDF submissions auto-checker for teachers.
Text can be chimeric at times, often formatted into files ranging from simple text files to complex objects. PDF file is one of the more complex files that may contain additional image objects aside from textual data. The automation of checking of PDF file can drastically improve efficiency, by removing redundancy of work, especially when running over multiple of files.

## Requirements
- [cv2](https://pypi.org/project/cv2/) `pip install cv2`
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
$ py kymera.py -d "<path_to_pdf_files>" -o "<path_to_tesseract.exe>" -a "<path_to_answerkey.csv> -z 2 -s 1 -t 90 -w 1 -g 1"
```

**1.** `-d <path>` - Full path of the dirctory containing the PDF files to analyze. 
**2.** `-o <*.exe>` - Full path of the tesseract executable file for OCR API.
**3.** `-a <*.csv>` - Full path to the answer key file, must be in csv format.
**4.** `-z <1>` - Zoom factor (1-5; default = 1), affects the quality of the OCR results. Higher value means higher quality, but may slow down the analysis.
**5.** `-s <0>` - Spell check (0-1; default = 0), autocorrects mispellings on the OCR results.
**6.** `-t <0>` - Threshold (1-100; default = 80), adjust tolearance level.
**7.** `-w <0>` - Write to file (0-1; default = 0), write OCR results to file.
**8.** `-g <0>` - Gather data (0-1; default = 0), gather character data from the documents.

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
- [x] Character collector
- [ ] Character classifier
- [ ] Grader, pending

## Status
- Accuracy = 0%


## Did you know?
The repository name `kymera` was inspired from the mythological creature called Chimera, an animal with body parts from different creatures.