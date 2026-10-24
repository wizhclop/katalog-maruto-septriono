import os, json, csv

json_dir = '70 image_FILE_JSON'
files = sorted([f for f in os.listdir(json_dir) if f.endswith('.json')])

master_data = []

def load_safe(p):
    for enc in ['utf-8', 'utf-8-sig', 'utf-16', 'utf-16-le', 'cp1252']:
        try:
            with open(p, 'r', encoding=enc) as f:
                return json.load(f)
        except Exception:
            pass
    return None

for f in files:
    data = load_safe(os.path.join(json_dir, f))
    if data:
        master_data.append(data)

# Simpan ke art_catalog.json
with open('art_catalog.json', 'w', encoding='utf-8') as f:
    json.dump(master_data, f, indent=2, ensure_ascii=False)

# Simpan ke art_catalog.csv
if master_data:
    all_keys = []
    for item in master_data:
        for k in item.keys():
            if k not in all_keys:
                all_keys.append(k)

    with open('art_catalog.csv', 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=all_keys)
        writer.writeheader()
        writer.writerows(master_data)

print(f'BERHASIL! {len(master_data)} karya digabungkan ke art_catalog.json dan art_catalog.csv')
