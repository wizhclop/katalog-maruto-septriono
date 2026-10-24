import os, json, stat, io
from PIL import Image, ImageFile, PngImagePlugin
import piexif

ImageFile.LOAD_TRUNCATED_IMAGES = True

img_dir = 'ART_70'
json_dir = '70 image_FILE_JSON'

def load_safe(p):
    for enc in ['utf-8', 'utf-8-sig', 'utf-16', 'utf-16-le', 'cp1252']:
        try:
            with open(p, 'r', encoding=enc) as f:
                return json.load(f)
        except Exception:
            pass
    return None

# 1. Perbaiki ART-050 (Buka kunci izin berkas & suntik PNG)
target_50 = next((f for f in os.listdir(img_dir) if 'ART-050' in f), None)
json_50 = next((f for f in os.listdir(json_dir) if 'ART-050' in f), None)

if target_50 and json_50:
    p_img = os.path.join(img_dir, target_50)
    p_json = os.path.join(json_dir, json_50)
    d = load_safe(p_json)
    
    # Hapus flag Read-Only jika ada
    os.chmod(p_img, stat.S_IWRITE)
    
    try:
        with open(p_img, 'rb') as f:
            img_data = f.read()
        im = Image.open(io.BytesIO(img_data))
        
        meta = PngImagePlugin.PngInfo()
        meta.add_text('Title', str(d.get('Judul', '')))
        meta.add_text('Description', str(d.get('artist_statement', '')))
        meta.add_text('Comment', str(d.get('deskripsi_kuratorial', '')))
        meta.add_text('Keywords', str(d.get('keywords', '')))
        
        im.save(p_img, format='PNG', pnginfo=meta)
        print(f' -> SUKSES DIPERBAIKI (PNG): {target_50}')
    except Exception as e:
        print(f' -> Gagal pada ART-050: {e}')

# 2. Cek status ART-013
target_13 = next((f for f in os.listdir(img_dir) if 'ART-013' in f), None)
json_13 = next((f for f in os.listdir(json_dir) if 'ART-013' in f), None)

if target_13 and json_13:
    p_img = os.path.join(img_dir, target_13)
    p_json = os.path.join(json_dir, json_13)
    d = load_safe(p_json)
    
    size = os.path.getsize(p_img)
    print(f'Informasi ART-013: Ukuran berkas saat ini = {size} bytes')
    
    if size == 0:
        print(' -> PERINGATAN: Berkas ART-013 berukuran 0 byte (rusak saat crash sebelumnya).')
    else:
        try:
            with open(p_img, 'rb') as f:
                raw = f.read()
            im = Image.open(io.BytesIO(raw))
            im.load()
            
            im_rgb = im.convert('RGB')
            exif_dict = {'0th': {}, 'Exif': {}, 'GPS': {}, '1st': {}, 'thumbnail': None}
            exif_dict['0th'][piexif.ImageIFD.XPTitle] = str(d.get('Judul', '')).encode('utf-16le', errors='ignore')
            exif_dict['0th'][piexif.ImageIFD.XPKeywords] = str(d.get('keywords', ''))[:1000].encode('utf-16le', errors='ignore')
            
            exif_bytes = piexif.dump(exif_dict)
            im_rgb.save(p_img, format='JPEG', quality=95, exif=exif_bytes)
            print(f' -> SUKSES DIPERBAIKI (JPG EXIF): {target_13}')
        except Exception as e:
            print(f' -> Diagnosa ART-013: {e}')
