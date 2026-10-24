import os, json, piexif
from PIL import Image

jp = '70 image_FILE_JSON/ID ART-013 Terjungkal.json'
ip = 'ART_70/ID ART-013 Terjungkal.JPG'

# Baca data JSON secara aman
d = None
for enc in ['utf-8', 'utf-8-sig', 'utf-16', 'utf-16-le', 'cp1252']:
    try:
        with open(jp, 'r', encoding=enc) as f:
            d = json.load(f)
            break
    except Exception:
        pass

if not d:
    print('Gagal membaca berkas JSON!')
    exit()

judul = str(d.get('Judul', 'Terjungkal'))
statement = str(d.get('artist_statement', ''))
kuratorial = str(d.get('deskripsi_kuratorial', ''))
keywords = str(d.get('keywords', ''))
deskripsi_lengkap = f"{statement}\n\nKuratorial: {kuratorial}\n\nTags: {keywords}"

try:
    with Image.open(ip) as im:
        im_rgb = im.convert('RGB')
        
        exif_dict = {'0th': {}, 'Exif': {}, 'GPS': {}, '1st': {}, 'thumbnail': None}
        # Batasi panjang karakter agar tidak melebihi batas segmen EXIF JPEG (~64KB)
        exif_dict['0th'][piexif.ImageIFD.ImageDescription] = deskripsi_lengkap[:1500].encode('utf-8', errors='ignore')
        exif_dict['0th'][piexif.ImageIFD.XPTitle] = judul.encode('utf-16le', errors='ignore')
        exif_dict['0th'][piexif.ImageIFD.XPKeywords] = keywords[:1500].encode('utf-16le', errors='ignore')
        exif_dict['0th'][piexif.ImageIFD.XPComment] = statement[:1500].encode('utf-16le', errors='ignore')

        exif_bytes = piexif.dump(exif_dict)
        im_rgb.save(ip, format='JPEG', quality=95, exif=exif_bytes)
        
    print('SUKSES! ART-013 Terjungkal berhasil disuntik metadata!')
except Exception as e:
    print(f'Gagal: {e}')
