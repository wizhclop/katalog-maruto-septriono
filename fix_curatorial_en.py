import json, os, urllib.parse

with open('art_catalog.json', 'r', encoding='utf-8') as f:
    items = json.load(f)

img_dir = 'ART_70'
all_images = os.listdir(img_dir)
cards_html = []

dict_pairs = [
    ('Tinta di atas kertas', 'Ink on paper'),
    ('Akrilik di atas kanvas', 'Acrylic on canvas'),
    ('Akrilik di kanvas', 'Acrylic on canvas'),
    ('Conte di atas kertas', 'Conte on paper'),
    ('Ballpoint di atas kertas', 'Ballpoint on paper'),
    ('Cat air di atas kertas', 'Watercolor on paper'),
    ('Pen di atas kertas', 'Pen on paper'),
    ('Koleksi Pribadi (Tidak Dijual)', 'Private Collection (Not For Sale)'),
    ('Koleksi Pribadi', 'Private Collection'),
    ('Tersedia', 'Available'),
    ('Free Ongkos Kirim', 'Free Shipping')
]

def quick_en(text):
    t = str(text)
    for id_w, en_w in dict_pairs:
        t = t.replace(id_w, en_w)
    return t

print(f'Menyusun katalog dwibahasa presisi untuk {len(items)} karya...')

