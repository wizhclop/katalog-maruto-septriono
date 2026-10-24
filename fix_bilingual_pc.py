import json, os, urllib.parse

with open('art_catalog.json', 'r', encoding='utf-8') as f:
    items = json.load(f)

img_dir = 'ART_70'
all_images = os.listdir(img_dir)
cards_html = []

for item in items:
    id_karya = str(item.get('ID', '')).strip()
    judul = item.get('Judul', 'Tanpa Judul')
    tahun = item.get('Tahun', '-')
    ukuran = item.get('Ukuran', '-')
    media = item.get('Media', '-')
    statement = item.get('artist_statement', '')
    kuratorial = item.get('deskripsi_kuratorial', '')
    keywords = item.get('keywords', '')

    id_num = ''.join(filter(str.isdigit, id_karya))
    matched_img = None
    for img_file in all_images:
        if id_karya and id_karya in img_file:
            matched_img = img_file
            break
        elif id_num and f'ART-{id_num}' in img_file.replace(' ', ''):
            matched_img = img_file
            break
        elif id_num and f'-{id_num}' in img_file:
            matched_img = img_file
            break

    img_src = f'ART_70/{urllib.parse.quote(matched_img)}' if matched_img else ''

    # Encode data ke atribut HTML agar aman
    cards_html.append(f'''
    <div class=\"card\" data-title=\"{judul.lower()}\" data-media=\"{media.lower()}\">
        <div class=\"img-wrap\">
            <img src=\"{img_src}\" alt=\"{judul}\" loading=\"lazy\" />
        </div>
        <div class=\"card-content\">
            <div class=\"badge-row\">
                <span class=\"badge\">{id_karya}</span>
                <span class=\"badge\">{tahun}</span>
                <span class=\"badge-secondary lang-target\" data-id=\"Karya Asli: Tidak Dijual\" data-en=\"Original: Not For Sale\">Karya Asli: Tidak Dijual</span>
            </div>
            <h2>{judul}</h2>
            <p class=\"meta\"><strong>{ukuran}</strong> | <span class=\"media-text\">{media}</span></p>
            <div class=\"prices\">
                <div class=\"price-item\">
                    <small class=\"lang-target\" data-id=\"Soft File (High-Res)\" data-en=\"High-Res Soft File\">Soft File (High-Res)</small>
                    <span class=\"price-val\">$ 250</span>
                </div>
                <div class=\"price-item\">
                    <small class=\"lang-target\" data-id=\"Lisensi Cetak\" data-en=\"Print License\">Lisensi Cetak</small>
                    <span class=\"price-val\">$ 100</span>
                    <span class=\"shipping-tag lang-target\" data-id=\"Bebas Ongkos Kirim\" data-en=\"Free Shipping\">Bebas Ongkos Kirim</span>
                </div>
            </div>
            <p class=\"statement lang-trans\">\"{statement}\"</p>
            <details>
                <summary class=\"lang-target\" data-id=\"Catatan Kuratorial &amp; SEO\" data-en=\"Curatorial Notes &amp; SEO\">Catatan Kuratorial &amp; SEO</summary>
                <p class=\"kuratorial lang-trans\">{kuratorial}</p>
                <p class=\"tags\"><strong>Tags:</strong> {keywords}</p>
            </details>
        </div>
    </div>
    ''')

