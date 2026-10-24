import os, json, csv

json_dir = '70 image_FILE_JSON'
files = sorted([f for f in os.listdir(json_dir) if f.endswith('.json')])

def load_safe(p):
    for enc in ['utf-8', 'utf-8-sig', 'utf-16', 'utf-16-le', 'cp1252']:
        try:
            with open(p, 'r', encoding=enc) as f:
                return json.load(f)
        except Exception:
            pass
    return None

updated_items = []

for jf in files:
    jp = os.path.join(json_dir, jf)
    d = load_safe(jp)
    if not d:
        continue

    # Tambahkan atribut etalase bisnis standar
    d.setdefault('status_karya', 'Tersedia')
    d.setdefault('harga_karya_asli_idr', '')
    d.setdefault('lisensi_cetak_digital', 'Tersedia')
    d.setdefault('harga_lisensi_cetak_idr', '')
    d.setdefault('kanal_distribusi', 'Koleksi Pribadi')

    with open(jp, 'w', encoding='utf-8') as f:
        json.dump(d, f, indent=2, ensure_ascii=False)
    
    updated_items.append(d)

# Perbarui berkas master art_catalog.json
with open('art_catalog.json', 'w', encoding='utf-8') as f:
    json.dump(updated_items, f, indent=2, ensure_ascii=False)

# Perbarui berkas master art_catalog.csv
if updated_items:
    all_keys = []
    for item in updated_items:
        for k in item.keys():
            if k not in all_keys:
                all_keys.append(k)

    with open('art_catalog.csv', 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=all_keys)
        writer.writeheader()
        writer.writerows(updated_items)

print(f'BERHASIL! Struktur bisnis etalase telah disinkronkan ke 70 berkas JSON, art_catalog.json, dan art_catalog.csv.')
