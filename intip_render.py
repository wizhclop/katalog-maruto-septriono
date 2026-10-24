with open('index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if 'render' in l.lower() or 'card.innerhtml' in l.lower() or 'curatorial' in l.lower() or 'item.' in l:
        start = max(0, i - 4)
        end = min(len(lines), i + 15)
        print(f"--- Ditemukan di sekitar baris {i+1} ---")
        print("".join(lines[start:end]))
        break
