import re

patterns = {
    # Summary: Menangkap bagian summary hingga header berikutnya, lebih toleran terhadap format
    'summary': r'(?is)(?:Summary|Profile|Objective|About)\s*(.*?)(?=\s*(?:Skills|Highlights|Experience|Education|Work|Employment|Accomplishments|\Z))',

    # Skills: Menangkap daftar skills atau highlights hingga header berikutnya
    'skills': r'(?is)(?:Skills|Highlights|Technical\s*Skills|Core\s*Competencies)\s*(.*?)(?=\s*(?:Summary|Experience|Education|Work|Employment|Accomplishments|\Z))',

    # Experience: Menangkap semua bagian pengalaman kerja dengan berbagai variasi header
    'experience': r'(?is)Experience\s*(.*?)(?=\s*Education|\Z)',

    # Job Details: Lebih toleran terhadap spasi, newline, dan karakter aneh
    'job_details': r'(?is)'
                   r'(\d{2})[./-]?(\d{4})\s*[-–]+\s*(\d{2})[./-]?(\d{4}|Present|Current)'  # Tanggal mulai & akhir
                   r'(?:\s*\n+|\s+)'                                  # Baris kosong/karakter aneh
                   r'([\w\s&.,]+?)\s*\n+'                           # Company Name
                   r'(?:[^\n\w]*\n+)?'                               # Karakter aneh opsional
                   r'([\w\s]+?)\s*,\s*([\w\s]+?)\s*\n+'             # City, State
                   r'([\w\s/]+?)\s*\n+'                             # Position
                   r'((?:.+?\n)+?)(?=\d{2}[./-]?\d{4}|Education|\Z)',

    # Education: Menangkap bagian pendidikan dengan berbagai variasi header
    'education': r'(?is)(?:Education|Academic|Qualifications)\s*(.*?)(?=\Z)',

    # Education Details: Menangkap tahun, gelar, dan institusi dengan format yang lebih fleksibel
    'education_details': r'(?is)(\d{4})\s*(.*?)\s*(.*?)(?=\s*(?:-\s*|\d{4}|\Z))'
}

def clean_text(text: str) -> str:
    """Clean text from OCR artifacts and normalize whitespace, but keep newlines."""
    # Ganti karakter mirip angka dengan konteks yang tepat
    def replace_o(match):
        return match.group(1) + '0' + match.group(2)
    def replace_i(match):
        return match.group(1) + '1' + match.group(2)
    
    text = re.sub(r'(\d)[oO](\d)', replace_o, text)  # o/O di antara angka jadi 0
    text = re.sub(r'(\d)[iI](\d)', replace_i, text)  # i/I di antara angka jadi 1
    text = re.sub(r'(\d)[lL](\d)', replace_i, text)  # l/L di antara angka jadi 1
    
    # Preserve 'o' in words
    text = re.sub(r'\b0\b', 'o', text)  # Single 0 -> o (likely a word)
    text = re.sub(r'\b0n\b', 'on', text)  # 0n -> on
    text = re.sub(r'\b0f\b', 'of', text)  # 0f -> of
    text = re.sub(r'\b0r\b', 'or', text)  # 0r -> or
    
    # Preserve numbers in dates and phone numbers
    text = re.sub(r'(\d{2})[oO](\d{4})', replace_o, text)  # o/O in dates -> 0
    text = re.sub(r'(\+62|08)[oO](\d)', replace_o, text)  # o/O in phone numbers -> 0
    
    # Hapus karakter aneh dan artifacts
    text = re.sub(r'[#/4]', ' ', text)  # Remove artifacts like #/4
    text = re.sub(r'[^\S\n]+', ' ', text)  # Normalize spaces and tabs, but keep newlines
    text = re.sub(r'\n+', '\n', text)    # Normalize multiple newlines
    
    # Bersihkan bullet points dan karakter aneh di awal baris
    text = re.sub(r'^[•\-\*]\s*', '', text, flags=re.MULTILINE)
    text = re.sub(r'\n[•\-\*]\s*', '\n', text)
    
    # Bersihkan spasi berlebih di awal dan akhir
    text = text.strip()
    
    # Normalisasi format tanggal
    text = re.sub(r'(\d{2})[./-](\d{4})', r'\1/\2', text)  # Standardize date format
    
    return text

