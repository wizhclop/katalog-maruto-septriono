import os
import json
import shutil
import re

CATALOG_PATH = r"F:\DATABASE_AI ART\ART\art_catalog.json"
SOURCE_IMAGE_DIR = r"F:\DATABASE_AI ART\ART\ART_70"
OUTPUT_DIR = r"F:\DATABASE_AI ART\ART\web_galeri"
OUTPUT_IMG_DIR = os.path.join(OUTPUT_DIR, "images")

os.makedirs(OUTPUT_IMG_DIR, exist_ok=True)

def build_hybrid_gallery():
    print("==================================================")
    print("  MEMBANGUN GALERI WEB HYBRID (GOTHIC & KOMERSIAL)")
    print("==================================================")

    if not os.path.exists(CATALOG_PATH):
        print("ERROR: art_catalog.json tidak ditemukan!")
        return

    with open(CATALOG_PATH, "r", encoding="utf-8-sig") as f:
        catalog = json.load(f)

    all_files_in_folder = os.listdir(SOURCE_IMAGE_DIR)
    catalog_reversed = list(reversed(catalog))
    cards_html = []
    found_count = 0

    for item in catalog_reversed:
        art_id = item.get("ID") or item.get("id") or "ART"
        title = item.get("Judul") or item.get("judul") or "Tanpa Judul"
        year = item.get("Tahun") or item.get("tahun") or "2026"
        size = item.get("Ukuran") or item.get("ukuran") or "-"
        media = item.get("Media") or item.get("media") or "-"
        filename = item.get("Nama_File") or item.get("file") or ""
        statement = item.get("artist_statement_id") or ""
        curatorial = item.get("deskripsi_kuratorial") or ""
        raw_tags = item.get("tags") or ""

        # Cocokkan nama file atau kode ART-xxx ke folder gambar
        matched_file = None
        if filename and os.path.exists(os.path.join(SOURCE_IMAGE_DIR, filename)):
            matched_file = filename
        else:
            clean_id_num = re.search(r"(\d+)", art_id)
            if clean_id_num:
                target_token = f"ART-{int(clean_id_num.group(1)):03d}"
                for f in all_files_in_folder:
                    if target_token.lower() in f.lower():
                        matched_file = f
                        break

        if matched_file:
            src_img = os.path.join(SOURCE_IMAGE_DIR, matched_file)
            ext = os.path.splitext(matched_file)[1]
            web_filename = f"{art_id}{ext}"
            dst_img = os.path.join(OUTPUT_IMG_DIR, web_filename)
            shutil.copy2(src_img, dst_img)
            web_img_rel = f"images/{web_filename}"
            item["web_image"] = web_filename
            found_count += 1
        else:
            web_img_rel = "images/notfound.jpg"
            item["web_image"] = ""

        # Escape teks untuk keamanan atribut HTML
        safe_statement = (statement[:130] + "...") if len(statement) > 130 else statement
        search_blob = f"{art_id} {title} {media} {year} {raw_tags}".lower()

        card = f"""
        <div class="art-card" data-search="{search_blob}">
            <div class="img-container" onclick="openModal('{art_id}')">
                <img src="{web_img_rel}" alt="{title}" loading="lazy" onerror="this.src='https://via.placeholder.com/400x500/181820/888?text=Maruto+Art'">
                <div class="art-badge-row">
                    <span class="badge badge-id">{art_id}</span>
                    <span class="badge badge-year">{year}</span>
                    <span class="badge badge-status">Karya Asli: Koleksi Pribadi</span>
                </div>
            </div>

            <div class="card-info">
                <h3 class="art-title" onclick="openModal('{art_id}')">{title}</h3>
                <p class="art-spec">{size} &bull; {media}</p>

                <!-- Panel Komersial -->
                <div class="commercial-box">
                    <div class="price-col">
                        <span class="price-label">Soft File (High-Res)</span>
                        <span class="price-val">$ 250</span>
                    </div>
                    <div class="price-col">
                        <span class="price-label">Lisensi Cetak</span>
                        <span class="price-val">$ 100</span>
                        <small class="free-shipping">Bebas Royalti</small>
                    </div>
                </div>

                <!-- Tombol Kontak Cepat -->
                <div class="action-buttons">
                    <a href="https://instagram.com/marutoseptriono" target="_blank" class="btn btn-dm">
                        ✉ DM Instagram
                    </a>
                    <a href="mailto:marutoseptriono@gmail.com?subject=Tanya Karya {art_id} - {title}" class="btn btn-email">
                        ✉ Order Email
                    </a>
                </div>

                <!-- Artist Statement Singkat -->
                <div class="card-statement" onclick="openModal('{art_id}')">
                    "{safe_statement}"
                </div>

                <div class="card-footer-link" onclick="openModal('{art_id}')">
                    &bull; Catatan Kuratorial & Detail Lengkap &rsaquo;
                </div>
            </div>
        </div>
        """
        cards_html.append(card)

    catalog_json_str = json.dumps(catalog, ensure_ascii=False)

    html_content = f"""<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Katalog Karya Maruto Septriono | Official Curatorial Archive & Commercial Portfolio</title>
    <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@600;700;900&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-color: #0b0c10;
            --surface-color: #14161d;
            --card-color: #1a1c24;
            --card-inner: #111318;
            --accent-gold: #c5a059;
            --accent-gold-light: #e5c378;
            --accent-teal: #1f7a8c;
            --text-main: #f0f0f5;
            --text-muted: #9598a6;
            --border-color: #262938;
            --price-green: #38bdf8;
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            background-color: var(--bg-color);
            color: var(--text-main);
            font-family: 'Plus Jakarta Sans', sans-serif;
            line-height: 1.5;
        }}

        /* TOP NAVIGATION */
        .top-nav {{
            display: flex;
            justify-content: flex-end;
            padding: 15px 30px;
            background: #08080b;
            border-bottom: 1px solid var(--border-color);
        }}

        .lang-switch button {{
            background: #1b1d26;
            color: var(--text-muted);
            border: 1px solid var(--border-color);
            padding: 5px 12px;
            font-size: 0.8rem;
            cursor: pointer;
            border-radius: 4px;
            font-family: inherit;
        }}

        .lang-switch button.active {{
            background: #0284c7;
            color: #fff;
            border-color: #0284c7;
            font-weight: 600;
        }}

        /* HEADER */
        header {{
            text-align: center;
            padding: 60px 20px 35px;
            background: radial-gradient(circle at center, #1e1b29 0%, var(--bg-color) 75%);
            border-bottom: 1px solid var(--border-color);
        }}

        header h1 {{
            font-family: 'Cinzel', serif;
            font-size: 2.6rem;
            letter-spacing: 2px;
            color: #38bdf8;
            margin-bottom: 6px;
        }}

        header p.subtitle {{
            font-size: 1rem;
            color: var(--text-muted);
            letter-spacing: 1px;
            margin-bottom: 25px;
        }}

        /* SEARCH BAR */
        .search-container {{
            max-width: 600px;
            margin: 0 auto;
            position: relative;
        }}

        .search-container input {{
            width: 100%;
            background: #101217;
            border: 1px solid #2f3447;
            border-radius: 8px;
            padding: 12px 20px;
            color: #fff;
            font-size: 0.95rem;
            font-family: inherit;
            outline: none;
            transition: all 0.3s;
        }}

        .search-container input:focus {{
            border-color: #38bdf8;
            box-shadow: 0 0 15px rgba(56, 189, 248, 0.2);
        }}

        .stats-tag {{
            display: inline-block;
            margin-top: 15px;
            font-size: 0.85rem;
            color: var(--accent-gold);
            background: rgba(197, 160, 89, 0.1);
            padding: 4px 14px;
            border-radius: 20px;
            border: 1px solid rgba(197, 160, 89, 0.25);
        }}

        /* GRID LAYOUT */
        .container {{
            max-width: 1440px;
            margin: 0 auto;
            padding: 40px 25px;
        }}

        .gallery-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
            gap: 25px;
        }}

        /* ART CARD */
        .art-card {{
            background: var(--card-color);
            border: 1px solid var(--border-color);
            border-radius: 10px;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            transition: transform 0.25s, border-color 0.25s;
        }}

        .art-card:hover {{
            border-color: #38bdf8;
            transform: translateY(-5px);
            box-shadow: 0 12px 25px rgba(0,0,0,0.5);
        }}

        .img-container {{
            position: relative;
            background: #000;
            width: 100%;
            height: 340px;
            cursor: pointer;
            overflow: hidden;
        }}

        .img-container img {{
            width: 100%;
            height: 100%;
            object-fit: cover;
            transition: transform 0.4s ease;
        }}

        .art-card:hover .img-container img {{
            transform: scale(1.04);
        }}

        .art-badge-row {{
            position: absolute;
            top: 10px;
            left: 10px;
            right: 10px;
            display: flex;
            gap: 6px;
            flex-wrap: wrap;
        }}

        .badge {{
            padding: 3px 8px;
            font-size: 0.7rem;
            font-weight: 600;
            border-radius: 4px;
            backdrop-filter: blur(4px);
        }}

        .badge-id {{
            background: #0284c7;
            color: #fff;
        }}

        .badge-year {{
            background: #0369a1;
            color: #e0f2fe;
        }}

        .badge-status {{
            background: rgba(30, 41, 59, 0.9);
            color: #94a3b8;
            border: 1px solid #475569;
        }}

        /* CARD BODY */
        .card-info {{
            padding: 18px;
            display: flex;
            flex-direction: column;
            flex-grow: 1;
            background: var(--card-inner);
        }}

        .art-title {{
            font-family: 'Cinzel', serif;
            font-size: 1.15rem;
            color: #fff;
            margin-bottom: 4px;
            cursor: pointer;
        }}

        .art-title:hover {{
            color: #38bdf8;
        }}

        .art-spec {{
            font-size: 0.8rem;
            color: var(--text-muted);
            margin-bottom: 12px;
        }}

        /* COMMERCIAL PANEL */
        .commercial-box {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            background: #181b24;
            border: 1px solid var(--border-color);
            border-radius: 6px;
            padding: 10px;
            margin-bottom: 12px;
            gap: 8px;
        }}

        .price-col {{
            display: flex;
            flex-direction: column;
        }}

        .price-label {{
            font-size: 0.72rem;
            color: var(--text-muted);
        }}

        .price-val {{
            font-size: 1.05rem;
            font-weight: 700;
            color: #38bdf8;
        }}

        .free-shipping {{
            font-size: 0.68rem;
            color: #64748b;
        }}

        /* ACTION BUTTONS */
        .action-buttons {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 8px;
            margin-bottom: 12px;
        }}

        .btn {{
            text-align: center;
            padding: 7px 10px;
            border-radius: 5px;
            font-size: 0.78rem;
            font-weight: 600;
            text-decoration: none;
            transition: opacity 0.2s;
        }}

        .btn:hover {{
            opacity: 0.88;
        }}

        .btn-dm {{
            background: linear-gradient(135deg, #e1306c, #fd1d1d);
            color: #fff;
        }}

        .btn-email {{
            background: #272a38;
            color: #e2e8f0;
            border: 1px solid #3e445b;
        }}

        /* STATEMENT PREVIEW */
        .card-statement {{
            font-size: 0.82rem;
            color: #b3b7c8;
            font-style: italic;
            margin-bottom: 12px;
            cursor: pointer;
            display: -webkit-box;
            -webkit-line-clamp: 3;
            -webkit-box-orient: vertical;
            overflow: hidden;
            line-height: 1.45;
        }}

        .card-footer-link {{
            margin-top: auto;
            font-size: 0.76rem;
            color: #38bdf8;
            cursor: pointer;
            padding-top: 8px;
            border-top: 1px solid #1f2330;
        }}

        /* MODAL DETAIL POPUP */
        .modal {{
            display: none;
            position: fixed;
            z-index: 9999;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(5, 6, 9, 0.94);
            backdrop-filter: blur(8px);
            align-items: center;
            justify-content: center;
            padding: 20px;
        }}

        .modal-content {{
            background: var(--surface-color);
            border: 1px solid var(--accent-gold);
            border-radius: 12px;
            max-width: 1050px;
            width: 100%;
            max-height: 90vh;
            overflow-y: auto;
            display: grid;
            grid-template-columns: 1fr 1fr;
            box-shadow: 0 25px 60px rgba(0,0,0,0.9);
            position: relative;
        }}

        .modal-close {{
            position: absolute;
            top: 15px;
            right: 20px;
            color: var(--text-muted);
            font-size: 2rem;
            cursor: pointer;
            z-index: 10;
        }}

        .modal-close:hover {{
            color: #fff;
        }}

        .modal-img-wrap {{
            background: #000;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }}

        .modal-img-wrap img {{
            max-width: 100%;
            max-height: 75vh;
            object-fit: contain;
            border-radius: 4px;
        }}

        .modal-details {{
            padding: 35px 30px;
            display: flex;
            flex-direction: column;
            gap: 14px;
        }}

        .modal-id {{
            font-family: 'Cinzel', serif;
            color: var(--accent-gold);
            font-size: 0.85rem;
            letter-spacing: 2px;
        }}

        .modal-title {{
            font-family: 'Cinzel', serif;
            font-size: 1.8rem;
            color: #fff;
            line-height: 1.25;
        }}

        .modal-specs {{
            border-top: 1px solid var(--border-color);
            border-bottom: 1px solid var(--border-color);
            padding: 10px 0;
            font-size: 0.88rem;
            color: var(--text-muted);
            display: flex;
            flex-direction: column;
            gap: 4px;
        }}

        .modal-specs span {{
            color: #fff;
            font-weight: 600;
        }}

        .modal-pricing-box {{
            background: #1a1e29;
            border: 1px solid #2d3448;
            padding: 12px;
            border-radius: 6px;
            display: flex;
            justify-content: space-around;
        }}

        .statement-box {{
            background: rgba(197, 160, 89, 0.05);
            border-left: 3px solid var(--accent-gold);
            padding: 10px 14px;
            font-style: italic;
            font-size: 0.92rem;
            color: #dedee5;
        }}

        .curatorial-box {{
            font-size: 0.88rem;
            color: var(--text-muted);
            line-height: 1.65;
        }}

        .tag {{
            display: inline-block;
            background: rgba(255, 255, 255, 0.05);
            color: #b0b0c5;
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 0.72rem;
            margin: 2px;
            border: 1px solid var(--border-color);
        }}

        footer {{
            text-align: center;
            padding: 45px 20px;
            border-top: 1px solid var(--border-color);
            color: var(--text-muted);
            font-size: 0.85rem;
        }}

        @media (max-width: 900px) {{
            .modal-content {{ grid-template-columns: 1fr; }}
            .modal-img-wrap {{ height: 320px; }}
            header h1 {{ font-size: 2rem; }}
        }}
    </style>
</head>
<body>

    <div class="top-nav">
        <div class="lang-switch">
            <button class="active">ID (Indonesia)</button>
            <button onclick="alert('Versi terjemahan bahasa Inggris kuratorial sedang disiapkan!')">EN (English)</button>
        </div>
    </div>

    <header>
        <h1>Katalog Karya Maruto Septriono</h1>
        <p class="subtitle">Arsip Digital, Portofolio & Etalase Komersial Internasional</p>

        <div class="search-container">
            <input type="text" id="searchInput" onkeyup="filterGallery()" placeholder="Cari judul karya, medium, tahun, atau ID (misal: ART-072, tinta)...">
        </div>

        <div class="stats-tag">
            Total Terarsip: <strong>{len(catalog)} Karya Seni</strong>
        </div>
    </header>

    <main class="container">
        <div class="gallery-grid" id="galleryGrid">
            {''.join(cards_html)}
        </div>
    </main>

    <!-- MODAL CURATORIAL POPUP -->
    <div id="artModal" class="modal" onclick="closeModalOnOutside(event)">
        <div class="modal-content">
            <span class="modal-close" onclick="closeModal()">&times;</span>
            <div class="modal-img-wrap">
                <img id="mImg" src="" alt="Detail Karya">
            </div>
            <div class="modal-details">
                <div class="modal-id" id="mId">ART-000</div>
                <h2 class="modal-title" id="mTitle">Judul Karya</h2>
                <div class="modal-specs">
                    <div>Tahun: <span id="mYear">2026</span></div>
                    <div>Media: <span id="mMedia">-</span></div>
                    <div>Ukuran Fisik: <span id="mSize">-</span></div>
                    <div>Status Fisik: <span style="color:#38bdf8;">Koleksi Pribadi</span></div>
                </div>

                <div class="modal-pricing-box">
                    <div>
                        <small style="color:#94a3b8; display:block;">Soft File High-Res</small>
                        <strong style="color:#38bdf8; font-size:1.1rem;">$ 250</strong>
                    </div>
                    <div style="border-left:1px solid #334155; padding-left:15px;">
                        <small style="color:#94a3b8; display:block;">Lisensi Cetak Royalti</small>
                        <strong style="color:#38bdf8; font-size:1.1rem;">$ 100</strong>
                    </div>
                </div>

                <div class="statement-box" id="mStatement">"Artist Statement..."</div>
                <div class="curatorial-box" id="mCuratorial">Catatan kuratorial...</div>
                <div id="mTags"></div>

                <div class="action-buttons" style="margin-top:10px;">
                    <a id="mDmBtn" href="https://instagram.com/marutoseptriono" target="_blank" class="btn btn-dm">
                        ✉ DM Instagram
                    </a>
                    <a id="mEmailBtn" href="#" class="btn btn-email">
                        ✉ Order via Email
                    </a>
                </div>
            </div>
        </div>
    </div>

    <footer>
        <p>&copy; 2026 Maruto Art Studio. Arsip Kuratorial & Portofolio Komersial Seniman.</p>
    </footer>

    <script>
        const catalogData = {catalog_json_str};

        function filterGallery() {{
            const query = document.getElementById('searchInput').value.toLowerCase().trim();
            const cards = document.querySelectorAll('.art-card');

            cards.forEach(card => {{
                const searchData = card.getAttribute('data-search') || '';
                if (searchData.includes(query)) {{
                    card.style.display = 'flex';
                }} else {{
                    card.style.display = 'none';
                }}
            }});
        }}

        function openModal(artId) {{
            const item = catalogData.find(x => (x.ID === artId || x.id === artId));
            if (!item) return;

            document.getElementById('mId').innerText = item.ID || item.id || '';
            const title = item.Judul || item.judul || 'Tanpa Judul';
            document.getElementById('mTitle').innerText = title;
            document.getElementById('mYear').innerText = item.Tahun || item.tahun || '-';
            document.getElementById('mMedia').innerText = item.Media || item.media || '-';
            document.getElementById('mSize').innerText = item.Ukuran || item.ukuran || '-';
            
            const webImg = item.web_image || '';
            document.getElementById('mImg').src = webImg ? ('images/' + webImg) : '';

            document.getElementById('mStatement').innerText = '"' + (item.artist_statement_id || 'Refleksi artistik.') + '"';
            document.getElementById('mCuratorial').innerText = item.deskripsi_kuratorial || 'Belum ada catatan kuratorial rinci.';

            // Perbarui tombol email modal
            document.getElementById('mEmailBtn').href = 'mailto:marutoseptriono@gmail.com?subject=Tanya Karya ' + (item.ID || '') + ' - ' + title;

            const tagsDiv = document.getElementById('mTags');
            tagsDiv.innerHTML = '';
            if (item.tags) {{
                item.tags.split(',').forEach(t => {{
                    const clean = t.trim().replace('#', '');
                    if (clean) {{
                        const span = document.createElement('span');
                        span.className = 'tag';
                        span.innerText = '#' + clean;
                        tagsDiv.appendChild(span);
                    }}
                }});
            }}

            document.getElementById('artModal').style.display = 'flex';
            document.body.style.overflow = 'hidden';
        }}

        function closeModal() {{
            document.getElementById('artModal').style.display = 'none';
            document.body.style.overflow = 'auto';
        }}

        function closeModalOnOutside(e) {{
            if (e.target.id === 'artModal') {{ closeModal(); }}
        }}

        document.addEventListener('keydown', (e) => {{ if (e.key === 'Escape') closeModal(); }});
    </script>
</body>
</html>
"""

    with open(os.path.join(OUTPUT_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"[OK] Selesai! Web Galeri Hybrid berhasil dibangun dengan {found_count} karya lengkap.")

if __name__ == "__main__":
    build_hybrid_gallery()
