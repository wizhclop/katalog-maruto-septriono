import os, json, base64, urllib.request, time, io, re
from PIL import Image

img_dir = 'ART_70'
json_dir = '70 image_FILE_JSON'
target_ids = ['ART-025', 'ART-067']

def load_json_safe(filepath):
    for enc in ['utf-8', 'utf-8-sig', 'utf-16', 'utf-16-le', 'cp1252']:
        try:
            with open(filepath, 'r', encoding=enc) as f:
                return json.load(f)
        except Exception:
            continue
    raise ValueError(f'Tidak dapat membaca encoding berkas: {filepath}')

print('Memproses 2 karya terakhir (ART-025 & ART-067)...')

for jf in sorted(os.listdir(json_dir)):
    if not any(tid in jf for tid in target_ids):
        continue

    jp = os.path.join(json_dir, jf)
    try:
        d = load_json_safe(jp)
    except Exception as e:
        print(f'Gagal membuka berkas {jf}: {e}')
        continue

    base_name = os.path.splitext(jf)[0]
    matched_img = next((f for f in os.listdir(img_dir) if os.path.splitext(f)[0] == base_name), None)
    if not matched_img:
        print(f'Gambar tidak ditemukan untuk {jf}')
        continue

    img_path = os.path.join(img_dir, matched_img)
    print(f'Sedang memproses: {matched_img}...')

    try:
        with Image.open(img_path) as im:
            im = im.convert('RGB')
            im.thumbnail((800, 800), Image.Resampling.LANCZOS)
            buffered = io.BytesIO()
            im.save(buffered, format='JPEG', quality=80)
            b64 = base64.b64encode(buffered.getvalue()).decode('utf-8')

        prompt = 'Analisis karya seni ini secara padat. Kembalikan HANYA teks JSON valid murni tanpa markdown dengan format kunci: {\"artist_statement\": \"2 kalimat refleksi\", \"deskripsi_kuratorial\": \"analisis teknik dan komposisi visual\", \"keywords\": \"daftar 25 kata kunci komersial dipisah koma\"}'
        
        payload = json.dumps({
            'model': 'qwen3-vl-2b-instruct',
            'messages': [{
                'role': 'user',
                'content': [
                    {'type': 'text', 'text': prompt},
                    {'type': 'image_url', 'image_url': {'url': f'data:image/jpeg;base64,{b64}'}}
                ]
            }],
            'temperature': 0.3,
            'max_tokens': 1200
        }).encode('utf-8')

        req = urllib.request.Request('http://localhost:1234/v1/chat/completions', data=payload, headers={'Content-Type': 'application/json'})
        res = urllib.request.urlopen(req, timeout=120)
        raw = json.loads(res.read().decode('utf-8'))['choices'][0]['message']['content'].strip()

        # Ekstrak blok JSON dengan regex
        clean = re.search(r'\{.*\}', raw, re.DOTALL)
        if clean:
            parsed = json.loads(clean.group(0))
        else:
            clean_str = raw.strip('').replace('json\n', '').strip()
            parsed = json.loads(clean_str)

        d.update(parsed)
        with open(jp, 'w', encoding='utf-8') as f:
            json.dump(d, f, indent=2, ensure_ascii=False)
        print(f' -> SUKSES: {d.get("Judul", jf)} berhasil dilengkapi!')

    except Exception as err:
        print(f' -> Gagal: {err}')

    time.sleep(1)

print('Proses selesai!')
