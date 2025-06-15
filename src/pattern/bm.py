def boyer_moore_search(text, pattern):
    """
    Melakukan pencarian string menggunakan algoritma Boyer-Moore
    dengan Bad Character Heuristic dan Good Suffix Heuristic.
    Mengembalikan list berisi indeks awal dari semua kemunculan pattern.
    """
    m = len(pattern)
    n = len(text)
    if m == 0:
        return []
    if n < m:
        return []

    matches = []

    # --- Preprocessing untuk Bad Character Heuristic ---
    bad_char = {}
    for i in range(m):
        bad_char[pattern[i]] = i

    # --- Preprocessing untuk Good Suffix Heuristic ---
    s = [0] * (m + 1)
    f = [0] * (m + 1)
    
    i = m
    j = m + 1
    f[i] = j
    while i > 0:
        while j <= m and pattern[i - 1] != pattern[j - 1]:
            if s[j] == 0:
                s[j] = j - i
            j = f[j]
        i -= 1
        j -= 1
        f[i] = j
    
    j = f[0]
    for i in range(m + 1):
        if s[i] == 0:
            s[i] = j
        if i == j:
            j = f[j]

    # --- Proses Pencarian ---
    shift = 0
    while shift <= n - m:
        j = m - 1
        while j >= 0 and pattern[j] == text[shift + j]:
            j -= 1
        
        if j < 0:
            matches.append(shift)
            # Geser berdasarkan Good Suffix Rule untuk menemukan kemunculan berikutnya
            shift += s[0]
        else:
            # Geser berdasarkan nilai maksimum dari Bad Character dan Good Suffix
            char_text = text[shift + j]
            bad_char_shift = j - bad_char.get(char_text, -1)
            good_suffix_shift = s[j + 1]
            
            shift += max(bad_char_shift, good_suffix_shift)
            
    return matches 