import json, os, urllib.parse

with open('art_catalog.json', 'r', encoding='utf-8') as f:
    items = json.load(f)

img_dir = 'ART_70'
all_images = os.listdir(img_dir)
cards_html = []

print(f'Membangun ulang antarmuka galeri untuk {len(items)} karya seni...')

for item in items:
    id_karya = str(item.get('ID', '')).strip()
    judul = item.get('Judul', 'Tanpa Judul')
    tahun = item.get('Tahun', '-')
    ukuran = item.get('Ukuran', '-')
    media = item.get('Media', '-')
    statement = item.get('artist_statement', '')
    kuratorial = item.get('deskripsi_kuratorial', '')
    keywords = item.get('keywords', '')

    # Ekstrak nomor angka ID (contoh ART-001 -> 001)
    id_num = ''.join(filter(str.isdigit, id_karya))

    # Logika pencocokan gambar yang fleksibel dan akurat
    matched_img = None
    for img_file in all_images:
        # Cek apakah ID lengkap ada di nama file, atau nomor ID ada di nama file
        if id_karya and id_karya in img_file:
            matched_img = img_file
            break
        elif id_num and f'ART-{id_num}' in img_file.replace(' ', ''):
            matched_img = img_file
            break
        elif id_num and f'-{id_num}' in img_file:
            matched_img = img_file
            break

    if matched_img:
        # Encode nama file agar karakter khusus/spasi terbaca lancar oleh browser
        encoded_img_name = urllib.parse.quote(matched_img)
        img_src = f'ART_70/{encoded_img_name}'
    else:
        img_src = ''

    cards_html.append(f'''
    <div class=\"card\" data-title=\"{judul.lower()}\" data-media=\"{media.lower()}\">
        <div class=\"img-wrap\">
            <img src=\"{img_src}\" alt=\"{judul}\" loading=\"lazy\" />
        </div>
        <div class=\"card-content\">
            <div class=\"badge-row\">
                <span class=\"badge\">{id_karya}</span>
                <span class=\"badge\">{tahun}</span>
                <span class=\"badge-secondary\">Original: Not For Sale</span>
            </div>
            <h2>{judul}</h2>
            <p class=\"meta\"><strong>{ukuran}</strong> | {media}</p>
            <div class=\"prices\">
                <div class=\"price-item\">
                    <small>Soft File (High-Res)</small>
                    <span class=\"price-val\">$ 250</span>
                </div>
                <div class=\"price-item\">
                    <small>Lisensi Cetak</small>
                    <span class=\"price-val\">$ 100</span>
                    <span class=\"shipping-tag\">Free Ongkir</span>
                </div>
            </div>
            <p class=\"statement\">\"{statement}\"</p>
            <details>
                <summary>Catatan Kuratorial & SEO</summary>
                <p class=\"kuratorial\">{kuratorial}</p>
                <p class=\"tags\"><strong>Tags:</strong> {keywords}</p>
            </details>
        </div>
    </div>
    ''')

html_template = f'''<!DOCTYPE html>
<html lang=\"id\">
<head>
    <meta charset=\"UTF-8\">
    <title>Katalog Koleksi Seni Rupa</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #0b1120; color: #f1f5f9; padding: 30px 20px; }}
        header {{ text-align: center; margin-bottom: 35px; }}
        header h1 {{ font-size: 2.4rem; color: #38bdf8; margin-bottom: 10px; }}
        header p {{ color: #94a3b8; font-size: 1.05rem; }}
        .search-box {{ max-width: 600px; margin: 20px auto 35px auto; }}
        .search-box input {{ width: 100%; padding: 14px 20px; border-radius: 30px; border: 1px solid #334155; background: #1e293b; color: #fff; font-size: 1rem; outline: none; }}
        .search-box input:focus {{ border-color: #38bdf8; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 25px; max-width: 1350px; margin: 0 auto; }}
        .card {{ background: #1e293b; border-radius: 12px; overflow: hidden; border: 1px solid #334155; display: flex; flex-direction: column; transition: transform 0.2s, border-color 0.2s; }}
        .card:hover {{ transform: translateY(-4px); border-color: #38bdf8; }}
        .img-wrap {{ width: 100%; height: 260px; background: #020617; overflow: hidden; display: flex; align-items: center; justify-content: center; }}
        .img-wrap img {{ max-width: 100%; max-height: 100%; object-fit: contain; }}
        .card-content {{ padding: 20px; flex-grow: 1; display: flex; flex-direction: column; }}
        .badge-row {{ margin-bottom: 10px; display: flex; gap: 6px; flex-wrap: wrap; }}
        .badge {{ background: #0284c7; color: #fff; padding: 3px 8px; border-radius: 6px; font-size: 0.72rem; font-weight: 600; }}
        .badge-secondary {{ background: #475569; color: #cbd5e1; padding: 3px 8px; border-radius: 6px; font-size: 0.72rem; }}
        h2 {{ margin: 4px 0 6px 0; font-size: 1.25rem; color: #f8fafc; }}
        .meta {{ color: #94a3b8; font-size: 0.85rem; margin-bottom: 15px; }}
        .prices {{ display: flex; justify-content: space-between; background: #0f172a; padding: 12px 14px; border-radius: 8px; margin-bottom: 14px; border: 1px solid #1e293b; }}
        .price-item {{ display: flex; flex-direction: column; }}
        .price-item small {{ color: #64748b; font-size: 0.75rem; margin-bottom: 2px; }}
        .price-val {{ font-size: 1.1rem; font-weight: bold; color: #38bdf8; }}
        .shipping-tag {{ font-size: 0.7rem; color: #10b981; font-weight: 600; margin-top: 2px; }}
        .statement {{ font-style: italic; font-size: 0.88rem; color: #cbd5e1; margin-bottom: 15px; line-height: 1.45; }}
        details {{ margin-top: auto; padding-top: 10px; border-top: 1px solid #334155; font-size: 0.82rem; color: #94a3b8; }}
        details summary {{ cursor: pointer; color: #38bdf8; margin-bottom: 8px; user-select: none; }}
        .kuratorial {{ margin-bottom: 8px; color: #e2e8f0; line-height: 1.4; }}
        .tags {{ font-size: 0.75rem; color: #64748b; word-break: break-word; }}
    </style>
</head>
<body>
    <header>
        <h1>Katalog Koleksi Seni Rupa</h1>
        <p>Arsip Digital, Portofolio &amp; Etalase Komersial Internasional</p>
        <div class=\"search-box\">
            <input type=\"text\" id=\"searchInput\" placeholder=\"Cari judul karya atau medium...\" onkeyup=\"filterCards()\" />
        </div>
    </header>
    <div class=\"grid\" id=\"artGrid\">
        {''.join(cards_html)}
    </div>
    <script>
        function filterCards() {{
            let input = document.getElementById('searchInput').value.toLowerCase();
            let cards = document.getElementsByClassName('card');
            for (let card of cards) {{
                let title = card.getAttribute('data-title');
                let media = card.getAttribute('data-media');
                if (title.includes(input) || media.includes(input)) {{
                    card.style.display = '';
                }} else {{
                    card.style.display = 'none';
                }}
            }}
        }}
    </script>
</body>
</html>'''

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html_template)

print('SELESAI! Tautan gambar telah disesuaikan dan index.html siap dibuka.')
