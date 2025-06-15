import PyPDF2
from .regex import patterns, extract_with_regex, extract_work_experience, extract_education, clean_text

# Tambahan untuk OCR
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import tempfile
import os

class CVExtractor:
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF file, fallback to OCR if needed."""
        try:
            print(f"Opening PDF file: {pdf_path}")
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ''
                print(f"Number of pages: {len(pdf_reader.pages)}")
                for i, page in enumerate(pdf_reader.pages):
                    page_text = page.extract_text()
                    if page_text:
                        print(f"Page {i+1} text length: {len(page_text)}")
                        text += page_text + '\n'
                # Clean the text
                text = clean_text(text)
                print(f"Total extracted text length: {len(text)}")
                # Jika hasil terlalu sedikit, fallback ke OCR
                if len(text.strip()) < 100 or not any(str(y) in text for y in range(1990, 2030)):
                    print("PyPDF2 extraction too short or no years found, using OCR fallback...")
                    text = self.ocr_pdf(pdf_path)
                if not text.strip():
                    print("Warning: No text was extracted from the PDF")
                return text
        except Exception as e:
            print(f"Error in extract_text_from_pdf: {str(e)}")
            raise Exception(f"Error reading PDF: {str(e)}")

    def ocr_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF using OCR (pytesseract + pdf2image)."""
        print("Starting OCR extraction...")
        text = ''
        with tempfile.TemporaryDirectory() as path:
            images = convert_from_path(pdf_path, output_folder=path)
            for i, image in enumerate(images):
                ocr_result = pytesseract.image_to_string(image, lang='eng')
                print(f"OCR page {i+1} text length: {len(ocr_result)}")
                text += ocr_result + '\n'
        text = clean_text(text)
        print(f"Total OCR extracted text length: {len(text)}")
        return text

    def analyze_cv(self, pdf_path: str) -> dict:
        """Main method to analyze CV using regex patterns"""
        try:
            print(f"Starting CV analysis for: {pdf_path}")
            text = self.extract_text_from_pdf(pdf_path)
            print(f"Extracted text sample: {text[:200]}...")
            # Extract information using regex patterns
            summary = extract_with_regex(text, patterns['summary'])
            skills = extract_with_regex(text, patterns['skills'])
            work_exp = extract_work_experience(text)
            education = extract_education(text)
            # Log extraction results
            print("\nExtraction Results:")
            print(f"Summary found: {len(summary)} items")
            print(f"Skills found: {len(skills)} items")
            print(f"Work experience found: {len(work_exp)} items")
            print(f"Education found: {len(education)} items")
            # Format results for display
            result = {
                'text': text,
                'summary': summary,
                'skills': skills,
                'work_experience': work_exp,
                'education': education
            }
            return result
        except Exception as e:
            print(f"Error in analyze_cv: {str(e)}")
            return {'error': str(e)} 