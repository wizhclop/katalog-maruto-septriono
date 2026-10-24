import os
import time
import json
import base64
import re
from io import BytesIO
from PIL import Image
import requests

WATCH_DIR = r"F:\DATABASE_AI ART\ART\ART_70"
CATALOG_PATH = r"F:\DATABASE_AI ART\ART\art_catalog.json"
LM_STUDIO_URL = "http://localhost:1234/v1/chat/completions"

os.makedirs(WATCH_DIR, exist_ok=True)

def safe_save_catalog(data, target_path):
    """Menulis ke berkas sementara terlebih dahulu agar art_catalog.json tidak korup saat Ctrl+C"""
    temp_path = target_path + ".tmp"
    with open(temp_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    os.replace(temp_path, target_path)

def encode_and_resize_image(image_path, max_dim=1024):
    with Image.open(image_path) as img:
        img = img.convert("RGB")
        img.thumbnail((max_dim, max_dim), Image.Resampling.LANCZOS)
        buffered = BytesIO()
        img.save(buffered, format="JPEG", quality=85)
        return base64.b64encode(buffered.getvalue()).decode("utf-8")

def get_next_art_id(catalog_data):
    max_id = 0
    for item in catalog_data:
        raw_id = item.get("ID") or item.get("id") or ""
        match = re.search(r"(\d+)", raw_id)
        if match:
            num = int(match.group(1))
            if num > max_id:
                max_id = num
    return f"ART-{max_id + 1:03d}"

def analyze_with_local_ai(base64_image):
    prompt_text = (
        "Analisis karya seni ini secara mendalam sebagai kurator dan arsiparis profesional. "
        "Kembalikan jawaban HANYA dalam format JSON valid tanpa teks pengantar atau markdown lainnya. "
        "Struktur JSON yang wajib:\n"
        "{\n"
        '  "Judul": "Judul puitis/filosofis yang sesuai",\n'
        '  "Tahun": "2026",\n'
        '  "Media": "Tinta di atas kertas / Akrilik di kanvas / Conte / AI Generated",\n'
        '  "Ukuran": "29.7 cm x 42 cm",\n'
        '  "artist_statement_id": "1-2 kalimat refleksi personal dan esensi filosofis karya.",\n'
        '  "deskripsi_kuratorial": "Catatan kuratorial mengenai teknik arsir, komposisi visual, dan makna karya.",\n'
        '  "tags": "art, sketch, drawing, indonesia, darkart, contemporaryart"\n'
        "}"
    )

    payload = {
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt_text},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                ]
            }
        ],
        "temperature": 0.4,
        "max_tokens": 800
    }

    response = requests.post(LM_STUDIO_URL, json=payload, timeout=120)
    response.raise_for_status()
    raw_content = response.json()["choices"][0]["message"]["content"].strip()
    
    if "```" in raw_content:
        raw_content = re.sub(r"```(?:json)?", "", raw_content).strip()
    
    return json.loads(raw_content)

def main():
    print("==================================================")
    print("  ASISTEN AI LOKAL: PENGAWAS FOLDER AKTIF")
    print(f"  Memantau folder : {WATCH_DIR}")
    print(f"  Target database : {CATALOG_PATH}")
    print("==================================================")

    # 1. Baca katalog awal
    if os.path.exists(CATALOG_PATH):
        with open(CATALOG_PATH, "r", encoding="utf-8-sig") as f:
            catalog = json.load(f)
    else:
        catalog = []

    # 2. Catat seluruh nama berkas lama
    processed_files = set()
    for item in catalog:
        f_name = item.get("Nama_File") or item.get("file") or item.get("filename")
        if f_name:
            processed_files.add(f_name.strip())

    # 3. Kunci seluruh file yang saat ini sudah berada di folder ART_70
    existing_files = [
        f for f in os.listdir(WATCH_DIR)
        if f.lower().endswith((".jpg", ".jpeg", ".png"))
    ]
    for f in existing_files:
        processed_files.add(f)

    print(f"[*] Database aktif: {len(catalog)} karya.")
    print(f"[*] Mengunci {len(processed_files)} berkas agar tidak diproses ulang.")
    print("  Status: Siaga. Masukkan gambar karya baru ke folder ART_70...")
    print("  Tekan Ctrl+C kapan saja untuk berhenti dengan aman.")
    print("==================================================")

    while True:
        try:
            current_files = [
                f for f in os.listdir(WATCH_DIR)
                if f.lower().endswith((".jpg", ".jpeg", ".png"))
            ]

            for file_name in current_files:
                if file_name not in processed_files:
                    file_path = os.path.join(WATCH_DIR, file_name)
                    print(f"\n[+] Karya BARU terdeteksi: {file_name}")
                    print("    Mengoptimalkan gambar & memanggil AI Lokal...")

                    try:
                        b64_img = encode_and_resize_image(file_path)
                        ai_result = analyze_with_local_ai(b64_img)

                        new_id = get_next_art_id(catalog)
                        new_entry = {
                            "ID": new_id,
                            "Judul": ai_result.get("Judul", "Tanpa Judul"),
                            "Tahun": ai_result.get("Tahun", "2026"),
                            "Ukuran": ai_result.get("Ukuran", "-"),
                            "Media": ai_result.get("Media", "-"),
                            "Nama_File": file_name,
                            "artist_statement_id": ai_result.get("artist_statement_id", ""),
                            "deskripsi_kuratorial": ai_result.get("deskripsi_kuratorial", ""),
                            "tags": ai_result.get("tags", "art, sketch, drawing, indonesia")
                        }

                        catalog.append(new_entry)
                        safe_save_catalog(catalog, CATALOG_PATH)
                        processed_files.add(file_name)

                        print("--------------------------------------------------")
                        print(f"  BERHASIL: {new_id} - {new_entry['Judul']}")
                        print(f"  Media     : {new_entry['Media']}")
                        print(f"  Statement : {new_entry['artist_statement_id']}")
                        print("  Status    : Tersimpan aman di art_catalog.json")
                        print("--------------------------------------------------")

                    except Exception as err:
                        print(f"  [!] Gagal memproses {file_name}: {err}")
                        processed_files.add(file_name)

            time.sleep(3)

        except KeyboardInterrupt:
            print("\nPengawas folder dinonaktifkan dengan aman.")
            break
        except Exception as e:
            print(f"Terjadi kesalahan loop: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
