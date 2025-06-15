import re

def locate_section(content, search_terms):
    """
    Locate the beginning of a section using provided search terms.
    Returns matching term and its position.
    """
    for term in search_terms:
        try:
            regex_pattern = r'^\s*' + re.escape(term) + r'\s*$'
            found_match = re.search(regex_pattern, content, re.IGNORECASE | re.MULTILINE)
            if found_match:
                return term, found_match.start()
        except re.error:
            continue
    return None, -1

def retrieve_section_content(content, section_keywords, boundary_headings):
    """
    Retrieves content for a specific section, ending at the next recognized heading.
    """
    _, section_start = locate_section(content, section_keywords)
    if section_start == -1:
        return "Not Found"

    section_end = len(content)
    
    # Locate the beginning of the subsequent section to define current section boundary
    # Search within text following the current section start
    remaining_content = content[section_start + 1:] 
    
    for header in boundary_headings:
        # Skip keywords belonging to the current section
        if header.lower() in [keyword.lower() for keyword in section_keywords]:
            continue

        _, next_header_pos = locate_section(remaining_content, [header])
        if next_header_pos != -1:
            # Convert relative position to absolute position
            absolute_position = section_start + 1 + next_header_pos
            section_end = min(section_end, absolute_position)

    # Get content from end of header line to beginning of next section
    header_line_match = re.search(r'.*', content[section_start:])
    if header_line_match:
        content_start = section_start + header_line_match.end()
        return content[content_start:section_end].strip()
    
    return "Not Found"

def parse_cv_sections(content):
    """
    Parses all essential sections (Summary, Skills, Experience, Education) from CV content.
    """
    section_mappings = {
        'summary': ['professional summary', 'executive profile', 'career overview', 'executive summary','summary', 'overview', 'profile', 'objective'],
        'skills': [ 'areas of expertise', 'skill highlights', 'core strengths', 'core qualifications','skills', 'abilities', 'technologies'],
        'experience': ['professional experience', 'work experience', 'teaching experience','experience', 'work history', 'employment history'],
        'education': [ 'education and training','education', 'qualifications']
    }

    recognized_headers = [ # Complete Header Map
        # Summary variants
        'Executive Profile','career overview', 'executive summary', 'Summary', 'Overview', 'Profile', 'Objective', 
        # Skills variants
        'Areas of Expertise','Skill Highlights', 'core strengths', 'core qualifications','Skills', 'Abilities', 'Technologies', 
        # Experience variants
         'Work experience', 'Teaching experience','Professional Experience', 'Experience','Work History', 'Employment History', 
        # Education variants
        'Education and Training','Education', 
        # Termination markers
        'Accomplishments', 'Highlights', 'Additional Information', 'References', 'Website and Links', 'Affiliations'
    ]

    parsed_sections = {}
    for section_key, keyword_list in section_mappings.items():
        parsed_sections[section_key] = retrieve_section_content(content, keyword_list, recognized_headers)

    return parsed_sections