def extract_with_regex(text: str, pattern: str) -> list:
    """Extract information using regex pattern"""
    try:
        # Clean the text first
        text = clean_text(text)
        
        # Debug: Print the text being searched
        print("\nSearching in text:")
        print(text[:500] + "...")
        
        # For summary and skills, try to find the section first
        if pattern in [patterns['summary'], patterns['skills']]:
            section_name = "Summary" if pattern == patterns['summary'] else "Skills"
            section_match = re.search(rf'(?is){section_name}\s*(.*?)(?=\s*(?:Experience|Education|Work|Employment|\Z))', text)
            if section_match:
                section_text = section_match.group(1).strip()
                # Clean up the section text
                section_text = re.sub(r'^[•\-\*]\s*', '', section_text, flags=re.MULTILINE)
                section_text = re.sub(r'\n[•\-\*]\s*', '\n', section_text)
                return [section_text]
        
        # Fall back to original pattern matching
        matches = re.finditer(pattern, text, re.MULTILINE | re.IGNORECASE | re.DOTALL)
        results = []
        for match in matches:
            if len(match.groups()) > 0:
                results.append(match.group(1).strip())
            else:
                results.append(match.group().strip())
        
        # Log the extraction
        print(f"\nExtracting with pattern: {pattern}")
        print(f"Found {len(results)} matches")
        if results:
            print(f"First match: {results[0][:100]}...")
        else:
            print("No matches found!")
        
        return results
    except Exception as e:
        print(f"Error in regex extraction: {str(e)}")
        return []

def extract_work_experience(text: str) -> list:
    """Extract work experience robustly from messy PDF extraction results."""
    import re
    experiences = []
    lines = text.splitlines()
    lines = clean_ocr_years(lines)
    lines = normalize_dates(lines)
    n = len(lines)
    i = 0
    while i < n:
        # Deteksi tanggal satu baris (09/2010 - 04/2011 atau 09 2010 - 04 2011)
        date_line = re.match(r'\s*(\d{2})[ /-]+(\d{4})\s*[-–]+\s*(\d{2})[ /-]+(\d{4})', lines[i])
        # Deteksi tanggal multi-baris (09 2010, -, 04 2011)
        date_multiline = (
            i+2 < n and
            re.match(r'\s*(\d{2})\s*(\d{4})', lines[i]) and
            re.match(r'\s*-\s*', lines[i+1]) and
            re.match(r'\s*(\d{2})\s*(\d{4})', lines[i+2])
        )
        if date_line:
            start_date = f"{date_line.group(1)}/{date_line.group(2)}"
            end_date = f"{date_line.group(3)}/{date_line.group(4)}"
            j = i + 1
        elif date_multiline:
            m1 = re.match(r'\s*(\d{2})\s*(\d{4})', lines[i])
            m2 = re.match(r'\s*(\d{2})\s*(\d{4})', lines[i+2])
            start_date = f"{m1.group(1)}/{m1.group(2)}"
            end_date = f"{m2.group(1)}/{m2.group(2)}"
            j = i + 3
        else:
            i += 1
            continue
        # Ambil blok sampai sebelum tanggal berikutnya atau Education
        block = []
        while j < n and not (
            re.match(r'\s*(\d{2})[ /-]+(\d{4})\s*[-–]+\s*(\d{2})[ /-]+(\d{4})', lines[j]) or
            (j+2 < n and re.match(r'\s*(\d{2})\s*(\d{4})', lines[j]) and re.match(r'\s*-\s*', lines[j+1]) and re.match(r'\s*(\d{2})\s*(\d{4})', lines[j+2])) or
            re.match(r'\s*Education', lines[j], re.IGNORECASE)
        ):
            block.append(lines[j])
            j += 1
        # Bersihkan blok dari baris kosong/aneh
        block = [b for b in block if b.strip() and not re.match(r'^[^\w]+$', b)]
        # Parsing field: company, city, state, position, description
        company = block[0].strip() if len(block) > 0 else ""
        city, state = "", ""
        position = ""
        description_lines = []
        # Cari city, state, position
        for idx in range(1, len(block)):
            # City, State biasanya dipisah koma
            if ',' in block[idx]:
                parts = block[idx].split(',')
                city = parts[0].strip()
                state = parts[1].strip() if len(parts) > 1 else ""
                # Posisi biasanya di baris berikutnya
                if idx+1 < len(block):
                    position = block[idx+1].strip()
                    description_lines = block[idx+2:]
                else:
                    position = ""
                    description_lines = []
                break
        else:
            # fallback: jika tidak ketemu city, state
            if len(block) > 1:
                position = block[1].strip()
                description_lines = block[2:]
        description = '\n'.join(description_lines).strip()
        experiences.append({
            'date_range': f"{start_date} - {end_date}",
            'company': company,
            'city': city,
            'state': state,
            'position': position,
            'description': description
        })
        i = j
    print(f"\nWork Experience Extraction:")
    print(f"Found {len(experiences)} work experiences")
    if experiences:
        print(f"Sample: {experiences[0]}")
    return experiences

