import re
import PyPDF2
# Pastikan Anda mengimpor info_extractor dari direktori yang sama
from .info_extractor import extract_all_info

class CVExtractor:
    def _extract_text_for_regex(self, pdf_path: str) -> str:
        """
        Mengekstrak teks dari PDF dengan mempertahankan format baris baru.
        Output ini ideal untuk ekstraksi berbasis pola (Regex).
        """
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ''
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + '\n'
                
                if not text.strip():
                    print("Peringatan: Tidak ada teks yang diekstrak dari PDF.")
                return text
        except Exception as e:
            print(f"Error dalam _extract_text_for_regex: {str(e)}")
            raise

    def _create_text_for_pattern_matching(self, raw_text: str) -> str:
        """
        Mengonversi teks mentah menjadi format yang bersih untuk pattern matching (KMP/BM).
        - Mengubah ke huruf kecil
        - Menghapus karakter non-alfanumerik (kecuali spasi)
        - Mengganti spasi ganda/baris baru dengan satu spasi
        """
        # 1. Ubah ke huruf kecil
        text = raw_text.lower()
        # 2. Ganti semua jenis whitespace (baris baru, tab, spasi ganda) dengan satu spasi
        text = re.sub(r'\s+', ' ', text)
        # 3. Hapus karakter selain huruf, angka, dan spasi
        text = re.sub(r'[^a-z0-9\s]', '', text)
        return text.strip()

    def analyze_cv(self, pdf_path: str) -> dict:
        """
        Metode utama untuk menganalisis CV.
        Menghasilkan DUA jenis teks dan informasi terstruktur.
        """
        try:
            # Langkah 1: Ekstrak teks dengan format asli untuk Regex
            text_for_regex = self._extract_text_for_regex(pdf_path)
            
            # Langkah 2: Buat versi teks yang bersih untuk Pattern Matching
            text_for_pattern_matching = self._create_text_for_pattern_matching(text_for_regex)
            
            # Langkah 3: Ekstrak info terstruktur menggunakan teks yang formatnya bagus
            structured_info = extract_all_info(text_for_regex)
            
            # Langkah 4: Kembalikan semua hasil dalam satu dictionary
            analysis_result = {
                'text_for_regex': text_for_regex,
                'text_for_pattern_matching': text_for_pattern_matching,
                **structured_info  # Menambahkan 'name', 'email', dll.
            }
            return analysis_result
        except Exception as e:
            print(f"Error dalam analyze_cv: {str(e)}")
            return {'error': str(e)}