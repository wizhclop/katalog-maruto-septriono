import os, json, base64, urllib.request, time, io
from PIL import Image

img_dir = 'ART_70'
json_dir = '70 image_FILE_JSON'
jsons = sorted([f for f in os.listdir(json_dir) if f.endswith('.json')])

print(f'Melanjutkan pemrosesan karya seni yang belum terisi...')

for idx, jf in enumerate(jsons, 1):
    jp = os.path.join(json_dir, jf)
    try:
        with open(jp, 'r', encoding='utf-8') as f:
            d = json.load(f)
    except Exception as e:
        print(f'[{idx}/{len(jsons)}] Gagal baca {jf}: {e}')
        continue

    # Lewati yang sudah berhasil diisi
    if d.get('artist_statement'):
        continue

    base_name = os.path.splitext(jf)[0]
    matched_img = next((f for f in os.listdir(img_dir) if os.path.splitext(f)[0] == base_name), None)
    if not matched_img:
        print(f'[{idx}/{len(jsons)}] Gambar tidak ditemukan untuk {jf}')
        continue

    img_path = os.path.join(img_dir, matched_img)
    print(f'[{idx}/{len(jsons)}] Mengirim ke AI (auto-resize): {matched_img}...')

    try:
        # Resize gambar ke ukuran aman (maks 1024px) di memori agar bebas Bad Request 400
        with Image.open(img_path) as im:
            im = im.convert('RGB')
            im.thumbnail((1024, 1024), Image.Resampling.LANCZOS)
            buffered = io.BytesIO()
            im.save(buffered, format='JPEG', quality=85)
            b64 = base64.b64encode(buffered.getvalue()).decode('utf-8')

        prompt = 'Analisis karya seni ini. Berikan respons dalam JSON valid murni tanpa markdown dengan kunci: artist_statement (2-3 kalimat filosofis), deskripsi_kuratorial (analisis teknik, komposisi, suasana), keywords (daftar 30 kata kunci komersial dipisah koma untuk SEO).'
        
        payload = json.dumps({
            'model': 'qwen3-vl-2b-instruct',
            'messages': [{
                'role': 'user',
                'content': [
                    {'type': 'text', 'text': prompt},
                    {'type': 'image_url', 'image_url': {'url': f'data:image/jpeg;base64,{b64}'}}
                ]
            }],
            'temperature': 0.4,
            'max_tokens': 1000
        }).encode('utf-8')

        req = urllib.request.Request('http://localhost:1234/v1/chat/completions', data=payload, headers={'Content-Type': 'application/json'})

        res = urllib.request.urlopen(req, timeout=120)
        raw = json.loads(res.read().decode('utf-8'))['choices'][0]['message']['content'].strip()
        clean = raw.strip('').replace('json\n', '').strip()
        parsed = json.loads(clean)
        
        d.update(parsed)
        with open(jp, 'w', encoding='utf-8') as f:
            json.dump(d, f, indent=2, ensure_ascii=False)
        print(f' -> SUKSES: {d.get("Judul", jf)} berhasil diperbarui!')

    except Exception as err:
        print(f' -> ERROR pada {jf}: {err}')

    time.sleep(1)

print('SELESAI! Seluruh sisa metadata telah berhasil diproses.')
