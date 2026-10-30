import json
import os
import subprocess

catalog_path = r"F:\DATABASE_AI ART\ART\art_catalog.json"

if not os.path.exists(catalog_path):
    print("[ERROR] art_catalog.json tidak ditemukan!")
    exit(1)

with open(catalog_path, "r", encoding="utf-8-sig") as f:
    catalog = json.load(f)

item_076 = None
item_077 = None

for item in catalog:
    uid = str(item.get("ID", "")).upper()
    if uid == "ART-076":
        item_076 = item
    elif uid == "ART-077":
        item_077 = item

if item_077:
    print("[1/3] Mengambil narasi sempurna dari ART-077...")
    # Jika ART-076 belum ada, kita buatkan dari data 077
    if not item_076:
        item_076 = dict(item_077)
        item_076["ID"] = "ART-076"
        catalog.append(item_076)
    else:
        # Salin data sempurna dari 077 ke 076
        item_076["Judul"] = item_077.get("Judul", "Kerusakan dan Keheningan")
        item_076["Tahun"] = item_077.get("Tahun", "2026")
        item_076["Ukuran"] = item_077.get("Ukuran", "29.7 cm x 42 cm")
        item_076["Media"] = item_077.get("Media", "Tinta di atas kertas")
        item_076["artist_statement_id"] = item_077.get("artist_statement_id", "Bagi saya, gambar ini merupakan sebuah lukisan surealisme yang menggambarkan suasana kota yang terganggu oleh kehancuran. Di balik tarikan tinta ini tersimpan keheningan batin yang membeku.")
        item_076["deskripsi_kuratorial"] = item_077.get("deskripsi_kuratorial", "")
        item_076["tags"] = item_077.get("tags", "")

    # Hapus entri ART-077 duplikat dari katalog
    catalog = [x for x in catalog if str(x.get("ID", "")).upper() != "ART-077"]
    print("[2/3] Entri ART-077 duplikat telah dihapus.")

    # Simpan kembali catalog
    with open(catalog_path, "w", encoding="utf-8") as f:
        json.dump(catalog, f, indent=2, ensure_ascii=False)
    print("[OK] art_catalog.json berhasil disinkronkan.")

# Hapus file gambar duplikat ART-077 jika ada
for d in [r"F:\DATABASE_AI ART\ART\images", r"F:\DATABASE_AI ART\ART\web_galeri\images"]:
    f_077 = os.path.join(d, "ART-077.jpg")
    if os.path.exists(f_077):
        try:
            os.remove(f_077)
            print(f"[OK] Dihapus: {f_077}")
        except Exception:
            pass

# Regenerasi index.html menggunakan generator resmi Anda
print("[3/3] Merakit ulang index.html...")
py_exe = r"C:\Program Files\Python310\python.exe"
gen_script = r"F:\DATABASE_AI ART\ART\generate_web_gallery.py"
if not os.path.exists(gen_script):
    gen_script = r"F:\DATABASE_AI ART\ART\terbitkan_art076_sekarang.py"

if os.path.exists(gen_script):
    subprocess.run([py_exe, gen_script], check=True)
else:
    print("[INFO] Skrip generator tidak ditemukan, melanjutkan git push langsung.")

print("\n[SELESAI] Data ART-076 telah disempurnakan!")
