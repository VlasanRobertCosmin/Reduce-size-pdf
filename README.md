# PDF Compressor

A simple Python script that automatically compresses PDF files until they are smaller than **10 MB**.

## Features

* Automatically reduces PDF file size
* Compresses and resizes embedded images
* Tries multiple compression levels
* Stops once the PDF is below **10 MB**
* Uses PyMuPDF and Pillow

## Installation

```bash
pip install -U pymupdf pillow
```

## Usage

```bash
python compress_pdf.py input.pdf output.pdf
```

Example:

```bash
python compress_pdf.py document.pdf document_compressed.pdf
```

The script automatically tries different compression settings and creates the smallest suitable PDF while preserving as much quality as possible.
