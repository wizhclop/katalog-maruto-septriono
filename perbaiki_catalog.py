import json
import re
import os

path = "art_catalog.json"

if not os.path.exists(path):
    print("ERROR: art_catalog.json tidak ditemukan.")
    exit()

with open(path, "r", encoding="utf-8-sig", errors="ignore") as f:
    raw = f.read().strip()

# 1. Bersihkan sisa koma berlebih di akhir list sebelum ']'
fixed_raw = re.sub(r',\s*\]', ']', raw)

# 2. Cek apakah tanda kurung penutup hilang
if not fixed_raw.endswith(']'):
    # Jika terpotong di tengah entri, cari penutup kurung kurawal terakhir
    last_brace = fixed_raw.rfind('}')
    if last_brace != -1:
        fixed_raw = fixed_raw[:last_brace+1] + '\n]'
    else:
        fixed_raw += '\n]'

try:
    data = json.loads(fixed_raw)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"BERHASIL: art_catalog.json kembali sehat dan valid! Total karya tersimpan: {len(data)}")

except Exception as err:
    print(f"Pola reguler gagal ({err}), mengaktifkan penyelamatan regex...")
    items = []
    # Ekstrak tiap blok {...} yang valid
    pattern = re.compile(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', re.DOTALL)
    for block in pattern.finditer(raw):
        try:
            parsed = json.loads(block.group(0))
            items.append(parsed)
        except:
            pass

    if items:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(items, f, indent=2, ensure_ascii=False)
        print(f"PULIH DARURAT: Berhasil menyelamatkan {len(items)} karya ke art_catalog.json!")
    else:
        print("ERROR: Tidak ada blok JSON yang dapat diselamatkan.")
