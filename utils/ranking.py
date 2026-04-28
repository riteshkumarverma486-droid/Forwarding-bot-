def score(name, query):
    name = (name or "").lower()
    q = query.lower()
    s = 0
    if q in name: s += 5
    if name.startswith(q): s += 3
    s -= abs(len(name) - len(q)) * 0.01
    return s
