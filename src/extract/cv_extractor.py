import re
import PyPDF2
# Impor modul baru kita
from .info_extractor import extract_all_info

class CVExtractor:
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF file"""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ''
                for page in pdf_reader.pages:
                    text += page.extract_text() + '\n'
                if not text.strip():
                    print("Warning: No text was extracted from the PDF")
                return text
        except Exception as e:
            print(f"Error in extract_text_from_pdf: {str(e)}")
            raise Exception(f"Error reading PDF: {str(e)}")
    
    def analyze_cv(self, pdf_path: str) -> dict:
        """
        Metode utama untuk menganalisis CV.
        Mengekstrak teks mentah dan informasi terstruktur.
        """
        try:
            text = self.extract_text_from_pdf(pdf_path)
            
            # Panggil fungsi ekstraksi dari info_extractor
            structured_info = extract_all_info(text)
            
            # Gabungkan teks mentah dengan info terstruktur
            analysis_result = {
                'raw_text': text,
                **structured_info  # Ini akan menambahkan 'name', 'email', 'phone', dll.
            }
            return analysis_result
        except Exception as e:
            print(f"Error in analyze_cv: {str(e)}")
            return {'error': str(e)}