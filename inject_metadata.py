import os, json, piexif
from PIL import Image, PngImagePlugin

img_dir = 'ART_70'
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

print(f'Mulai menyuntikkan metadata ke {len(files)} berkas gambar...')
sukses = 0

for idx, jf in enumerate(files, 1):
    d = load_safe(os.path.join(json_dir, jf))
    if not d:
        continue

    base_name = os.path.splitext(jf)[0]
    matched_img = next((f for f in os.listdir(img_dir) if os.path.splitext(f)[0] == base_name), None)
    if not matched_img:
        print(f'[{idx}/{len(files)}] Gambar tidak ditemukan: {jf}')
        continue

    img_path = os.path.join(img_dir, matched_img)
    judul = str(d.get('Judul', ''))
    statement = str(d.get('artist_statement', ''))
    kuratorial = str(d.get('deskripsi_kuratorial', ''))
    keywords = str(d.get('keywords', ''))
    
    deskripsi_lengkap = f"{statement}\n\nKuratorial: {kuratorial}\n\nTags: {keywords}"

    try:
        ext = os.path.splitext(matched_img)[1].lower()
        if ext in ['.jpg', '.jpeg']:
            # Suntikkan via EXIF / IPTC ImageDescription & XPComment
            im = Image.open(img_path)
            exif_dict = {'0th': {}, 'Exif': {}, 'GPS': {}, '1st': {}, 'thumbnail': None}
            if 'exif' in im.info:
                try:
                    exif_dict = piexif.load(im.info['exif'])
                except Exception:
                    pass

            exif_dict['0th'][piexif.ImageIFD.ImageDescription] = deskripsi_lengkap.encode('utf-8', errors='ignore')
            exif_dict['0th'][piexif.ImageIFD.XPTitle] = judul.encode('utf-16le', errors='ignore')
            exif_dict['0th'][piexif.ImageIFD.XPKeywords] = keywords.encode('utf-16le', errors='ignore')
            exif_dict['0th'][piexif.ImageIFD.XPComment] = statement.encode('utf-16le', errors='ignore')

            exif_bytes = piexif.dump(exif_dict)
            im.save(img_path, exif=exif_bytes)
            im.close()
            sukses += 1
            print(f'[{idx}/{len(files)}] OK (JPG EXIF): {matched_img}')

        elif ext == '.png':
            # Suntikkan via Text Chunk PNG baku
            im = Image.open(img_path)
            meta = PngImagePlugin.PngInfo()
            meta.add_text("Title", judul)
            meta.add_text("Description", deskripsi_lengkap)
            meta.add_text("Comment", statement)
            meta.add_text("Keywords", keywords)
            
            im.save(img_path, pnginfo=meta)
            im.close()
            sukses += 1
            print(f'[{idx}/{len(files)}] OK (PNG Metadata): {matched_img}')

    except Exception as e:
        print(f'[{idx}/{len(files)}] Gagal injeksi {matched_img}: {e}')

print(f'SELESAI! Sebanyak {sukses} gambar telah disuntik metadata.')
