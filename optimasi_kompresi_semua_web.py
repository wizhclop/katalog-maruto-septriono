import os
import json
import shutil
import re
import subprocess
from PIL import Image

BASE_DIR = r"F:\DATABASE_AI ART\ART"
CATALOG_PATH = os.path.join(BASE_DIR, "art_catalog.json")
SOURCE_IMG_DIR = os.path.join(BASE_DIR, "ART_70")
OUTPUT_DIR = os.path.join(BASE_DIR, "web_galeri")
OUTPUT_IMG_DIR = os.path.join(OUTPUT_DIR, "images")

os.makedirs(OUTPUT_IMG_DIR, exist_ok=True)

def find_repo_folder():
    for d in [r"C:\Users", r"F:\\"]:
        if os.path.exists(d):
            for root, dirs, files in os.walk(d):
                if ".git" in dirs:
                    git_cfg = os.path.join(root, ".git", "config")
                    if os.path.exists(git_cfg):
                        try:
                            with open(git_cfg, "r", encoding="utf-8", errors="ignore") as f:
                                if "katalog-maruto-septriono" in f.read():
                                    return root
                        except Exception:
                            pass
    return None

def compress_image(src_path, dst_path, max_dim=1400, quality=85):
    try:
        with Image.open(src_path) as img:
            img = img.convert("RGB")
            img.thumbnail((max_dim, max_dim), Image.Resampling.LANCZOS)
            img.save(dst_path, format="JPEG", quality=quality, optimize=True)
        return True
    except Exception as e:
        shutil.copy2(src_path, dst_path)
        return False

def main():
    print("==================================================")
    print("  OPTIMASI & KOMPRESI WEB OTOMATIS (75 KARYA)     ")
    print("==================================================")

    if not os.path.exists(CATALOG_PATH):
        print("ERROR: art_catalog.json tidak ditemukan!")
        return

    with open(CATALOG_PATH, "r", encoding="utf-8-sig") as f:
        catalog = json.load(f)

    repo_dir = find_repo_folder()
    repo_img_dir = os.path.join(repo_dir, "images") if repo_dir else None
    if repo_img_dir:
        os.makedirs(repo_img_dir, exist_ok=True)

    all_raw_files = os.listdir(SOURCE_IMG_DIR) if os.path.exists(SOURCE_IMG_DIR) else []
    print(f"[INFO] Memproses kompresi tajam untuk {len(catalog)} karya dari folder ART_70...")

    success_count = 0

    for item in catalog:
        art_id = item.get("ID") or item.get("id") or "ART"
        title = item.get("Judul") or item.get("judul") or ""
        fn = item.get("Nama_File") or ""

        # Cari file asli di folder ART_70
        matched_file = None
        if fn and os.path.exists(os.path.join(SOURCE_IMG_DIR, fn)):
            matched_file = fn

        if not matched_file:
            num_match = re.search(r"(\d+)", art_id)
            if num_match:
                n = int(num_match.group(1))
                patterns = [
                    re.compile(rf"(?:^|[^\d]){n:03d}(?:[^\d]|$)", re.IGNORECASE),
                    re.compile(rf"(?:^|[^\d]){n:02d}(?:[^\d]|$)", re.IGNORECASE),
                    re.compile(rf"(?:^|[^\d]){n}(?:[^\d]|$)", re.IGNORECASE)
                ]
                for f in all_raw_files:
                    if any(p.search(f) for p in patterns):
                        matched_file = f
                        break

        if not matched_file and len(title) > 3:
            clean_t = re.sub(r'[^a-zA-Z0-9]', '', title).lower()
            for f in all_raw_files:
                if clean_t[:6] in re.sub(r'[^a-zA-Z0-9]', '', f).lower():
                    matched_file = f
                    break

        clean_num = re.search(r"(\d+)", art_id)
        n_int = int(clean_num.group(1)) if clean_num else 0

        # Varian nama file yang akan dibuat
        name_3d = f"ART-{n_int:03d}.jpg"
        name_2d = f"ART-{n_int:02d}.jpg"
        name_raw = f"ART-{n_int}.jpg"

        if matched_file:
            src_file = os.path.join(SOURCE_IMG_DIR, matched_file)
            
            # Kompres ke berkas utama di web_galeri/images
            dst_master = os.path.join(OUTPUT_IMG_DIR, name_3d)
            compress_image(src_file, dst_master)

            # Buat duplikasi ringan 2 digit & raw di web_galeri
            for alt_name in [name_2d, name_raw]:
                alt_path = os.path.join(OUTPUT_IMG_DIR, alt_name)
                if not os.path.exists(alt_path):
                    shutil.copy2(dst_master, alt_path)

            # Salin ke repo Git lokal untuk GitHub Pages & Vercel
            if repo_img_dir:
                for target_name in [name_3d, name_2d, name_raw]:
                    shutil.copy2(dst_master, os.path.join(repo_img_dir, target_name))

            success_count += 1

    print(f"\n[OK] Sukses mengompres {success_count} gambar ke resolusi web optimal!")

    # Kirim ke GitHub & Vercel
    if repo_dir:
        print("\n[>>] Mendorong seluruh gambar teroptimasi ke GitHub & Vercel...")
        try:
            subprocess.run(["git", "add", "images"], cwd=repo_dir, check=True)
            subprocess.run(["git", "commit", "-m", "Optimasi Web Otomatis (Kompresi Ringan 75 Gambar untuk GitHub & Vercel)"], cwd=repo_dir, check=True)
            subprocess.run(["git", "push", "origin", "main"], cwd=repo_dir, check=True)
            print("\n==================================================")
            print("  [BERHASIL] GITHUB PAGES & VERCEL KINI SUPER CEPAT!")
            print("==================================================")
        except Exception as e:
            print(f"[!] Info Git: {e}")

if __name__ == "__main__":
    main()
