def kmp_search(text, pattern):
    """
    Melakukan pencarian string menggunakan algoritma Knuth-Morris-Pratt.
    Mengembalikan list berisi indeks awal dari semua kemunculan pattern.
    """
    def compute_lps(pattern):
        # Longest Proper Prefix which is also Suffix
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

    lps = compute_lps(pattern)
    matches = []
    i = 0  # pointer untuk text
    j = 0  # pointer untuk pattern
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