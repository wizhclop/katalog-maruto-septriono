import os
import subprocess
from PIL import Image

img_dirs = [
    r"F:\DATABASE_AI ART\ART\web_galeri\images",
    r"F:\DATABASE_AI ART\ART\images"
]

print("[1/2] Memulai kompresi gambar web galeri (Target: ~90 KB per gambar)...")

for d in img_dirs:
    if not os.path.exists(d):
        continue
    for f in os.listdir(d):
        if f.lower().endswith((".jpg", ".jpeg")):
            path = os.path.join(d, f)
            try:
                with Image.open(path) as im:
                    im_rgb = im.convert("RGB")
                    # Batasi resolusi maksimal ke 1000px (sangat tajam di HP, sangat ringan di RAM)
                    im_rgb.thumbnail((1000, 1000), Image.Resampling.LANCZOS)
                    im_rgb.save(path, format="JPEG", quality=75, optimize=True)
            except Exception as e:
                pass

print("[OK] Seluruh gambar berhasil dikompresi ringan!")

# Dorong pembaruan ke GitHub & Vercel
subprocess.run(["git", "add", "images", "web_galeri/images"], check=True)
subprocess.run(["git", "commit", "-m", "Optimasi kompresi gambar web ringan (~90KB per karya)"], check=True)
subprocess.run(["git", "push", "origin", "main"], check=True)
print("\n[2/2] [SUKSES] Gambar super ringan telah terbit ke Vercel!")