html_template = f'''<!DOCTYPE html>
<html lang=\"id\">
<head>
    <meta charset=\"UTF-8\">
    <title>Katalog Karya Maruto Septriono</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #0b1120; color: #f1f5f9; padding: 30px 20px; }}
        .top-bar {{ display: flex; justify-content: flex-end; max-width: 1350px; margin: 0 auto 15px auto; gap: 10px; align-items: center; }}
        .lang-switch {{ background: #1e293b; border: 1px solid #334155; border-radius: 20px; padding: 4px; display: inline-flex; }}
        .lang-btn {{ background: transparent; border: none; color: #94a3b8; padding: 6px 14px; border-radius: 16px; cursor: pointer; font-size: 0.85rem; font-weight: 600; transition: all 0.2s; }}
        .lang-btn.active {{ background: #0284c7; color: #fff; }}
        header {{ text-align: center; margin-bottom: 35px; }}
        header h1 {{ font-size: 2.5rem; color: #38bdf8; margin-bottom: 10px; font-weight: 700; }}
        header p {{ color: #94a3b8; font-size: 1.1rem; }}
        .search-box {{ max-width: 600px; margin: 25px auto 35px auto; }}
        .search-box input {{ width: 100%; padding: 14px 22px; border-radius: 30px; border: 1px solid #334155; background: #1e293b; color: #fff; font-size: 1rem; outline: none; }}
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
    <div class=\"top-bar\">
        <div class=\"lang-switch\">
            <button class=\"lang-btn active\" id=\"btn-id\" onclick=\"switchLang('id')\">ID (Indonesia)</button>
            <button class=\"lang-btn\" id=\"btn-en\" onclick=\"switchLang('en')\">EN (English)</button>
        </div>
    </div>

    <header>
        <h1 id=\"header-title\" class=\"lang-target\" data-id=\"Katalog Karya Maruto Septriono\" data-en=\"Maruto Septriono Art Catalog\">Katalog Karya Maruto Septriono</h1>
        <p id=\"header-sub\" class=\"lang-target\" data-id=\"Arsip Digital, Portofolio &amp; Etalase Komersial Internasional\" data-en=\"Digital Archive, Portfolio &amp; International Commercial Gallery\">Arsip Digital, Portofolio &amp; Etalase Komersial Internasional</p>
        <div class=\"search-box\">
            <input type=\"text\" id=\"searchInput\" placeholder=\"Cari judul karya atau medium...\" onkeyup=\"filterCards()\" />
        </div>
    </header>

    <div class=\"grid\" id=\"artGrid\">
        {''.join(cards_html)}
    </div>

    <script>
        // Kamus istilah seni rupa & kuratorial (ID -> EN)
        const artDictionary = [
            [/Tinta di atas kertas/gi, "Ink on paper"],
            [/Akrilik di atas kanvas/gi, "Acrylic on canvas"],
            [/Conte di atas kertas/gi, "Conte on paper"],
            [/Ballpoint di atas kertas/gi, "Ballpoint on paper"],
            [/Cat air di atas kertas/gi, "Watercolor on paper"],
            [/Dalam karya seni ini/gi, "In this artwork"],
            [/saya menggambarkan/gi, "I depict"],
            [/perjalanan spiritual/gi, "spiritual journey"],
            [/simbolisme dan makna filosofis/gi, "symbolism and philosophical meaning"],
            [/konflik antara kekuatan internal dan eksternal/gi, "the conflict between internal and external forces"],
            [/hubungan manusia dengan alam semesta/gi, "the human relationship with the universe"],
            [/menggunakan teknik/gi, "utilizes the technique of"],
            [/sketsa tinta hitam putih/gi, "black and white ink sketch"],
            [/sangat detail/gi, "highly detailed"],
            [/menciptakan suasana yang mendalam/gi, "creating a profound atmosphere"],
            [/Komposisi menggambarkan/gi, "The composition portrays"],
            [/seorang figur/gi, "a figure"],
            [/terhubung dengan elemen-elemen yang kompleks/gi, "connected with complex elements"],
            [/organisme dan struktur mekanis/gi, "organisms and mechanical structures"],
            [/Suasana yang ditampilkan/gi, "The mood presented"],
            [/konsisten dengan tema filosofis/gi, "consistent with the philosophical theme"],
            [/karya seni ini/gi, "this artwork"],
            [/karya seni/gi, "artwork"],
            [/penelitian visual/gi, "visual study"],
            [/menampilkan/gi, "features"],
            [/ekspresi/gi, "expression"]
        ];

        // Simpan teks asli saat pertama kali dimuat
        document.querySelectorAll('.lang-trans').forEach(el => {{
            el.setAttribute('data-original-id', el.innerHTML);
        }});

        function switchLang(lang) {{
            // 1. Ubah tombol & UI statis
            document.querySelectorAll('.lang-btn').forEach(b => b.classList.remove('active'));
            document.getElementById('btn-' + lang).classList.add('active');

            document.querySelectorAll('.lang-target').forEach(el => {{
                el.innerHTML = el.getAttribute('data-' + lang);
            }});

            const search = document.getElementById('searchInput');
            if (search) {{
                search.placeholder = lang === 'en' ? 'Search by artwork title or medium...' : 'Cari judul karya atau medium...';
            }}

            // 2. Terjemahkan teks kuratorial & statement secara instan
            document.querySelectorAll('.lang-trans').forEach(el => {{
                let originalText = el.getAttribute('data-original-id');
                if (lang === 'en') {{
                    let translated = originalText;
                    artDictionary.forEach(([pattern, replacement]) => {{
                        translated = translated.replace(pattern, replacement);
                    }});
                    el.innerHTML = translated;
                }} else {{
                    el.innerHTML = originalText;
                }}
            }});

            // 3. Terjemahkan istilah media
            document.querySelectorAll('.media-text').forEach(el => {{
                if (!el.getAttribute('data-orig-media')) {{
                    el.setAttribute('data-orig-media', el.innerText);
                }}
                let orig = el.getAttribute('data-orig-media');
                if (lang === 'en') {{
                    let t = orig;
                    artDictionary.forEach(([pattern, replacement]) => {{
                        t = t.replace(pattern, replacement);
                    }});
                    el.innerText = t;
                }} else {{
                    el.innerText = orig;
                }}
            }});
        }}

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

print('SELESAI! index.html kini menggunakan engine dwibahasa bawaan mandiri yang dijamin berjalan mulus di browser PC.')
