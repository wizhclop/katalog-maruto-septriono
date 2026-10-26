import os
import json
import re
import html

BASE_DIR = r"F:\DATABASE_AI ART\ART"
CATALOG_PATH = os.path.join(BASE_DIR, "art_catalog.json")
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")
OUTPUT_XML = os.path.join(BASE_DIR, "tema_blogspot_maruto.xml")
LOCAL_WEB_IMG_DIR = os.path.join(BASE_DIR, "web_galeri", "images")

def build_blogspot_xml():
    print("==================================================")
    print("  MEMBANGUN TEMA BLOGSPOT DENGAN GAMBAR 100% AKURAT")
    print("==================================================")

    if not os.path.exists(CATALOG_PATH):
        print("ERROR: art_catalog.json tidak ditemukan!")
        return

    with open(CATALOG_PATH, "r", encoding="utf-8-sig") as f:
        catalog = json.load(f)

    artist_name = "Maruto Septriono"
    artist_email = "kirimdoa@gmail.com"
    instagram_handle = "maruto.septriono"
    vercel_url = "https://katalog-maruto-septriono.vercel.app"

    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as cf:
                cfg = json.load(cf)
                artist_name = cfg.get("ARTIST_NAME", artist_name)
                artist_email = cfg.get("ARTIST_EMAIL", artist_email)
                instagram_handle = cfg.get("INSTAGRAM_HANDLE", instagram_handle)
                vercel_url = cfg.get("VERCEL_CATALOG_URL", vercel_url)
        except Exception:
            pass

    # Ambil daftar file gambar yang sebenarnya ada di web_galeri/images
    existing_images = []
    if os.path.exists(LOCAL_WEB_IMG_DIR):
        existing_images = os.listdir(LOCAL_WEB_IMG_DIR)

    img_base = f"{vercel_url}/images"

    catalog_reversed = list(reversed(catalog))
    cards_html = []
    found_img_count = 0

    for item in catalog_reversed:
        art_id = item.get("ID") or item.get("id") or "ART"
        title = item.get("Judul") or item.get("judul") or "Tanpa Judul"
        year = item.get("Tahun") or item.get("tahun") or "2026"
        size = item.get("Ukuran") or item.get("ukuran") or "-"
        media = item.get("Media") or item.get("media") or "-"
        statement = item.get("artist_statement_id") or ""
        raw_tags = item.get("tags") or ""

        # Deteksi nama file asli yang cocok di folder images
        matched_img = None
        # Prioritas 1: Sesuai web_image dari katalog
        if item.get("web_image") and item.get("web_image") in existing_images:
            matched_img = item.get("web_image")
        else:
            # Prioritas 2: Cari awalan kode ID (misal ART-01 atau ART-001)
            clean_num = re.search(r"(\d+)", art_id)
            if clean_num:
                num_int = int(clean_num.group(1))
                candidates = [
                    f"{art_id}.jpg", f"{art_id}.png", f"{art_id}.jpeg",
                    f"ART-{num_int:03d}.jpg", f"ART-{num_int:03d}.png",
                    f"ART-{num_int:02d}.jpg", f"ART-{num_int:02d}.png",
                    f"ART-{num_int}.jpg", f"ART-{num_int}.png"
                ]
                for c in candidates:
                    if c in existing_images:
                        matched_img = c
                        break

        if matched_img:
            web_img_url = f"{img_base}/{matched_img}"
            item["resolved_web_img"] = matched_img
            found_img_count += 1
        else:
            web_img_url = f"{img_base}/{art_id}.jpg"
            item["resolved_web_img"] = f"{art_id}.jpg"

        safe_statement_raw = (statement[:100] + "...") if len(statement) > 100 else statement
        safe_statement = html.escape(safe_statement_raw, quote=True)
        safe_title = html.escape(title, quote=True)
        safe_size = html.escape(size, quote=True)
        safe_media = html.escape(media, quote=True)
        search_blob = html.escape(f"{art_id} {title} {media} {year} {raw_tags}".lower(), quote=True)

        card = f"""
        <div class="art-card" id="card-{art_id}" data-search="{search_blob}">
            <div class="img-container" onclick="openModal('{art_id}')">
                <img src="{web_img_url}" alt="{safe_title}" loading="lazy" onerror="this.src='https://via.placeholder.com/400x500/181820/888?text=Maruto+Art'"/>
                <div class="art-badge-row">
                    <span class="badge badge-id">{art_id}</span>
                    <span class="badge badge-year">{year}</span>
                </div>
            </div>

            <div class="card-info">
                <h3 class="art-title" onclick="openModal('{art_id}')">{safe_title}</h3>
                <p class="art-spec">{safe_size} &#8226; {safe_media}</p>

                <div class="commercial-box">
                    <div class="price-col">
                        <span class="price-label">Soft File</span>
                        <span class="price-val">$ 250</span>
                    </div>
                    <div class="price-col">
                        <span class="price-label">Lisensi</span>
                        <span class="price-val">$ 100</span>
                    </div>
                </div>

                <div class="action-buttons">
                    <a href="https://instagram.com/{instagram_handle}" target="_blank" class="btn btn-dm">
                        ✉ DM
                    </a>
                    <a href="mailto:{artist_email}?subject=Tanya Karya {art_id} - {safe_title}" class="btn btn-email">
                        ✉ Email
                    </a>
                </div>

                <div class="card-statement" onclick="openModal('{art_id}')">
                    &quot;{safe_statement}&quot;
                </div>

                <div class="card-footer-row">
                    <span class="card-footer-link" onclick="openModal('{art_id}')">&#8226; Detail &#8250;</span>
                    <button class="btn-copy-card" onclick="copyDirectLink('{art_id}', event)" title="Salin Link">🔗 Link</button>
                </div>
            </div>
        </div>
        """
        cards_html.append(card)

    cards_joined = "".join(cards_html)
    catalog_json_str = json.dumps(catalog, ensure_ascii=False)
    catalog_count = len(catalog)

    xml_template = """<?xml version="1.0" encoding="UTF-8" ?>
<!DOCTYPE html>
<html b:css='false' b:defaultwidgetversion='2' b:layoutsversion='3' expr:dir='data:blog.languageDirection' xmlns='http://www.w3.org/1999/xhtml' xmlns:b='http://www.google.com/2005/gml/b' xmlns:data='http://www.google.com/2005/gml/data' xmlns:expr='http://www.google.com/2005/gml/expr'>
<head>
    <meta content='width=device-width, initial-scale=1.0' name='viewport'/>
    <title>Katalog Karya __ARTIST_NAME__ | Official Curatorial Archive</title>
    <b:skin><![CDATA[
        #header-holder, .sidebar, .comments, #blog-pager, .feed-links, .status-msg-wrap { display:none !important; }
    ]]></b:skin>
    <link href='https://fonts.googleapis.com/css2?family=Cinzel:wght@600;700;900&amp;family=Plus+Jakarta+Sans:wght@300;400;500;600;700&amp;display=swap' rel='stylesheet'/>
    <style>
        :root {
            --bg-color: #0b0c10;
            --surface-color: #14161d;
            --card-color: #1a1c24;
            --card-inner: #111318;
            --accent-gold: #c5a059;
            --accent-gold-light: #e5c378;
            --text-main: #f0f0f5;
            --text-muted: #9598a6;
            --border-color: #262938;
            --price-green: #38bdf8;
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            background-color: var(--bg-color) !important;
            color: var(--text-main) !important;
            font-family: 'Plus Jakarta Sans', sans-serif;
            line-height: 1.4;
        }

        .top-nav {
            display: flex;
            justify-content: flex-end;
            padding: 12px 20px;
            background: #08080b;
            border-bottom: 1px solid var(--border-color);
        }

        .lang-switch button {
            background: #1b1d26;
            color: var(--text-muted);
            border: 1px solid var(--border-color);
            padding: 4px 10px;
            font-size: 0.75rem;
            cursor: pointer;
            border-radius: 4px;
            font-family: inherit;
        }

        .lang-switch button.active {
            background: #0284c7;
            color: #fff;
            border-color: #0284c7;
            font-weight: 600;
        }

        header {
            text-align: center;
            padding: 35px 15px 25px;
            background: radial-gradient(circle at center, #1e1b29 0%, var(--bg-color) 75%);
            border-bottom: 1px solid var(--border-color);
        }

        header h1 {
            font-family: 'Cinzel', serif;
            font-size: 2.2rem;
            letter-spacing: 1.5px;
            color: #38bdf8;
            margin-bottom: 6px;
        }

        header p.subtitle {
            font-size: 0.9rem;
            color: var(--text-muted);
            letter-spacing: 0.5px;
            margin-bottom: 18px;
        }

        .search-container {
            max-width: 600px;
            margin: 0 auto;
            position: relative;
        }

        .search-container input {
            width: 100%;
            background: #101217;
            border: 1px solid #2f3447;
            border-radius: 8px;
            padding: 10px 16px;
            color: #fff;
            font-size: 0.9rem;
            font-family: inherit;
            outline: none;
            transition: all 0.3s;
        }

        .search-container input:focus {
            border-color: #38bdf8;
            box-shadow: 0 0 12px rgba(56, 189, 248, 0.2);
        }

        .stats-tag {
            display: inline-block;
            margin-top: 12px;
            font-size: 0.8rem;
            color: var(--accent-gold);
            background: rgba(197, 160, 89, 0.1);
            padding: 3px 12px;
            border-radius: 20px;
            border: 1px solid rgba(197, 160, 89, 0.25);
        }

        .container {
            max-width: 1440px;
            margin: 0 auto;
            padding: 30px 15px;
        }

        .gallery-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 20px;
        }

        .art-card {
            background: var(--card-color);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            transition: transform 0.25s, border-color 0.25s;
        }

        .art-card:hover {
            border-color: #38bdf8;
            transform: translateY(-4px);
            box-shadow: 0 10px 20px rgba(0,0,0,0.5);
        }

        .img-container {
            position: relative;
            background: #000;
            width: 100%;
            height: 280px;
            cursor: pointer;
            overflow: hidden;
        }

        .img-container img {
            width: 100%;
            height: 100%;
            object-fit: cover;
            transition: transform 0.4s ease;
        }

        .art-card:hover .img-container img {
            transform: scale(1.04);
        }

        .art-badge-row {
            position: absolute;
            top: 8px;
            left: 8px;
            display: flex;
            gap: 5px;
            flex-wrap: wrap;
        }

        .badge {
            padding: 2px 6px;
            font-size: 0.65rem;
            font-weight: 600;
            border-radius: 3px;
            backdrop-filter: blur(4px);
        }

        .badge-id { background: #0284c7; color: #fff; }
        .badge-year { background: #0369a1; color: #e0f2fe; }

        .card-info {
            padding: 14px;
            display: flex;
            flex-direction: column;
            flex-grow: 1;
            background: var(--card-inner);
        }

        .art-title {
            font-family: 'Cinzel', serif;
            font-size: 1.05rem;
            color: #fff;
            margin-bottom: 3px;
            cursor: pointer;
            line-height: 1.25;
        }

        .art-title:hover { color: #38bdf8; }

        .art-spec {
            font-size: 0.75rem;
            color: var(--text-muted);
            margin-bottom: 10px;
        }

        .commercial-box {
            display: grid;
            grid-template-columns: 1fr 1fr;
            background: #181b24;
            border: 1px solid var(--border-color);
            border-radius: 5px;
            padding: 8px;
            margin-bottom: 10px;
            gap: 6px;
            text-align: center;
        }

        .price-col { display: flex; flex-direction: column; }
        .price-label { font-size: 0.65rem; color: var(--text-muted); }
        .price-val { font-size: 0.95rem; font-weight: 700; color: #38bdf8; }

        .action-buttons {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 6px;
            margin-bottom: 10px;
        }

        .btn {
            text-align: center;
            padding: 6px 4px;
            border-radius: 4px;
            font-size: 0.72rem;
            font-weight: 600;
            text-decoration: none;
            transition: opacity 0.2s;
        }

        .btn:hover { opacity: 0.88; }
        .btn-dm { background: linear-gradient(135deg, #e1306c, #fd1d1d); color: #fff; }
        .btn-email { background: #272a38; color: #e2e8f0; border: 1px solid #3e445b; }

        .card-statement {
            font-size: 0.75rem;
            color: #b3b7c8;
            font-style: italic;
            margin-bottom: 10px;
            cursor: pointer;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
            line-height: 1.35;
        }

        .card-footer-row {
            margin-top: auto;
            padding-top: 8px;
            border-top: 1px solid #1f2330;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .card-footer-link { font-size: 0.72rem; color: #38bdf8; cursor: pointer; }

        .btn-copy-card {
            background: #1e2230;
            color: #cbd5e1;
            border: 1px solid #334155;
            padding: 2px 6px;
            font-size: 0.68rem;
            border-radius: 3px;
            cursor: pointer;
            transition: all 0.2s;
        }

        .btn-copy-card:hover { background: #0284c7; color: #fff; }

        .modal {
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
            padding: 15px;
        }

        .modal-content {
            background: var(--surface-color);
            border: 1px solid var(--accent-gold);
            border-radius: 10px;
            max-width: 1050px;
            width: 100%;
            max-height: 90vh;
            overflow-y: auto;
            display: grid;
            grid-template-columns: 1fr 1fr;
            box-shadow: 0 25px 60px rgba(0,0,0,0.9);
            position: relative;
        }

        .modal-close {
            position: absolute;
            top: 12px;
            right: 18px;
            color: var(--text-muted);
            font-size: 1.8rem;
            cursor: pointer;
            z-index: 10;
        }

        .modal-close:hover { color: #fff; }

        .modal-img-wrap {
            background: #000;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 15px;
        }

        .modal-img-wrap img {
            max-width: 100%;
            max-height: 75vh;
            object-fit: contain;
            border-radius: 4px;
        }

        .modal-details {
            padding: 25px 20px;
            display: flex;
            flex-direction: column;
            gap: 12px;
        }

        .modal-id {
            font-family: 'Cinzel', serif;
            color: var(--accent-gold);
            font-size: 0.8rem;
            letter-spacing: 2px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .modal-title {
            font-family: 'Cinzel', serif;
            font-size: 1.5rem;
            color: #fff;
            line-height: 1.25;
        }

        .modal-specs {
            border-top: 1px solid var(--border-color);
            border-bottom: 1px solid var(--border-color);
            padding: 8px 0;
            font-size: 0.82rem;
            color: var(--text-muted);
            display: flex;
            flex-direction: column;
            gap: 4px;
        }

        .modal-specs span { color: #fff; font-weight: 600; }

        .modal-pricing-box {
            background: #1a1e29;
            border: 1px solid #2d3448;
            padding: 10px;
            border-radius: 6px;
            display: flex;
            justify-content: space-around;
        }

        .statement-box {
            background: rgba(197, 160, 89, 0.05);
            border-left: 3px solid var(--accent-gold);
            padding: 8px 12px;
            font-style: italic;
            font-size: 0.85rem;
            color: #dedee5;
        }

        .curatorial-box {
            font-size: 0.82rem;
            color: var(--text-muted);
            line-height: 1.55;
        }

        .tag {
            display: inline-block;
            background: rgba(255, 255, 255, 0.05);
            color: #b0b0c5;
            padding: 2px 6px;
            border-radius: 3px;
            font-size: 0.68rem;
            margin: 2px;
            border: 1px solid var(--border-color);
        }

        #toast {
            visibility: hidden;
            min-width: 200px;
            background-color: #0284c7;
            color: #fff;
            text-align: center;
            border-radius: 6px;
            padding: 10px 14px;
            position: fixed;
            z-index: 10000;
            bottom: 25px;
            left: 50%;
            transform: translateX(-50%);
            font-size: 0.8rem;
            font-weight: 600;
            box-shadow: 0 4px 15px rgba(0,0,0,0.4);
        }

        #toast.show {
            visibility: visible;
            animation: fadein 0.3s, fadeout 0.5s 2.5s;
        }

        @keyframes fadein { from { bottom: 10px; opacity: 0; } to { bottom: 25px; opacity: 1; } }
        @keyframes fadeout { from { bottom: 25px; opacity: 1; } to { bottom: 10px; opacity: 0; } }

        footer {
            text-align: center;
            padding: 35px 15px;
            border-top: 1px solid var(--border-color);
            color: var(--text-muted);
            font-size: 0.8rem;
        }

        @media (max-width: 768px) {
            .container { padding: 15px 8px; }
            .gallery-grid {
                grid-template-columns: repeat(2, 1fr) !important;
                gap: 10px !important;
            }
            .img-container { height: 180px !important; }
            .card-info { padding: 10px 8px !important; }
            .art-title { font-size: 0.85rem !important; }
            .art-spec { font-size: 0.68rem !important; margin-bottom: 6px !important; }
            .commercial-box { padding: 5px !important; margin-bottom: 6px !important; gap: 4px !important; }
            .price-val { font-size: 0.82rem !important; }
            .btn { padding: 5px 2px !important; font-size: 0.65rem !important; }
            .card-statement { display: none !important; }
            header h1 { font-size: 1.6rem !important; }
            header { padding: 25px 12px 18px !important; }
            .modal-content { grid-template-columns: 1fr !important; }
            .modal-img-wrap { height: 280px !important; padding: 10px !important; }
            .modal-details { padding: 20px 15px !important; }
        }
    </style>
</head>
<body>
    <b:section id='main' showaddelement='no'/>

    <div class='top-nav'>
        <div class='lang-switch'>
            <button class='active'>ID (Indonesia)</button>
            <button onclick="alert('Versi terjemahan bahasa Inggris kuratorial sedang disiapkan!')">EN (English)</button>
        </div>
    </div>

    <header>
        <h1>Katalog Karya __ARTIST_NAME__</h1>
        <p class='subtitle'>Arsip Digital, Portofolio &amp; Etalase Komersial Internasional</p>

        <div class='search-container'>
            <input id='searchInput' onkeyup='filterGallery()' placeholder='Cari judul, ID (ART-075), atau media...' type='text'/>
        </div>

        <div class='stats-tag'>
            Total Terarsip: <strong>__CATALOG_COUNT__ Karya Seni</strong>
        </div>
    </header>

    <main class='container'>
        <div class='gallery-grid' id='galleryGrid'>
            __CARDS_CONTENT__
        </div>
    </main>

    <div class='modal' id='artModal' onclick='closeModalOnOutside(event)'>
        <div class='modal-content'>
            <span class='modal-close' onclick='closeModal()'>&#215;</span>
            <div class='modal-img-wrap'>
                <img alt='Detail Karya' id='mImg' src=''/>
            </div>
            <div class='modal-details'>
                <div class='modal-id'>
                    <span id='mId'>ART-000</span>
                    <button class='btn-copy-card' onclick='copyModalLink()'>🔗 Salin Link</button>
                </div>
                <h2 class='modal-title' id='mTitle'>Judul Karya</h2>
                <div class='modal-specs'>
                    <div>Tahun: <span id='mYear'>2026</span></div>
                    <div>Media: <span id='mMedia'>-</span></div>
                    <div>Ukuran Fisik: <span id='mSize'>-</span></div>
                    <div>Status Fisik: <span style='color:#38bdf8;'>Koleksi Pribadi</span></div>
                </div>

                <div class='modal-pricing-box'>
                    <div>
                        <small style='color:#94a3b8; display:block;'>Soft File High-Res</small>
                        <strong style='color:#38bdf8; font-size:1.1rem;'>$ 250</strong>
                    </div>
                    <div style='border-left:1px solid #334155; padding-left:15px;'>
                        <small style='color:#94a3b8; display:block;'>Lisensi Cetak Royalti</small>
                        <strong style='color:#38bdf8; font-size:1.1rem;'>$ 100</strong>
                    </div>
                </div>

                <div class='statement-box' id='mStatement'>&quot;Artist Statement...&quot;</div>
                <div class='curatorial-box' id='mCuratorial'>Catatan kuratorial...</div>
                <div id='mTags'/>

                <div class='action-buttons' style='margin-top:10px;'>
                    <a class='btn btn-dm' href='https://instagram.com/__INSTAGRAM_HANDLE__' id='mDmBtn' target='_blank'>
                        ✉ DM Instagram
                    </a>
                    <a class='btn btn-email' href='#' id='mEmailBtn'>
                        ✉ Order via Email
                    </a>
                </div>
            </div>
        </div>
    </div>

    <div id='toast'>Tautan karya berhasil disalin!</div>

    <footer>
        <p>&#169; 2026 __ARTIST_NAME__. Arsip Kuratorial &amp; Portofolio Komersial Seniman.</p>
    </footer>

    <script>
        //<![CDATA[
        const catalogData = __CATALOG_JSON__;
        let currentModalArtId = '';

        function showToast(msg) {
            const t = document.getElementById('toast');
            t.innerText = msg;
            t.className = 'show';
            setTimeout(() => { t.className = t.className.replace('show', ''); }, 2800);
        }

        function copyDirectLink(artId, e) {
            if (e) e.stopPropagation();
            const url = window.location.origin + window.location.pathname + '#' + artId;
            navigator.clipboard.writeText(url).then(() => {
                showToast('🔗 Tautan ' + artId + ' berhasil disalin!');
            }).catch(() => {
                prompt('Salin tautan ini:', url);
            });
        }

        function copyModalLink() {
            if (currentModalArtId) {
                copyDirectLink(currentModalArtId);
            }
        }

        function filterGallery() {
            const query = document.getElementById('searchInput').value.toLowerCase().trim();
            const cards = document.querySelectorAll('.art-card');

            cards.forEach(card => {
                const searchData = card.getAttribute('data-search') || '';
                if (searchData.includes(query)) {
                    card.style.display = 'flex';
                } else {
                    card.style.display = 'none';
                }
            });
        }

        function openModal(artId, updateHash = true) {
            const item = catalogData.find(x => (x.ID === artId || x.id === artId));
            if (!item) return;

            currentModalArtId = item.ID || item.id || '';
            document.getElementById('mId').innerText = currentModalArtId;
            const title = item.Judul || item.judul || 'Tanpa Judul';
            document.getElementById('mTitle').innerText = title;
            document.getElementById('mYear').innerText = item.Tahun || item.tahun || '-';
            document.getElementById('mMedia').innerText = item.Media || item.media || '-';
            document.getElementById('mSize').innerText = item.Ukuran || item.ukuran || '-';
            
            const resolvedImg = item.resolved_web_img || item.web_image || '';
            document.getElementById('mImg').src = resolvedImg ? ('__IMG_BASE__/' + resolvedImg) : '';

            document.getElementById('mStatement').innerText = '"' + (item.artist_statement_id || 'Refleksi artistik.') + '"';
            document.getElementById('mCuratorial').innerText = item.deskripsi_kuratorial || 'Belum ada catatan kuratorial rinci.';

            document.getElementById('mEmailBtn').href = 'mailto:__ARTIST_EMAIL__?subject=Tanya Karya ' + currentModalArtId + ' - ' + encodeURIComponent(title);

            const tagsDiv = document.getElementById('mTags');
            tagsDiv.innerHTML = '';
            if (item.tags) {
                item.tags.split(',').forEach(t => {
                    const clean = t.trim().replace('#', '');
                    if (clean) {
                        const span = document.createElement('span');
                        span.className = 'tag';
                        span.innerText = '#' + clean;
                        tagsDiv.appendChild(span);
                    }
                });
            }

            document.getElementById('artModal').style.display = 'flex';
            document.body.style.overflow = 'hidden';

            if (updateHash) {
                history.pushState(null, null, '#' + currentModalArtId);
            }
        }

        function closeModal() {
            document.getElementById('artModal').style.display = 'none';
            document.body.style.overflow = 'auto';
            currentModalArtId = '';
            history.pushState(null, null, window.location.pathname);
        }

        function closeModalOnOutside(e) {
            if (e.target.id === 'artModal') { closeModal(); }
        }

        document.addEventListener('keydown', (e) => { if (e.key === 'Escape') closeModal(); });

        window.addEventListener('DOMContentLoaded', () => {
            const hash = window.location.hash.replace('#', '').trim();
            if (hash) {
                setTimeout(() => {
                    openModal(hash, false);
                    const el = document.getElementById('card-' + hash);
                    if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }, 300);
            }
        });

        window.addEventListener('popstate', () => {
            const hash = window.location.hash.replace('#', '').trim();
            if (hash) {
                openModal(hash, false);
            } else {
                closeModal();
            }
        });
        //]]>
    </script>
</body>
</html>
"""

    xml_final = xml_template.replace("__ARTIST_NAME__", html.escape(artist_name))
    xml_final = xml_final.replace("__ARTIST_EMAIL__", html.escape(artist_email))
    xml_final = xml_final.replace("__INSTAGRAM_HANDLE__", html.escape(instagram_handle))
    xml_final = xml_final.replace("__CATALOG_COUNT__", str(catalog_count))
    xml_final = xml_final.replace("__CARDS_CONTENT__", cards_joined)
    xml_final = xml_final.replace("__CATALOG_JSON__", catalog_json_str)
    xml_final = xml_final.replace("__IMG_BASE__", img_base)

    entity_replacements = {
        "&copy;": "&#169;",
        "&times;": "&#215;",
        "&bull;": "&#8226;",
        "&rsaquo;": "&#8250;",
        "&lsaquo;": "&#8249;",
        "&trade;": "&#8482;",
        "&reg;": "&#174;",
        "&mdash;": "&#8212;",
        "&ndash;": "&#8211;",
        "&hellip;": "&#8230;",
        "&nbsp;": "&#160;"
    }
    for ent, num in entity_replacements.items():
        xml_final = xml_final.replace(ent, num)

    with open(OUTPUT_XML, "w", encoding="utf-8") as f:
        f.write(xml_final)

    print(f"\n[OK] BERHASIL! Ditemukan {found_img_count} file gambar yang cocok presisi.")
    print(f"     📂 Tema Blogspot baru disimpan di: {OUTPUT_XML}")

if __name__ == "__main__":
    build_blogspot_xml()
