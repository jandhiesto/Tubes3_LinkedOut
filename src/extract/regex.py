import re

patterns = {
    # Summary: Menangkap bagian summary hingga header berikutnya, lebih toleran terhadap format
    'summary': r'(?is)(?:Summary|Profile|Objective|About)\s*(.*?)(?=\s*(?:Skills|Highlights|Experience|Education|Work|Employment|\Z))',

    # Skills: Menangkap daftar skills atau highlights hingga header berikutnya
    'skills': r'(?is)(?:Skills|Highlights|Technical\s*Skills|Core\s*Competencies)\s*(.*?)(?=\s*(?:Summary|Experience|Education|Work|Employment|\Z))',

    # Experience: Menangkap semua bagian pengalaman kerja dengan berbagai variasi header
    'experience': r'(?is)(?:Experience|Work\s*Experience|Employment|Professional\s*Experience)\s*(.*?)(?=\s*Education|\Z)',

    # Job Details: Lebih toleran terhadap spasi, newline, dan karakter aneh
    'job_details': r'(?is)'
                   r'(\d{2}[./-]?\d{4})\s*[-–]?\s*(\d{2}[./-]?\d{4}|Present|Current)'  # Tanggal mulai & akhir
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
    # Ganti karakter mirip angka
    text = text.replace('O', '0').replace('o', '0')
    text = re.sub(r'(?<=\d)I(?=\d)', '1', text)  # I di antara angka jadi 1
    text = re.sub(r'(?<=\d)l(?=\d)', '1', text)  # l di antara angka jadi 1
    
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

def clean_ocr_years(lines):
    import re
    cleaned = []
    for line in lines:
        # Ganti karakter mirip angka
        line = line.replace('O', '0').replace('o', '0')
        line = re.sub(r'(?<=\d)I(?=\d)', '1', line)  # I di antara angka jadi 1
        line = re.sub(r'(?<=\d)l(?=\d)', '1', line)  # l di antara angka jadi 1
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
        date_line = re.match(r'\s*(\d{2})[./-]?(\d{4})\s*[-–]+\s*(\d{2})[./-]?(\d{4})', lines[i])
        # Deteksi tanggal multi-baris (09 2010, -, 04 2011)
        date_multiline = (
            i+2 < n and
            re.match(r'\s*(\d{2})[./-]?(\d{4})', lines[i]) and
            re.match(r'\s*[-–]\s*', lines[i+1]) and
            re.match(r'\s*(\d{2})[./-]?(\d{4})', lines[i+2])
        )
        # Deteksi tanggal dengan "Present" atau "Current"
        date_present = re.match(r'\s*(\d{2})[./-]?(\d{4})\s*[-–]+\s*(Present|Current)', lines[i], re.IGNORECASE)
        
        if date_line:
            start_date = f"{date_line.group(1)}/{date_line.group(2)}"
            end_date = f"{date_line.group(3)}/{date_line.group(4)}"
            j = i + 1
        elif date_multiline:
            m1 = re.match(r'\s*(\d{2})[./-]?(\d{4})', lines[i])
            m2 = re.match(r'\s*(\d{2})[./-]?(\d{4})', lines[i+2])
            start_date = f"{m1.group(1)}/{m1.group(2)}"
            end_date = f"{m2.group(1)}/{m2.group(2)}"
            j = i + 3
        elif date_present:
            start_date = f"{date_present.group(1)}/{date_present.group(2)}"
            end_date = "Present"
            j = i + 1
        else:
            i += 1
            continue

        # Ambil blok sampai sebelum tanggal berikutnya atau Education
        block = []
        while j < n and not (
            re.match(r'\s*(\d{2})[./-]?(\d{4})\s*[-–]+\s*(\d{2})[./-]?(\d{4})', lines[j]) or
            re.match(r'\s*(\d{2})[./-]?(\d{4})\s*[-–]+\s*(Present|Current)', lines[j], re.IGNORECASE) or
            (j+2 < n and re.match(r'\s*(\d{2})[./-]?(\d{4})', lines[j]) and re.match(r'\s*[-–]\s*', lines[j+1]) and re.match(r'\s*(\d{2})[./-]?(\d{4})', lines[j+2])) or
            re.match(r'\s*(?:Education|Academic|Qualifications)', lines[j], re.IGNORECASE)
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

        # Cari city, state, position dengan lebih fleksibel
        for idx in range(1, len(block)):
            # City, State biasanya dipisah koma
            if ',' in block[idx]:
                parts = [p.strip() for p in block[idx].split(',')]
                city = parts[0]
                state = parts[1] if len(parts) > 1 else ""
                # Posisi bisa di baris yang sama setelah koma atau di baris berikutnya
                if len(parts) > 2:
                    position = parts[2]
                    description_lines = block[idx+1:]
                elif idx+1 < len(block):
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

        # Bersihkan description dari bullet points dan karakter aneh
        description = '\n'.join(description_lines).strip()
        description = re.sub(r'^[•\-\*]\s*', '', description, flags=re.MULTILINE)
        description = re.sub(r'\n[•\-\*]\s*', '\n', description)

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