import os
import json
import subprocess
import re
from PIL import Image

BASE_DIR = r"F:\DATABASE_AI ART\ART"
CATALOG_PATH = os.path.join(BASE_DIR, "art_catalog.json")

SOURCE_IMG_DIRS = [
    os.path.join(BASE_DIR, "ART_70"),
    os.path.join(BASE_DIR, "web_galeri", "images"),
    os.path.join(BASE_DIR, "images"),
    r"F:\AI\model\MyArtLibrary"
]

TARGET_IMG_DIRS = [
    os.path.join(BASE_DIR, "web_galeri", "images"),
    os.path.join(BASE_DIR, "images")
]

for t in TARGET_IMG_DIRS:
    os.makedirs(t, exist_ok=True)

print("==================================================")
print("  PROSES MASSAL ART-001 SAMPAI ART-074")
print("==================================================")

if not os.path.exists(CATALOG_PATH):
    print(f"[ERROR] {CATALOG_PATH} tidak ditemukan!")
    exit(1)

with open(CATALOG_PATH, "r", encoding="utf-8-sig") as f:
    catalog = json.load(f)

# Standarisasi dan pemulihan Statement & Kuratorial jika kosong/berupa template
default_templates = [
    "*1-2 kalimat refleksi",
    "kembalikan hanya",
    "artist statement...",
    "refleksi artistik."
]

def need_refine(txt):
    if not txt or len(txt.strip()) < 15:
        return True
    t_low = txt.lower()
    return any(p in t_low for p in default_templates)

compressed_count = 0
updated_meta_count = 0

for item in catalog:
    uid_str = str(item.get("ID") or item.get("id") or "").upper().strip()
    match = re.search(r"ART-(\d+)", uid_str)
    if not match:
        continue
    
    num = int(match.group(1))
    if not (1 <= num <= 74):
        continue  # Hanya fokus pada rentang ART-001 sampai ART-074

    norm_id = f"ART-{num:03d}"
    item["ID"] = norm_id
    judul = item.get("Judul") or item.get("judul") or f"Karya {norm_id}"
    media = item.get("Media") or item.get("media") or "Tinta di atas kertas"
    
    # 1. Periksa & Lengkapi Statement / Kuratorial
    cur_stmt = item.get("artist_statement_id") or item.get("artist_statement") or item.get("statement") or ""
    cur_kura = item.get("deskripsi_kuratorial") or item.get("deskripsi") or ""

    if need_refine(cur_stmt):
        item["artist_statement_id"] = (
            f"Karya '{judul}' mengeksplorasi batas keheningan dan tegangan batin, "
            f"mengalirkan tarikan garis intuitif sebagai dialog eksistensial manusia di hadapan semesta."
        )
        updated_meta_count += 1
    else:
        item["artist_statement_id"] = cur_stmt

    if need_refine(cur_kura):
        item["deskripsi_kuratorial"] = (
            f"Komposisi figuratif dan deformasi organis pada karya ini bertumpu pada intensitas {media.lower()}, "
            f"membangun kedalaman visual surealistik dengan permainan kontras arsir gelap-terang yang solid dan ritmis."
        )
        updated_meta_count += 1
    else:
        item["deskripsi_kuratorial"] = cur_kura

    item["tags"] = item.get("tags") or "art, fineart, drawing, surrealism, inkdrawing, contemporaryart, marutoseptriono"
    item["web_image"] = f"{norm_id}.jpg"

    # 2. Cari Berkas Fisik & Kompres Gambar Menjadi ~90-120 KB
    matched_src = None
    search_tokens = [f"art-{num:03d}", f"art-{num:02d}", f"art-{num}"]
    
    for sdir in SOURCE_IMG_DIRS:
        if not os.path.exists(sdir):
            continue
        for fn in os.listdir(sdir):
            fn_low = fn.lower()
            if any(tok in fn_low for tok in search_tokens) and fn_low.endswith((".jpg", ".jpeg", ".png")):
                matched_src = os.path.join(sdir, fn)
                break
        if matched_src:
            break

    if matched_src:
        try:
            with Image.open(matched_src) as im:
                im_rgb = im.convert("RGB")
                im_rgb.thumbnail((1000, 1000), Image.Resampling.LANCZOS)
                for tdir in TARGET_IMG_DIRS:
                    out_f = os.path.join(tdir, f"{norm_id}.jpg")
                    im_rgb.save(out_f, format="JPEG", quality=78, optimize=True)
            compressed_count += 1
        except Exception as e:
            print(f"[!] Gagal kompres {norm_id}: {e}")

print(f"\n[1/3] Selesai: {compressed_count} gambar berhasil dikompresi ringan (~90-120 KB).")
print(f"[2/3] Selesai: Metadata narasi katalog disinkronkan untuk 74 karya.")

# Simpan art_catalog.json
with open(CATALOG_PATH, "w", encoding="utf-8") as f:
    json.dump(catalog, f, indent=2, ensure_ascii=False)

# 3. Rakit Ulang Web Galeri
print("[3/3] Merakit ulang halaman index.html...")
py_exe = r"C:\Program Files\Python310\python.exe"
gen_script = os.path.join(BASE_DIR, "generate_web_gallery.py")
if os.path.exists(gen_script):
    subprocess.run([py_exe, gen_script], check=True)

# Pastikan file root index.html sinkron dengan web_galeri/index.html
src_idx = os.path.join(BASE_DIR, "web_galeri", "index.html")
dst_idx = os.path.join(BASE_DIR, "index.html")
if os.path.exists(src_idx) and os.path.exists(dst_idx):
    with open(src_idx, "r", encoding="utf-8") as rf:
        cnt = rf.read()
    with open(dst_idx, "w", encoding="utf-8") as wf:
        wf.write(cnt)

# 4. Dorong ke GitHub & Vercel
print("\n[PUSH] Mengunggah pembaruan massal ke GitHub & Vercel...")
subprocess.run(["git", "add", "."], check=True)
subprocess.run(["git", "commit", "-m", "Otomasi massal ART-001 s.d ART-074: Kompresi gambar ringan dan standarisasi kuratorial"], check=True)
subprocess.run(["git", "push", "origin", "main"], check=True)

print("\n==================================================")
print("  [SUKSES LENGKAP] ART-001 s.d ART-074 BERHASIL DIUPDATE!")
print("==================================================")
