# pattern/matching.py

def kmp_search(text, pattern):
    """
    Melakukan pencarian string menggunakan algoritma Knuth-Morris-Pratt.
    Mengembalikan list berisi indeks awal dari semua kemunculan pattern.
    """
    def compute_lps(pattern):
        lps = [0] * len(pattern)
        length = 0
        i = 1
        while i < len(pattern):
            if pattern[i] == pattern[length]:
                length += 1
                lps[i] = length
                i += 1
            else:
                if length != 0:
                    length = lps[length - 1]
                else:
                    lps[i] = 0
                    i += 1
        return lps

    if not pattern or not text:
        return []

    pattern = pattern.lower()
    text = text.lower()
    lps = compute_lps(pattern)
    matches = []
    i = 0
    j = 0
    while i < len(text):
        if pattern[j] == text[i]:
            i += 1
            j += 1
        
        if j == len(pattern):
            matches.append(i - j)
            j = lps[j - 1]
        elif i < len(text) and pattern[j] != text[i]:
            if j != 0:
                j = lps[j - 1]
            else:
                i += 1
    return matches


def boyer_moore_search(text, pattern):
    """
    Melakukan pencarian string menggunakan algoritma Boyer-Moore.
    Mengembalikan list berisi indeks awal dari semua kemunculan pattern.
    """
    pattern = pattern.lower()
    text = text.lower()
    m = len(pattern)
    n = len(text)
    if m == 0: return []
    if n < m: return []

    matches = []
    bad_char = {pattern[i]: i for i in range(m)}

    shift = 0
    while shift <= n - m:
        j = m - 1
        while j >= 0 and pattern[j] == text[shift + j]:
            j -= 1
        
        if j < 0:
            matches.append(shift)
            shift += (m - bad_char.get(text[shift + m], -1) if shift + m < n else 1)
        else:
            shift += max(1, j - bad_char.get(text[shift + j], -1))
            
    return matches


def levenshtein_distance(s1, s2):
    """
    Menghitung Levenshtein distance antara dua string.
    """
    s1 = s1.lower()
    s2 = s2.lower()
    
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)

    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    
    return previous_row[-1]