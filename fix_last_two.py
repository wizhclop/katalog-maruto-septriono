import os, json, piexif, tempfile, shutil
from PIL import Image, PngImagePlugin

img_dir = 'ART_70'
json_dir = '70 image_FILE_JSON'
targets = ['ART-013', 'ART-050']

def load_safe(p):
    for enc in ['utf-8', 'utf-8-sig', 'utf-16', 'utf-16-le', 'cp1252']:
        try:
            with open(p, 'r', encoding=enc) as f:
                return json.load(f)
        except Exception:
            pass
    return None

print('Memperbaiki dan menyuntikkan 2 berkas terakhir...')

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
        # Coba buka citra
        im = None
        try:
            im = Image.open(img_path)
            im.load()
        except Exception:
            # Jika header rusak, coba buka via buffer biner murni
            with open(img_path, 'rb') as f:
                raw_bytes = f.read()
            import io
            im = Image.open(io.BytesIO(raw_bytes))
            im.load()

        ext = os.path.splitext(matched_img)[1].lower()

        # Buat penulisan aman via file temporary untuk menghindari permission denied
        fd, temp_path = tempfile.mkstemp(suffix=ext)
        os.close(fd)

        if ext == '.png':
            meta = PngImagePlugin.PngInfo()
            meta.add_text('Title', judul)
            meta.add_text('Description', deskripsi_lengkap)
            meta.add_text('Comment', statement)
            meta.add_text('Keywords', keywords)
            im.save(temp_path, format='PNG', pnginfo=meta)
            im.close()
            shutil.move(temp_path, img_path)
            print(f' -> BERHASIL (PNG): {matched_img}')

        else:
            im_rgb = im.convert('RGB')
            im.close()
            exif_dict = {'0th': {}, 'Exif': {}, 'GPS': {}, '1st': {}, 'thumbnail': None}
            exif_dict['0th'][piexif.ImageIFD.ImageDescription] = deskripsi_lengkap[:1500].encode('utf-8', errors='ignore')
            exif_dict['0th'][piexif.ImageIFD.XPTitle] = judul.encode('utf-16le', errors='ignore')
            exif_dict['0th'][piexif.ImageIFD.XPKeywords] = keywords[:1500].encode('utf-16le', errors='ignore')
            exif_dict['0th'][piexif.ImageIFD.XPComment] = statement[:1500].encode('utf-16le', errors='ignore')

            exif_bytes = piexif.dump(exif_dict)
            im_rgb.save(temp_path, format='JPEG', quality=95, exif=exif_bytes)
            im_rgb.close()
            shutil.move(temp_path, img_path)
            print(f' -> BERHASIL (JPG EXIF): {matched_img}')

    except Exception as err:
        print(f' -> Masih kendala pada {matched_img}: {err}')

print('Penyelesaian tuntas!')