def extract_all_info(text: str) -> dict:
    """Extract all information from CV text using regex patterns"""
    try:
        # Clean the text first
        text = clean_text(text)
        
        # Extract basic information
        summary = extract_with_regex(text, patterns['summary'])
        skills = extract_with_regex(text, patterns['skills'])
        
        # Extract work experience
        work_experience = extract_work_experience(text)
        
        # Extract education
        education = extract_education(text)
        
        # Combine all information
        return {
            'summary': summary[0] if summary else 'N/A',
            'skills': skills[0] if skills else 'N/A',
            'work_experience': work_experience,
            'education': education
        }
    except Exception as e:
        print(f"Error in extract_all_info: {str(e)}")
        return {
            'summary': 'N/A',
            'skills': 'N/A',
            'work_experience': [],
            'education': []
        }

def clean_ocr_years(lines):
    import re
    cleaned = []
    
    def replace_o(match):
        return match.group(1) + '0' + match.group(2)
    def replace_i(match):
        return match.group(1) + '1' + match.group(2)
    
    for line in lines:
        # Ganti karakter mirip angka dengan konteks yang tepat
        line = re.sub(r'(\d)[oO](\d)', replace_o, line)  # o/O di antara angka jadi 0
        line = re.sub(r'(\d)[iI](\d)', replace_i, line)  # i/I di antara angka jadi 1
        line = re.sub(r'(\d)[lL](\d)', replace_i, line)  # l/L di antara angka jadi 1
        
        # Preserve 'o' in words
        line = re.sub(r'\b0\b', 'o', line)  # Single 0 -> o (likely a word)
        line = re.sub(r'\b0n\b', 'on', line)  # 0n -> on
        line = re.sub(r'\b0f\b', 'of', line)  # 0f -> of
        line = re.sub(r'\b0r\b', 'or', line)  # 0r -> or
        
        # Preserve numbers in dates
        line = re.sub(r'(\d{2})[oO](\d{4})', replace_o, line)  # o/O in dates -> 0
        line = re.sub(r'(\+62|08)[oO](\d)', replace_o, line)  # o/O in phone numbers -> 0
        
        line = re.sub(r'(?<=\d)\s+(?=\d)', '', line)  # Hapus spasi di antara digit tahun
        # Koreksi tahun 3 digit jadi 4 digit jika memungkinkan
        line = re.sub(r'(\d{2})\s*20(\d)\b', r'\1 201\2', line)
        cleaned.append(line)
    return cleaned

def normalize_dates(lines):
    """Gabungkan baris tanggal yang terpisah akibat ekstraksi PDF yang buruk."""
    import re
    normalized = []
    i = 0
    while i < len(lines):
        # Gabungkan blok tanggal yang terpisah
        if re.match(r'\d{2}\s*\d{4}', lines[i].strip()):
            start = lines[i].strip()
            # Cek baris berikutnya untuk '-', lalu baris berikutnya untuk end
            if i+2 < len(lines) and re.match(r'\s*-\s*', lines[i+1]) and re.match(r'\d{2}\s*\d{4}', lines[i+2].strip()):
                end = lines[i+2].strip()
                normalized.append(f'{start} - {end}')
                i += 3
                continue
        normalized.append(lines[i])
        i += 1
    return normalized

def extract_education(text: str) -> list:
    """Extract education details including dates, degrees, and institutions"""
    try:
        education_info = []
        # Find all education sections
        edu_sections = extract_with_regex(text, patterns['education'])
        
        for section in edu_sections:
            # Extract education details (year, degree, institution)
            edu_details = re.finditer(patterns['education_details'], section, re.MULTILINE | re.IGNORECASE | re.DOTALL)
            for match in edu_details:
                year = match.group(1).strip()
                degree = match.group(2).strip()
                institution = match.group(3).strip()
                
                # Bersihkan degree dari karakter aneh dan format yang tidak konsisten
                degree = re.sub(r'[•\-\*]\s*', '', degree)
                degree = re.sub(r'\s+', ' ', degree)
                
                # Bersihkan institution dari karakter aneh
                institution = re.sub(r'[•\-\*]\s*', '', institution)
                institution = re.sub(r'\s+', ' ', institution)
                
                # Cek apakah ada informasi tambahan dalam kurung
                if '(' in institution and ')' in institution:
                    main_institution = institution.split('(')[0].strip()
                    additional_info = institution[institution.find('(')+1:institution.find(')')].strip()
                    institution = main_institution
                    if additional_info:
                        degree = f"{degree} ({additional_info})"
                
                # Validasi data
                if year and (degree or institution):  # Minimal harus ada tahun dan salah satu dari degree/institution
                    education_info.append({
                        'year': year,
                        'degree': degree,
                        'institution': institution
                    })
        
        print(f"\nEducation Extraction:")
        print(f"Found {len(education_info)} education entries")
        if education_info:
            print(f"Sample: {education_info[0]}")
        
        return education_info
    except Exception as e:
        print(f"Error extracting education: {str(e)}")
        return []

# Example usage code removed to prevent NameError