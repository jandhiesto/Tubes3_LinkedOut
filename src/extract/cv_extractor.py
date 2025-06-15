import fitz  # PyMuPDF
import re

class CVExtractor:
    def __init__(self, file_path):
        self.file_path = file_path
        self._raw_content = ""
        self._processed_content = ""
    
    def retrieve_raw_text(self):
        """Return the raw text content from the PDF"""
        if not self._raw_content:
            self._extract_text_from_pdf()
        return self._raw_content
    
    def retrieve_cleaned_text(self):
        """Return the processed text as a continuous string"""
        if not self._processed_content:
            self._convert_to_continuous_text()
        return self._processed_content

    def get_file_path(self):
        """Return the current PDF file path"""
        return self.file_path

    def update_file_path(self, path):
        """Update the PDF file path and reset cached content"""
        self.file_path = path
        self._raw_content = ""
        self._processed_content = ""

    def _extract_text_from_pdf(self):
        """Extract text content from all PDF pages"""
        document = fitz.open(self.file_path)
        text_content = ""
        for page_num in range(len(document)):
            page = document[page_num]
            text_content += page.get_text()
        document.close()
        self._raw_content = text_content

    def _convert_to_continuous_text(self):
        """Process text to lowercase continuous string without punctuation"""
        if not self._raw_content:
            self._extract_text_from_pdf()
        
        # Strip punctuation marks using regex
        no_punct_text = re.sub(r'[^\w\s]', '', self._raw_content)
        # Normalize whitespace and convert to lowercase
        normalized_text = re.sub(r'\s+', ' ', no_punct_text).lower().strip()
        self._processed_content = normalized_text

    def process(self):
        """Execute the complete text extraction and processing workflow"""
        self._extract_text_from_pdf()
        self._convert_to_continuous_text()