for idx, item in enumerate(items):
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

    cards_html.append(f'''
    <div class=\"card\" data-title=\"{judul.lower()}\" data-media=\"{media.lower()}\">
        <div class=\"img-wrap\">
            <img src=\"{img_src}\" alt=\"{judul}\" loading=\"lazy\" />
        </div>
        <div class=\"card-content\">
            <div class=\"badge-row\">
                <span class=\"badge\">{id_karya}</span>
                <span class=\"badge\">{tahun}</span>
                <span class=\"badge-secondary ui-not-for-sale\">Karya Asli: Tidak Dijual</span>
            </div>
            <h2>{judul}</h2>
            <p class=\"meta\"><strong>{ukuran}</strong> | <span class=\"card-media\" data-id=\"{media}\" data-en=\"{quick_en(media)}\">{media}</span></p>
            <div class=\"prices\">
                <div class=\"price-item\">
                    <small class=\"ui-soft-file\">Soft File (High-Res)</small>
                    <span class=\"price-val\">$ 250</span>
                </div>
                <div class=\"price-item\">
                    <small class=\"ui-print-license\">Lisensi Cetak</small>
                    <span class=\"price-val\">$ 100</span>
                    <span class=\"shipping-tag ui-free-shipping\">Bebas Ongkos Kirim</span>
                </div>
            </div>
            <p class=\"statement trans-block\" data-orig=\"{urllib.parse.quote(statement)}\">\"{statement}\"</p>
            <details>
                <summary class=\"ui-curatorial-btn\">Catatan Kuratorial &amp; SEO</summary>
                <div class=\"kuratorial-box\">
                    <p class=\"kuratorial trans-block\" data-orig=\"{urllib.parse.quote(kuratorial)}\">{kuratorial}</p>
                    <p class=\"tags\"><strong>Tags:</strong> {keywords}</p>
                </div>
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
        .loading-pill {{ display: none; font-size: 0.82rem; color: #38bdf8; background: #1e293b; padding: 4px 12px; border-radius: 12px; border: 1px solid #0284c7; }}
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
        .kuratorial-box {{ margin-top: 6px; }}
        .kuratorial {{ margin-bottom: 8px; color: #e2e8f0; line-height: 1.4; }}
        .tags {{ font-size: 0.75rem; color: #64748b; word-break: break-word; }}
    </style>
</head>
<body>
    <div class=\"top-bar\">
        <span class=\"loading-pill\" id=\"loadPill\">Menerjemahkan seluruh narasi kuratorial...</span>
        <div class=\"lang-switch\">
            <button class=\"lang-btn active\" id=\"btn-id\" onclick=\"applyLang('id')\">ID (Indonesia)</button>
            <button class=\"lang-btn\" id=\"btn-en\" onclick=\"applyLang('en')\">EN (English)</button>
        </div>
    </div>

    <header>
        <h1 id=\"mainTitle\">Katalog Karya Maruto Septriono</h1>
        <p id=\"subTitle\">Arsip Digital, Portofolio &amp; Etalase Komersial Internasional</p>
        <div class=\"search-box\">
            <input type=\"text\" id=\"searchInput\" placeholder=\"Cari judul karya atau medium...\" onkeyup=\"filterCards()\" />
        </div>
    </header>

    <div class=\"grid\" id=\"artGrid\">
        {''.join(cards_html)}
    </div>

    <script>
        const enCache = new Map();

        async function fetchTranslationBatch(texts) {{
            const results = [];
            for (let t of texts) {{
                if (!t || t.trim() === '') {{
                    results.push('');
                    continue;
                }}
                if (enCache.has(t)) {{
                    results.push(enCache.get(t));
                    continue;
                }}
                try {{
                    const url = 'https://translate.googleapis.com/translate_a/single?client=gtx&sl=id&tl=en&dt=t&q=' + encodeURIComponent(t);
                    const res = await fetch(url);
                    const data = await res.json();
                    let translated = '';
                    if (data && data[0]) {{
                        data[0].forEach(part => {{ if (part[0]) translated += part[0]; }});
                    }}
                    let finalRes = translated || t;
                    enCache.set(t, finalRes);
                    results.push(finalRes);
                }} catch (e) {{
                    results.push(t);
                }}
            }}
            return results;
        }}

        async function applyLang(lang) {{
            document.querySelectorAll('.lang-btn').forEach(b => b.classList.remove('active'));
            document.getElementById('btn-' + lang).classList.add('active');

            const isEN = (lang === 'en');
            
            document.getElementById('mainTitle').innerText = isEN ? 'Maruto Septriono Art Catalog' : 'Katalog Karya Maruto Septriono';
            document.getElementById('subTitle').innerText = isEN ? 'Digital Archive, Portfolio & International Commercial Gallery' : 'Arsip Digital, Portofolio & Etalase Komersial Internasional';
            document.getElementById('searchInput').placeholder = isEN ? 'Search by artwork title or medium...' : 'Cari judul karya atau medium...';

            document.querySelectorAll('.ui-not-for-sale').forEach(el => el.innerText = isEN ? 'Original: Not For Sale' : 'Karya Asli: Tidak Dijual');
            document.querySelectorAll('.ui-soft-file').forEach(el => el.innerText = isEN ? 'High-Res Soft File' : 'Soft File (High-Res)');
            document.querySelectorAll('.ui-print-license').forEach(el => el.innerText = isEN ? 'Print License' : 'Lisensi Cetak');
            document.querySelectorAll('.ui-free-shipping').forEach(el => el.innerText = isEN ? 'Free Worldwide Shipping' : 'Bebas Ongkos Kirim');
            document.querySelectorAll('.ui-curatorial-btn').forEach(el => el.innerText = isEN ? 'Curatorial Statement & SEO' : 'Catatan Kuratorial & SEO');

            document.querySelectorAll('.card-media').forEach(el => {{
                el.innerText = isEN ? el.getAttribute('data-en') : el.getAttribute('data-id');
            }});

            const blocks = Array.from(document.querySelectorAll('.trans-block'));
            const pill = document.getElementById('loadPill');

            if (isEN) {{
                pill.style.display = 'inline-block';
                const rawTexts = blocks.map(el => decodeURIComponent(el.getAttribute('data-orig')));
                
                const batchSize = 6;
                for (let i = 0; i < blocks.length; i += batchSize) {{
                    const sliceBlocks = blocks.slice(i, i + batchSize);
                    const sliceTexts = rawTexts.slice(i, i + batchSize);
                    const translatedSlice = await fetchTranslationBatch(sliceTexts);
                    
                    sliceBlocks.forEach((el, idx) => {{
                        let resText = translatedSlice[idx];
                        if (el.classList.contains('statement')) {{
                            el.innerText = '\"' + resText + '\"';
                        }} else {{
                            el.innerText = resText;
                        }}
                    }});
                }}
                pill.style.display = 'none';
            }} else {{
                pill.style.display = 'none';
                blocks.forEach(el => {{
                    let raw = decodeURIComponent(el.getAttribute('data-orig'));
                    if (el.classList.contains('statement')) {{
                        el.innerText = '\"' + raw + '\"';
                    }} else {{
                        el.innerText = raw;
                    }}
                }});
            }}
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

print('SUKSES! index.html telah diperbarui.')
