import json
import os
import re

catalog_path = "art_catalog.json"

if not os.path.exists(catalog_path):
    print(f"ERROR: art_catalog.json tidak ditemukan di {os.getcwd()}")
    exit()

# Buka dengan utf-8-sig agar aman dari karakter BOM
with open(catalog_path, "r", encoding="utf-8-sig") as f:
    karya_list = json.load(f)

output_file = "jadwal_promosi_medsos.txt"

with open(output_file, "w", encoding="utf-8") as out:
    out.write("============================================================\n")
    out.write("PANDUAN MATERI PROMOSI MEDSOS (INSTAGRAM, PINTEREST, BLOG)\n")
    out.write(f"Total Karya Terjadwal: {len(karya_list)} Karya\n")
    out.write("============================================================\n\n")
    
    for i, item in enumerate(karya_list, start=1):
        art_id = item.get("ID") or item.get("id") or f"ART-{i:03d}"
        judul = item.get("Judul") or item.get("judul") or "Tanpa Judul"
        tahun = item.get("Tahun") or item.get("tahun") or "-"
        ukuran = item.get("Ukuran") or item.get("ukuran") or "-"
        media = item.get("Media") or item.get("media") or "-"
        kuratorial = item.get("deskripsi_kuratorial") or ""
        
        # Buat Artist Statement otomatis dari kuratorial agar tidak ada tanda petik kosong
        statement = item.get("artist_statement_id")
        if not statement or statement.strip() == "":
            if kuratorial:
                kalimat = [k.strip() for k in re.split(r'[.!?]', kuratorial) if len(k.strip()) > 20]
                statement = kalimat[0] + "." if kalimat else f"Eksplorasi garis dan medium {media.lower()} yang merefleksikan dinamika batin dan ruang personal."
            else:
                statement = f"Eksplorasi garis dan medium {media.lower()} yang merefleksikan dinamika batin dan ruang personal."
        
        tags = item.get("tags") or "art, sketch, drawing, indonesia"
        hashtag_list = " ".join(["#" + t.strip().replace(" ", "") for t in tags.split(",") if t.strip()])
        if "#inkdrawing" not in hashtag_list:
            hashtag_list += " #indonesianartist #contemporaryart #artcollector #darkart #marutoseptriono"
        
        out.write(f"--- [POSTING #{i:02d}] {art_id} - {judul} ({tahun}) ---\n\n")
        out.write(f'"{statement}"\n\n')
        out.write(f"Karya  : {judul} ({tahun})\n")
        out.write(f"Media  : {media}\n")
        out.write(f"Ukuran : {ukuran}\n\n")
        if kuratorial:
            out.write(f"Catatan Kuratorial:\n{kuratorial}\n\n")
        out.write("Status Koleksi & Lisensi:\n")
        out.write("✔ High-Res Soft File (Lisensi Komersial)\n")
        out.write("✔ Lisensi Cetak (Print License)\n\n")
        out.write("Katalog resmi & inquiry lisensi:\n")
        out.write("https://wizhclop.github.io/katalog-maruto-septriono/\n\n")
        out.write(f"Tagar:\n{hashtag_list}\n\n")
        out.write("="*60 + "\n\n")

print(f"SUKSES: Seluruh {len(karya_list)} karya lengkap berhasil dirapikan di '{output_file}'!")
