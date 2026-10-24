import os
import json
import re
import tempfile
import shutil
import piexif
from PIL import Image, PngImagePlugin

BASE_DIR = r"F:\DATABASE_AI ART\ART"
CATALOG_PATH = os.path.join(BASE_DIR, "art_catalog.json")
IMG_DIR = os.path.join(BASE_DIR, "ART_70")

ARTIST_NAME = "Maruto Septriono"
COPYRIGHT_NOTICE = "© 2026 Maruto Septriono. All Rights Reserved. Official Portfolio: http://wizhclop.github.io/katalog-maruto-septriono"

def inject_metadata():
    print("==================================================")
    print("  INJEKSI METADATA IPTC / EXIF KE BERKAS GAMBAR   ")
    print("==================================================")

    if not os.path.exists(CATALOG_PATH):
        print("ERROR: art_catalog.json tidak ditemukan!")
        return

    with open(CATALOG_PATH, "r", encoding="utf-8-sig") as f:
        catalog = json.load(f)

    all_files = os.listdir(IMG_DIR)
    success_count = 0
    fail_count = 0

    for idx, item in enumerate(catalog, 1):
        art_id = item.get("ID") or item.get("id") or f"ART-{idx:03d}"
        title = item.get("Judul") or item.get("judul") or "Tanpa Judul"
        statement = item.get("artist_statement_id") or ""
        curatorial = item.get("deskripsi_kuratorial") or ""
        tags = item.get("tags") or "art, drawing, darkart, surealisgothic, gothic, indonesia"
        filename = item.get("Nama_File") or item.get("file") or ""

        # Cari berkas gambar yang cocok di ART_70
        matched_file = None
        if filename and os.path.exists(os.path.join(IMG_DIR, filename)):
            matched_file = filename
        else:
            clean_id_num = re.search(r"(\d+)", art_id)
            if clean_id_num:
                target_token = f"ART-{int(clean_id_num.group(1)):03d}"
                for f in all_files:
                    if target_token.lower() in f.lower():
                        matched_file = f
                        break

        if not matched_file:
            print(f"[{art_id}] Berkas gambar tidak ditemukan di ART_70.")
            fail_count += 1
            continue

        img_path = os.path.join(IMG_DIR, matched_file)
        ext = os.path.splitext(matched_file)[1].lower()

        # Deskripsi lengkap untuk IPTC Caption / Description
        full_desc = f"{statement}\n\nCatatan Kuratorial:\n{curatorial}\n\nKode Arsip: {art_id}"
        # Batasi panjang string aman untuk segmen JPEG header (~1500 char)
        safe_desc = full_desc[:1500]
        safe_keywords = tags[:1000]

        try:
            if ext in [".jpg", ".jpeg"]:
                im = Image.open(img_path)
                im_rgb = im.convert("RGB")
                
                # Baca atau inisialisasi struktur EXIF
                exif_dict = {"0th": {}, "Exif": {}, "GPS": {}, "1st": {}, "thumbnail": None}
                if "exif" in im.info:
                    try:
                        exif_dict = piexif.load(im.info["exif"])
                    except Exception:
                        pass

                # Suntikkan tag standar industri stok & metadata Windows/Photoshop
                exif_dict["0th"][piexif.ImageIFD.Artist] = ARTIST_NAME.encode("utf-8", errors="ignore")
                exif_dict["0th"][piexif.ImageIFD.Copyright] = COPYRIGHT_NOTICE.encode("utf-8", errors="ignore")
                exif_dict["0th"][piexif.ImageIFD.ImageDescription] = safe_desc.encode("utf-8", errors="ignore")
                exif_dict["0th"][piexif.ImageIFD.XPTitle] = title.encode("utf-16le", errors="ignore")
                exif_dict["0th"][piexif.ImageIFD.XPAuthor] = ARTIST_NAME.encode("utf-16le", errors="ignore")
                exif_dict["0th"][piexif.ImageIFD.XPKeywords] = safe_keywords.encode("utf-16le", errors="ignore")
                exif_dict["0th"][piexif.ImageIFD.XPComment] = statement[:500].encode("utf-16le", errors="ignore")

                exif_bytes = piexif.dump(exif_dict)

                # Penulisan aman via file sementara (menghindari lock file)
                fd, tmp_file = tempfile.mkstemp(suffix=".jpg")
                os.close(fd)
                im_rgb.save(tmp_file, format="JPEG", quality=95, exif=exif_bytes)
                im.close()
                im_rgb.close()

                shutil.move(tmp_file, img_path)
                success_count += 1
                print(f"[OK] {art_id} (JPG): {title}")

            elif ext == ".png":
                im = Image.open(img_path)
                meta = PngImagePlugin.PngInfo()
                meta.add_text("Title", title)
                meta.add_text("Author", ARTIST_NAME)
                meta.add_text("Copyright", COPYRIGHT_NOTICE)
                meta.add_text("Description", safe_desc)
                meta.add_text("Comment", statement)
                meta.add_text("Keywords", safe_keywords)

                fd, tmp_file = tempfile.mkstemp(suffix=".png")
                os.close(fd)
                im.save(tmp_file, format="PNG", pnginfo=meta)
                im.close()

                shutil.move(tmp_file, img_path)
                success_count += 1
                print(f"[OK] {art_id} (PNG): {title}")

        except Exception as e:
            print(f"[GAGAL] {art_id} ({matched_file}): {e}")
            fail_count += 1

    print("--------------------------------------------------")
    print(f"SELESAI! Berhasil menyuntik metadata ke {success_count} gambar.")
    if fail_count > 0:
        print(f"Perhatian: {fail_count} berkas dilewati/gagal.")

if __name__ == "__main__":
    inject_metadata()
