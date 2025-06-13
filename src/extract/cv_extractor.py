import re
import PyPDF2

class CVExtractor:
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF file"""
        try:
            print(f"Opening PDF file: {pdf_path}")
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ''
                print(f"Number of pages: {len(pdf_reader.pages)}")
                
                for i, page in enumerate(pdf_reader.pages):
                    page_text = page.extract_text()
                    print(f"Page {i+1} text length: {len(page_text)}")
                    text += page_text + '\n'
                
                print(f"Total extracted text length: {len(text)}")
                if not text.strip():
                    print("Warning: No text was extracted from the PDF")
                return text
        except Exception as e:
            print(f"Error in extract_text_from_pdf: {str(e)}")
            raise Exception(f"Error reading PDF: {str(e)}")
    
    def analyze_cv(self, pdf_path: str) -> dict:
        """Main method to analyze CV"""
        try:
            print(f"Starting CV analysis for: {pdf_path}")
            text = self.extract_text_from_pdf(pdf_path)
            print(f"Extracted text sample: {text[:200]}...")
            return {'text': text}
        except Exception as e:
            print(f"Error in analyze_cv: {str(e)}")
            return {'error': str(e)} 