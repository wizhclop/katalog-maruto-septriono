import os, json, piexif
from PIL import Image, PngImagePlugin

img_dir = 'ART_70'
json_dir = '70 image_FILE_JSON'
targets = ['ART-013', 'ART-025', 'ART-050']

def load_safe(p):
    for enc in ['utf-8', 'utf-8-sig', 'utf-16', 'utf-16-le', 'cp1252']:
        try:
            with open(p, 'r', encoding=enc) as f:
                return json.load(f)
        except Exception:
            pass
    return None

print('Memproses 3 berkas tertinggal...')

for jf in os.listdir(json_dir):
    if not any(t in jf for t in targets):
        continue

    d = load_safe(os.path.join(json_dir, jf))
    if not d:
        continue

    base_name = os.path.splitext(jf)[0]
    matched_img = next((f for f in os.listdir(img_dir) if os.path.splitext(f)[0] == base_name), None)
    if not matched_img:
        continue

    img_path = os.path.join(img_dir, matched_img)
    judul = str(d.get('Judul', ''))
    statement = str(d.get('artist_statement', ''))
    kuratorial = str(d.get('deskripsi_kuratorial', ''))
    keywords = str(d.get('keywords', ''))
    deskripsi_lengkap = f"{statement}\n\nKuratorial: {kuratorial}\n\nTags: {keywords}"

    try:
        with Image.open(img_path) as im:
            actual_format = im.format

        if actual_format == 'PNG':
            # Suntik via text chunk PNG
            with Image.open(img_path) as im:
                meta = PngImagePlugin.PngInfo()
                meta.add_text("Title", judul)
                meta.add_text("Description", deskripsi_lengkap)
                meta.add_text("Comment", statement)
                meta.add_text("Keywords", keywords)
                im.save(img_path, pnginfo=meta)
            print(f' -> OK (PNG): {matched_img}')

        else:
            # Format JPEG: pangkas panjang karakter jika melebihi limit EXIF
            with Image.open(img_path) as im:
                im = im.convert('RGB')
                exif_dict = {'0th': {}, 'Exif': {}, 'GPS': {}, '1st': {}, 'thumbnail': None}
                # Batasi deskripsi dan tag agar tidak meluap dari batas segmen 64KB
                exif_dict['0th'][piexif.ImageIFD.ImageDescription] = deskripsi_lengkap[:2000].encode('utf-8', errors='ignore')
                exif_dict['0th'][piexif.ImageIFD.XPTitle] = judul.encode('utf-16le', errors='ignore')
                exif_dict['0th'][piexif.ImageIFD.XPKeywords] = keywords[:2000].encode('utf-16le', errors='ignore')
                exif_dict['0th'][piexif.ImageIFD.XPComment] = statement[:2000].encode('utf-16le', errors='ignore')
                
                exif_bytes = piexif.dump(exif_dict)
                im.save(img_path, 'JPEG', quality=95, exif=exif_bytes)
            print(f' -> OK (JPG EXIF): {matched_img}')

    except Exception as err:
        print(f' -> Gagal pada {matched_img}: {err}')

print('Selesai perbaikan!')
