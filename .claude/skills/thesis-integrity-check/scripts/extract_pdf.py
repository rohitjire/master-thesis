#!/usr/bin/env python3
"""
extract_pdf.py - Extract text from a thesis PDF with page markers.

Usage:
    python extract_pdf.py <thesis.pdf> [-o extracted_text.txt]

Writes UTF-8 text with "===== PAGE n =====" markers so later steps can map
findings back to page numbers. Tries pdfplumber first, falls back to pypdf.
"""
import sys
import argparse


def extract(path):
    pages = []
    try:
        import pdfplumber
        with pdfplumber.open(path) as pdf:
            for i, page in enumerate(pdf.pages, 1):
                pages.append((i, page.extract_text() or ""))
        return pages
    except Exception as e:
        sys.stderr.write(f"pdfplumber unavailable/failed ({e}); trying pypdf...\n")
    from pypdf import PdfReader
    reader = PdfReader(path)
    for i, page in enumerate(reader.pages, 1):
        pages.append((i, page.extract_text() or ""))
    return pages


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf")
    ap.add_argument("-o", "--out", default="extracted_text.txt")
    args = ap.parse_args()

    pages = extract(args.pdf)
    with open(args.out, "w", encoding="utf-8") as f:
        for n, txt in pages:
            f.write(f"\n\n===== PAGE {n} =====\n\n")
            f.write(txt)

    nchars = sum(len(t) for _, t in pages)
    print(f"Extracted {len(pages)} pages, {nchars} chars -> {args.out}")
    if nchars < 500:
        print("!! Very little text extracted. The PDF may be scanned/image-based; "
              "OCR would be needed before this skill can analyze it.")


if __name__ == "__main__":
    main()
