def levenshtein_distance(s1: str, s2: str) -> int:
    """
    Menghitung jarak Levenshtein antara dua string.
    Jarak Levenshtein adalah jumlah minimum operasi single-character edit
    (insertions, deletions, substitutions) yang diperlukan untuk mengubah satu string menjadi string lainnya.
    """
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

def calculate_similarity(s1: str, s2: str) -> float:
    """
    Menghitung tingkat kemiripan antara dua string menggunakan Levenshtein Distance.
    Mengembalikan nilai antara 0 (tidak mirip) sampai 1 (identik).
    """
    if not s1 or not s2:
        return 0.0
    
    max_len = max(len(s1), len(s2))
    if max_len == 0:
        return 1.0
    
    distance = levenshtein_distance(s1, s2)
    return 1.0 - (distance / max_len)

def fuzzy_search(text: str, pattern: str, threshold: float = 0.8) -> list[tuple[int, float]]:
    """
    Melakukan pencarian fuzzy menggunakan Levenshtein Distance.
    
    Args:
        text: Teks yang akan dicari
        pattern: Pola yang dicari
        threshold: Ambang batas kemiripan (0.0 - 1.0)
    
    Returns:
        List of tuples (index, similarity_score) untuk setiap kemunculan yang memenuhi threshold
    """
    text = text.lower()
    pattern = pattern.lower()
    matches = []
    
    words = text.split()
    
    for i, word in enumerate(words):
        similarity = calculate_similarity(word, pattern)
        if similarity >= threshold:
            start_pos = text.find(word)
            matches.append((start_pos, similarity))
    
    return sorted(matches, key=lambda x: x[1], reverse=True)

def fuzzy_search_all(text: str, patterns: list[str], threshold: float = 0.8) -> dict[str, list[tuple[int, float]]]:
    """
    Melakukan pencarian fuzzy untuk multiple patterns.
    
    Args:
        text: Teks yang akan dicari
        patterns: List of patterns yang dicari
        threshold: Ambang batas kemiripan (0.0 - 1.0)
    
    Returns:
        Dictionary dengan key pattern dan value list of tuples (index, similarity_score)
    """
    results = {}
    for pattern in patterns:
        matches = fuzzy_search(text, pattern, threshold)
        if matches:
            results[pattern] = matches
    return results 