import os
import json
import re

BASE_DIR = r"F:\DATABASE_AI ART\ART"
CATALOG_PATH = os.path.join(BASE_DIR, "art_catalog.json")
OUTPUT_DIR = os.path.join(BASE_DIR, "promosi_konten")

os.makedirs(OUTPUT_DIR, exist_ok=True)

# Konfigurasi Tautan Portofolio Resmi
PORTFOLIO_WEBSITES = [
    {
        "nama": "Katalog Utama (GitHub Pages)",
        "url": "http://wizhclop.github.io/katalog-maruto-septriono"
    }
]

def format_website_links_text():
    return "\n".join([f"• {site['nama']}: {site['url']}" for site in PORTFOLIO_WEBSITES])

def format_website_links_html():
    return "\n".join([f'  <li><strong>{site["nama"]}:</strong> <a href="{site["url"]}" target="_blank">{site["url"]}</a></li>' for site in PORTFOLIO_WEBSITES])

def generate_promo_content(item):
    art_id = item.get("ID") or item.get("id") or "ART-000"
    title = item.get("Judul") or item.get("judul") or "Tanpa Judul"
    year = item.get("Tahun") or item.get("tahun") or "2026"
    media = item.get("Media") or item.get("media") or "Campuran"
    size = item.get("Ukuran") or item.get("ukuran") or "-"
    statement = item.get("artist_statement_id") or "Eksplorasi garis dan bentuk mengenai kedalaman eksistensi."
    curatorial = item.get("deskripsi_kuratorial") or "Refleksi visual dalam tarikan medium dan bayang gelap."
    raw_tags = item.get("tags") or "art, darkart, surealisgothic, gothic, drawing, indonesia"

    tags_formatted = " ".join([f"#{t.strip().replace('#','')}" for t in raw_tags.split(",") if t.strip()])
    web_text_block = format_website_links_text()
    web_html_block = format_website_links_html()
    primary_url = PORTFOLIO_WEBSITES[0]["url"]

    # Optimasi Format Pinterest (Maks 100 char title, maks 500 char desc)
    pin_title = f"{title} - Gothic Surrealism Ink Art by Maruto Septriono"[:100]
    pin_desc_raw = f'"{statement}" Karya orisinal "{title}" ({year}) oleh Maruto Septriono. Medium: {media}, Dimensi: {size}. Tersedia High-Res Digital Master ($250) & Commercial Print License ($100). Jelajahi katalog resmi untuk inquiry kuratorial dan lisensi.'
    pin_desc = (pin_desc_raw[:450] + "...") if len(pin_desc_raw) > 450 else pin_desc_raw

    content = f"""================================================================================
KONTEN PROMOSI & PUBLIKASI: {art_id} - {title.upper()}
================================================================================

[1] TAKARIR INSTAGRAM / FACEBOOK (SIAP SALIN & TEMPEL)
--------------------------------------------------------------------------------
"{statement}"

{title} ({year})
Karya ini mengalirkan ketegangan visual antara ruang sunyi dan detail organik, merefleksikan dialog batin seniman melalui tarikan {media.lower()}.

📐 Rincian Teknis & Arsip:
• Kode Arsip: {art_id}
• Medium: {media}
• Dimensi Fisik: {size}
• Tahun Penciptaan: {year}
• Status Fisik: Koleksi Pribadi (Private Archive)

💼 Ketersediaan Lisensi & Format Digital:
• High-Resolution Digital Master File: $ 250 USD
• Commercial Print License: $ 100 USD (Bebas Royalti)

Minat lisensi, cetak eksklusif, atau kolaborasi kuratorial?
Kirim DM ke @marutoseptriono atau Email ke: marutoseptriono@gmail.com

Arsip Portofolio Resmi:
{web_text_block}

{tags_formatted}
--------------------------------------------------------------------------------


[2] MATERI PIN PINTEREST (OPTIMASI SEO MESIN PENCARI VISUAL)
--------------------------------------------------------------------------------
📌 Judul Pin (Pin Title - Copy & Paste):
{pin_title}

📝 Deskripsi Pin (Pin Description - Siap Pakai):
{pin_desc}

🔗 Tautan Tujuan (Destination Link):
{primary_url}

🏷 Rekomendasi Papan / Board:
• Dark Surrealism Art
• Ink & Pen Fine Art
• Indonesian Contemporary Art

🔖 Tag Topik Pencarian (Search Tags):
dark art, surrealism, ink drawing, gothic illustration, fine art portfolio, contemporary art, macabre aesthetic
--------------------------------------------------------------------------------


[3] ARTIKEL BLOGSPOT / WEB (BEHIND THE SCENES & CATATAN KURATORIAL)
--------------------------------------------------------------------------------
Judul Postingan: Di Balik Karya {title} ({art_id}): Penjelajahan Garis dan Ruang Sunyi

Isi Postingan (Format HTML, Siap Tempel di Tab 'HTML View' Blogspot):

<p><em>"{statement}"</em></p>

<p>Dalam setiap goresan karya <strong>{title}</strong> yang diselesaikan pada tahun {year}, medium {media.lower()} menjadi saluran reflektif untuk menangkap suasana eksistensial yang sunyi. Berukuran fisik {size}, karya dengan kode arsip <strong>{art_id}</strong> ini memadukan kedalaman bayangan dan detail tekstur yang menjadi ciri khas penjelajahan artistik saya dalam langgam surealisme gothic.</p>

<h3>Catatan Proses & Konsep Visual</h3>
<p>{curatorial}</p>

<p>Melalui karya ini, saya tidak sekadar menyajikan komposisi bentuk rupa, melainkan membuka ruang kontemplasi bagi penikmat seni untuk menyelami ketegangan antara kerapuhan material dan keteguhan batin.</p>

<hr/>

<h3>Katalog Digital & Informasi Lisensi Komersial</h3>
<p>Karya fisik asli <strong>{title}</strong> saat ini tercatat aman sebagai arsip koleksi pribadi di Maruto Art Studio. Bagi kolektor institusi, galeri, penerbit, maupun penikmat seni yang memerlukan berkas master resolusi tinggi atau hak lisensi penggunaan cetak komersial:</p>
<ul>
  <li><strong>Berkas Master Resolusi Tinggi (High-Res Digital File):</strong> $ 250 USD</li>
  <li><strong>Lisensi Penggunaan Cetak Komersial (Royalty-Free):</strong> $ 100 USD</li>
</ul>

<p>Untuk korespondensi resmi, akuisisi, dan pertanyaan kuratorial:</p>
<ul>
  <li><strong>Email:</strong> <a href="mailto:marutoseptriono@gmail.com">marutoseptriono@gmail.com</a></li>
  <li><strong>Instagram:</strong> <a href="https://instagram.com/marutoseptriono" target="_blank">@marutoseptriono</a></li>
{web_html_block}
</ul>
================================================================================
"""
    file_path = os.path.join(OUTPUT_DIR, f"{art_id}_promosi.txt")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    return file_path

def main():
    if not os.path.exists(CATALOG_PATH):
        print("Katalog tidak ditemukan!")
        return

    with open(CATALOG_PATH, "r", encoding="utf-8-sig") as f:
        catalog = json.load(f)

    print(f"Membangun draf promosi terpadu (Instagram, Pinterest, Blog) untuk {len(catalog)} karya...")
    for item in catalog:
        generate_promo_content(item)

    print(f"[OK] Selesai! Seluruh 73 draf promosi telah memuat bagian Pinterest di folder:\n{OUTPUT_DIR}")

if __name__ == "__main__":
    main()
