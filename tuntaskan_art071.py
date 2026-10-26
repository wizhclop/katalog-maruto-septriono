import os
import json
import shutil
import re
import subprocess
from PIL import Image

BASE_DIR = r"F:\DATABASE_AI ART\ART"
CATALOG_PATH = os.path.join(BASE_DIR, "art_catalog.json")
SOURCE_IMG_DIR = os.path.join(BASE_DIR, "ART_70")
OUTPUT_IMG_DIR = os.path.join(BASE_DIR, "web_galeri", "images")

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

def main():
    print("==================================================")
    print("  MENUNTASKAN KARTU TERAKHIR: ART-071             ")
    print("==================================================")

    if not os.path.exists(CATALOG_PATH):
        print("ERROR: art_catalog.json tidak ada!")
        return

    with open(CATALOG_PATH, "r", encoding="utf-8-sig") as f:
        catalog = json.load(f)

    repo_dir = find_repo_folder()
    repo_img_dir = os.path.join(repo_dir, "images") if repo_dir else None

    # Cari data ART-071 di katalog
    art71_item = None
    for it in catalog:
        if str(it.get("ID", "")).strip() == "ART-071" or str(it.get("id", "")).strip() == "ART-071":
            art71_item = it
            break

    all_raw_files = os.listdir(SOURCE_IMG_DIR) if os.path.exists(SOURCE_IMG_DIR) else []
    
    # Deteksi file fisik ART-071 (bisa ComfyUI_00175, 071, Kematian, dll.)
    matched_file = None
    if art71_item:
        old_fn = art71_item.get("Nama_File", "")
        if old_fn and os.path.exists(os.path.join(SOURCE_IMG_DIR, old_fn)):
            matched_file = old_fn

    if not matched_file:
        for f in all_raw_files:
            f_low = f.lower()
            if "071" in f_low or "comfyui_00175" in f_low or "menyatu" in f_low or "menyentuh" in f_low:
                matched_file = f
                break

    if matched_file:
        src_path = os.path.join(SOURCE_IMG_DIR, matched_file)
        print(f"[OK] Berkas asli ART-071 ditemukan: {matched_file}")
        
        # Konversi dan kompres ke format ART-071.jpg & ART-71.jpg
        for target_name in ["ART-071.jpg", "ART-71.jpg"]:
            dst_local = os.path.join(OUTPUT_IMG_DIR, target_name)
            try:
                with Image.open(src_path) as img:
                    img = img.convert("RGB")
                    img.thumbnail((1200, 1200), Image.Resampling.LANCZOS)
                    img.save(dst_local, format="JPEG", quality=82, optimize=True)
            except Exception:
                shutil.copy2(src_path, dst_local)

            if repo_img_dir:
                shutil.copy2(dst_local, os.path.join(repo_img_dir, target_name))
        
        print("[OK] Gambar ART-071.jpg & ART-71.jpg berhasil disiapkan di folder repositori.")
    else:
        print("[PERINGATAN] File fisik ART-071 tidak terdeteksi otomatis di ART_70.")

    # Dorong pembaruan ke GitHub & Vercel
    if repo_dir:
        print("\n[>>] Mendorong pembaruan berkas ART-071 ke GitHub & Vercel...")
        try:
            subprocess.run(["git", "add", "-A"], cwd=repo_dir, check=True)
            subprocess.run(["git", "commit", "-m", "Lengkapi gambar ART-071 untuk Blogspot & Vercel"], cwd=repo_dir, check=True)
            subprocess.run(["git", "push", "origin", "main"], cwd=repo_dir, check=True)
            print("\n==================================================")
            print("  [BERHASIL 100%] KARTU TERAKHIR SUDAH TERBIT!    ")
            print("==================================================")
        except Exception as e:
            print(f"[!] Info Git: {e}")

if __name__ == "__main__":
    main()
