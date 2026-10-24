import os
import json
import shutil
import re

CATALOG_PATH = r"F:\DATABASE_AI ART\ART\art_catalog.json"
SOURCE_IMAGE_DIR = r"F:\DATABASE_AI ART\ART\ART_70"
OUTPUT_DIR = r"F:\DATABASE_AI ART\ART\web_galeri"
OUTPUT_IMG_DIR = os.path.join(OUTPUT_DIR, "images")

os.makedirs(OUTPUT_IMG_DIR, exist_ok=True)

MEDIA_TRANSLATIONS = {
    "tinta di atas kertas": "Ink on paper",
    "conte di atas kertas": "Conté crayon on paper",
    "akrilik di kanvas": "Acrylic on canvas",
    "cat minyak di kanvas": "Oil on canvas",
    "pensil di atas kertas": "Graphite pencil on paper",
    "pulpen di atas kertas": "Ballpoint pen on paper",
    "pen diatas kertas": "Pen on paper",
    "image generate ai": "AI Generated Digital Art",
    "ai generated": "AI Generated Digital Art"
}

def translate_media(media_str):
    if not media_str:
        return "-"
    m_clean = media_str.strip().lower()
    for id_term, en_term in MEDIA_TRANSLATIONS.items():
        if id_term in m_clean:
            return en_term
    return media_str

def build_bilingual_gallery():
    print("==================================================")
    print("  MEMBANGUN GALERI WEB HP 2-KOLOM (COMPACT GRID)  ")
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
        title_id = item.get("Judul") or item.get("judul") or "Tanpa Judul"
        title_en = item.get("Judul_EN") or item.get("title_en") or item.get("Title_EN") or title_id
        year = item.get("Tahun") or item.get("tahun") or "2026"
        size = item.get("Ukuran") or item.get("ukuran") or "-"
        media_id = item.get("Media") or item.get("media") or "-"
        media_en = translate_media(media_id)
        filename = item.get("Nama_File") or item.get("file") or ""

        stmt_id = (
            item.get("artist_statement_id") or 
            item.get("Artist_Statement") or 
            item.get("artist_statement") or 
            item.get("statement") or 
            item.get("Statement") or 
            ""
        ).strip()

        curat_id = (
            item.get("deskripsi_kuratorial") or 
            item.get("Deskripsi_Kuratorial") or 
            item.get("deskripsi") or 
            item.get("Deskripsi") or 
            ""
        ).strip()

        if not stmt_id:
            stmt_id = curat_id if curat_id else f"Eksplorasi visual dan perenungan bentuk mengenai dinamika eksistensial, diwujudkan melalui medium {media_id.lower()}."

        if not curat_id:
            curat_id = f"Karya {title_id} ({year}) merefleksikan kedalaman simbolik surealisme dalam tarikan garis dan kontras material {media_id.lower()}."

        stmt_en = (
            item.get("artist_statement_en") or 
            item.get("Artist_Statement_EN") or 
            item.get("statement_en") or 
            ""
        ).strip()

        curat_en = (
            item.get("deskripsi_kuratorial_en") or 
            item.get("Deskripsi_Kuratorial_EN") or 
            item.get("curatorial_en") or 
            ""
        ).strip()

        if not stmt_en:
            stmt_en = f"Visual contemplation and existential inquiry exploring consciousness, rendered meticulously through {media_en.lower()}."
        if not curat_en:
            curat_en = f"The piece '{title_en}' ({year}) investigates surrealist iconography, embodying intricate organic forms and architectural tensions."

        raw_tags = item.get("tags") or item.get("Tags") or "surealisgothic, gothic, art, drawing"

        item["Judul"] = title_id
        item["Judul_EN"] = title_en
        item["Media"] = media_id
        item["Media_EN"] = media_en
        item["artist_statement_id"] = stmt_id
        item["artist_statement_en"] = stmt_en
        item["deskripsi_kuratorial"] = curat_id
        item["deskripsi_kuratorial_en"] = curat_en

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
            if not os.path.exists(dst_img):
                shutil.copy2(src_img, dst_img)
            web_img_rel = f"images/{web_filename}"
            item["web_image"] = web_filename
            found_count += 1
        else:
            web_img_rel = "images/notfound.jpg"
            item["web_image"] = ""

        safe_stmt_id = (stmt_id[:135] + "...") if len(stmt_id) > 135 else stmt_id
        safe_stmt_en = (stmt_en[:135] + "...") if len(stmt_en) > 135 else stmt_en
        search_blob = f"{art_id} {title_id} {title_en} {media_id} {media_en} {year} {raw_tags}".lower()

        card = f"""
        <div class="art-card" data-search="{search_blob}" id="card-{art_id}">
            <div class="img-container" onclick="openModal('{art_id}')">
                <img src="{web_img_rel}" alt="{title_id}" loading="lazy" onerror="this.src='https://via.placeholder.com/400x500/181820/888?text=Maruto+Art'">
                <div class="art-badge-row">
                    <span class="badge badge-id">{art_id}</span>
                    <span class="badge badge-year">{year}</span>
                    <span class="badge badge-status" data-i18n="badge_status">Koleksi Pribadi</span>
                </div>
            </div>

            <div class="card-info">
                <h3 class="art-title" onclick="openModal('{art_id}')" data-title-id="{title_id}" data-title-en="{title_en}">{title_id}</h3>
                <p class="art-spec" data-spec-id="{size} &bull; {media_id}" data-spec-en="{size} &bull; {media_en}">{size} &bull; {media_id}</p>

                <div class="commercial-box">
                    <div class="price-col">
                        <span class="price-label" data-i18n="label_softfile">Soft File</span>
                        <span class="price-val">$ 250</span>
                    </div>
                    <div class="price-col">
                        <span class="price-label" data-i18n="label_license">Lisensi Cetak</span>
                        <span class="price-val">$ 100</span>
                    </div>
                </div>

                <div class="action-buttons">
                    <a href="https://instagram.com/marutoseptriono" target="_blank" class="btn btn-dm">
                        ✉ DM
                    </a>
                    <a href="mailto:marutoseptriono@gmail.com?subject=Inquiry {art_id} - {title_id}" class="btn btn-email" data-email-title="{title_id}">
                        ✉ Email
                    </a>
                </div>

                <div class="card-statement" onclick="openModal('{art_id}')" data-stmt-id='"{safe_stmt_id}"' data-stmt-en='"{safe_stmt_en}"'>
                    "{safe_stmt_id}"
                </div>

                <div class="card-footer-link" onclick="openModal('{art_id}')" data-i18n="btn_curatorial">
                    &bull; Catatan Kuratorial &rsaquo;
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
            --text-main: #f0f0f5;
            --text-muted: #9598a6;
            --border-color: #262938;
            --price-green: #38bdf8;
        }}

        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            background-color: var(--bg-color);
            color: var(--text-main);
            font-family: 'Plus Jakarta Sans', sans-serif;
            line-height: 1.4;
            overflow-x: hidden;
        }}

        .top-nav {{
            display: flex;
            justify-content: flex-end;
            padding: 10px 16px;
            background: #08080b;
            border-bottom: 1px solid var(--border-color);
        }}
        .lang-switch button {{
            background: #1b1d26; color: var(--text-muted); border: 1px solid var(--border-color);
            padding: 5px 12px; font-size: 0.8rem; cursor: pointer; border-radius: 4px; font-family: inherit; font-weight: 600; transition: all 0.2s;
        }}
        .lang-switch button.active {{ background: #0284c7; color: #fff; border-color: #0284c7; }}

        header {{
            text-align: center;
            padding: 35px 14px 20px;
            background: radial-gradient(circle at center, #1e1b29 0%, var(--bg-color) 75%);
            border-bottom: 1px solid var(--border-color);
        }}
        header h1 {{
            font-family: 'Cinzel', serif;
            font-size: 2.2rem;
            letter-spacing: 1.5px;
            color: #38bdf8;
            margin-bottom: 4px;
        }}
        header p.subtitle {{
            font-size: 0.9rem;
            color: var(--text-muted);
            letter-spacing: 0.5px;
            margin-bottom: 16px;
        }}

        .search-container {{
            max-width: 550px;
            width: 100%;
            margin: 0 auto;
        }}
        .search-container input {{
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
        }}
        .search-container input:focus {{ border-color: #38bdf8; box-shadow: 0 0 12px rgba(56, 189, 248, 0.2); }}

        .stats-tag {{
            display: inline-block;
            margin-top: 12px;
            font-size: 0.8rem;
            color: var(--accent-gold);
            background: rgba(197, 160, 89, 0.1);
            padding: 3px 12px;
            border-radius: 20px;
            border: 1px solid rgba(197, 160, 89, 0.25);
        }}

        .container {{
            max-width: 1440px;
            margin: 0 auto;
            padding: 24px 14px;
        }}
        .gallery-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
        }}

        .art-card {{
            background: var(--card-color);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            transition: transform 0.2s, border-color 0.2s;
        }}
        .art-card:hover {{ border-color: #38bdf8; transform: translateY(-3px); box-shadow: 0 10px 20px rgba(0,0,0,0.5); }}

        .img-container {{
            position: relative;
            background: #000;
            width: 100%;
            height: 320px;
            cursor: pointer;
            overflow: hidden;
        }}
        .img-container img {{
            width: 100%;
            height: 100%;
            object-fit: cover;
            transition: transform 0.3s ease;
        }}
        .art-card:hover .img-container img {{ transform: scale(1.03); }}

        .art-badge-row {{
            position: absolute;
            top: 8px;
            left: 8px;
            right: 8px;
            display: flex;
            gap: 4px;
            flex-wrap: wrap;
        }}
        .badge {{ padding: 2px 6px; font-size: 0.68rem; font-weight: 600; border-radius: 4px; backdrop-filter: blur(4px); }}
        .badge-id {{ background: #0284c7; color: #fff; }}
        .badge-year {{ background: #0369a1; color: #e0f2fe; }}
        .badge-status {{ background: rgba(30, 41, 59, 0.9); color: #94a3b8; border: 1px solid #475569; }}

        .card-info {{
            padding: 14px;
            display: flex;
            flex-direction: column;
            flex-grow: 1;
            background: var(--card-inner);
        }}
        .art-title {{
            font-family: 'Cinzel', serif;
            font-size: 1.05rem;
            color: #fff;
            margin-bottom: 3px;
            cursor: pointer;
            line-height: 1.3;
        }}
        .art-title:hover {{ color: #38bdf8; }}
        .art-spec {{ font-size: 0.75rem; color: var(--text-muted); margin-bottom: 10px; }}

        .commercial-box {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            background: #181b24;
            border: 1px solid var(--border-color);
            border-radius: 6px;
            padding: 8px;
            margin-bottom: 10px;
            gap: 6px;
        }}
        .price-col {{ display: flex; flex-direction: column; }}
        .price-label {{ font-size: 0.68rem; color: var(--text-muted); }}
        .price-val {{ font-size: 0.95rem; font-weight: 700; color: #38bdf8; }}

        .action-buttons {{ display: grid; grid-template-columns: 1fr 1fr; gap: 6px; margin-bottom: 10px; }}
        .btn {{ text-align: center; padding: 7px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 600; text-decoration: none; transition: opacity 0.2s; }}
        .btn:hover {{ opacity: 0.88; }}
        .btn-dm {{ background: linear-gradient(135deg, #e1306c, #fd1d1d); color: #fff; }}
        .btn-email {{ background: #272a38; color: #e2e8f0; border: 1px solid #3e445b; }}

        .card-statement {{
            font-size: 0.78rem;
            color: #b3b7c8;
            font-style: italic;
            margin-bottom: 10px;
            cursor: pointer;
            min-height: 42px;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
            line-height: 1.4;
        }}
        .card-footer-link {{ margin-top: auto; font-size: 0.72rem; color: #38bdf8; cursor: pointer; padding-top: 6px; border-top: 1px solid #1f2330; }}

        /* MODAL POPUP */
        .modal {{
            display: none;
            position: fixed;
            z-index: 9999;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(5, 6, 9, 0.95);
            backdrop-filter: blur(8px);
            align-items: center;
            justify-content: center;
            padding: 12px;
        }}
        .modal-content {{
            background: var(--surface-color);
            border: 1px solid var(--accent-gold);
            border-radius: 10px;
            max-width: 1000px;
            width: 100%;
            max-height: 90vh;
            overflow-y: auto;
            display: grid;
            grid-template-columns: 1fr 1fr;
            box-shadow: 0 20px 50px rgba(0,0,0,0.9);
            position: relative;
        }}
        .modal-close {{
            position: absolute;
            top: 10px;
            right: 14px;
            color: var(--text-muted);
            font-size: 1.8rem;
            cursor: pointer;
            z-index: 10;
        }}
        .modal-close:hover {{ color: #fff; }}
        .modal-img-wrap {{
            background: #000;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 14px;
        }}
        .modal-img-wrap img {{
            max-width: 100%;
            max-height: 70vh;
            object-fit: contain;
            border-radius: 4px;
        }}
        .modal-details {{
            padding: 24px 20px;
            display: flex;
            flex-direction: column;
            gap: 12px;
        }}
        .modal-id {{ font-family: 'Cinzel', serif; color: var(--accent-gold); font-size: 0.8rem; letter-spacing: 2px; }}
        .modal-title {{ font-family: 'Cinzel', serif; font-size: 1.5rem; color: #fff; line-height: 1.25; }}
        .modal-specs {{
            border-top: 1px solid var(--border-color);
            border-bottom: 1px solid var(--border-color);
            padding: 8px 0;
            font-size: 0.82rem;
            color: var(--text-muted);
            display: flex;
            flex-direction: column;
            gap: 4px;
        }}
        .modal-specs span {{ color: #fff; font-weight: 600; }}
        .modal-pricing-box {{
            background: #1a1e29;
            border: 1px solid #2d3448;
            padding: 10px;
            border-radius: 6px;
            display: flex;
            justify-content: space-around;
        }}
        .statement-box {{
            background: rgba(197, 160, 89, 0.05);
            border-left: 3px solid var(--accent-gold);
            padding: 8px 12px;
            font-style: italic;
            font-size: 0.85rem;
            color: #dedee5;
        }}
        .curatorial-box {{ font-size: 0.82rem; color: var(--text-muted); line-height: 1.55; }}
        .tag {{
            display: inline-block;
            background: rgba(255, 255, 255, 0.05);
            color: #b0b0c5;
            padding: 2px 7px;
            border-radius: 4px;
            font-size: 0.7rem;
            margin: 2px;
            border: 1px solid var(--border-color);
        }}
        footer {{ text-align: center; padding: 30px 14px; border-top: 1px solid var(--border-color); color: var(--text-muted); font-size: 0.8rem; }}

        /* ============================================================ */
        /* KHUSUS TAMPILAN HP (MOBILE COMPACT: 2 KOLOM SEPERTI WEB LAMA) */
        /* ============================================================ */
        @media (max-width: 768px) {{
            header {{ padding: 22px 10px 14px; }}
            header h1 {{ font-size: 1.35rem; }}
            header p.subtitle {{ font-size: 0.75rem; margin-bottom: 12px; }}
            .container {{ padding: 12px 6px; }}

            /* 2 KOLOM KARTU BERJAJAR DI HP */
            .gallery-grid {{
                grid-template-columns: repeat(2, 1fr);
                gap: 8px;
            }}

            /* TINGGI GAMBAR DI HP DIBUAT KOMPAK (CEPAT DI-SCROLL) */
            .img-container {{ height: 180px; }}

            .art-badge-row {{ top: 5px; left: 5px; right: 5px; gap: 3px; }}
            .badge {{ font-size: 0.6rem; padding: 2px 4px; }}
            .badge-status {{ display: none; }} /* Sembunyikan badge panjang di HP */

            .card-info {{ padding: 8px; }}
            .art-title {{ font-size: 0.85rem; margin-bottom: 2px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
            .art-spec {{ font-size: 0.68rem; margin-bottom: 6px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}

            .commercial-box {{ padding: 5px 6px; margin-bottom: 6px; gap: 4px; }}
            .price-label {{ font-size: 0.6rem; }}
            .price-val {{ font-size: 0.82rem; }}

            .action-buttons {{ gap: 4px; margin-bottom: 6px; }}
            .btn {{ padding: 5px 4px; font-size: 0.68rem; }}

            .card-statement {{
                font-size: 0.72rem;
                min-height: 32px;
                -webkit-line-clamp: 2;
                margin-bottom: 6px;
                line-height: 1.3;
            }}
            .card-footer-link {{ font-size: 0.65rem; padding-top: 4px; }}

            /* MODAL TETAP BESAR & DETAIL SAAT DIKLIK */
            .modal-content {{
                grid-template-columns: 1fr;
                max-height: 92vh;
            }}
            .modal-img-wrap {{
                height: 260px;
                padding: 8px;
            }}
            .modal-img-wrap img {{
                max-height: 240px;
            }}
            .modal-details {{ padding: 16px 14px; gap: 10px; }}
            .modal-title {{ font-size: 1.25rem; }}
        }}
    </style>
</head>
<body>

    <div class="top-nav">
        <div class="lang-switch">
            <button id="btnLangID" class="active" onclick="switchLanguage('ID')">ID (Indonesia)</button>
            <button id="btnLangEN" onclick="switchLanguage('EN')">EN (English)</button>
        </div>
    </div>

    <header>
        <h1 id="mainTitle">Katalog Karya Maruto Septriono</h1>
        <p class="subtitle" id="mainSubtitle">Arsip Digital, Portofolio & Etalase Komersial Internasional</p>

        <div class="search-container">
            <input type="text" id="searchInput" onkeyup="filterGallery()" placeholder="Cari judul karya, medium, tahun, atau ID (misal: ART-073, tinta)...">
        </div>

        <div class="stats-tag">
            <span id="txtTotal">Total Terarsip</span>: <strong>{len(catalog)} <span id="txtUnit">Karya Seni</span></strong>
        </div>
    </header>

    <main class="container">
        <div class="gallery-grid" id="galleryGrid">
            {''.join(cards_html)}
        </div>
    </main>

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
                    <div><span id="mYearLabel">Tahun</span>: <span id="mYear">2026</span></div>
                    <div><span id="mMediaLabel">Media</span>: <span id="mMedia">-</span></div>
                    <div><span id="mSizeLabel">Ukuran Fisik</span>: <span id="mSize">-</span></div>
                    <div><span id="mStatusLabel">Status Fisik</span>: <span style="color:#38bdf8;" id="mStatusVal">Koleksi Pribadi</span></div>
                </div>

                <div class="modal-pricing-box">
                    <div>
                        <small style="color:#94a3b8; display:block;" id="mP1Label">Soft File High-Res</small>
                        <strong style="color:#38bdf8; font-size:1.05rem;">$ 250</strong>
                    </div>
                    <div style="border-left:1px solid #334155; padding-left:14px;">
                        <small style="color:#94a3b8; display:block;" id="mP2Label">Lisensi Cetak Royalti</small>
                        <strong style="color:#38bdf8; font-size:1.05rem;">$ 100</strong>
                    </div>
                </div>

                <div class="statement-box" id="mStatement">"Artist Statement..."</div>
                <div class="curatorial-box" id="mCuratorial">Catatan kuratorial...</div>
                <div id="mTags"></div>

                <div class="action-buttons" style="margin-top:8px;">
                    <a id="mDmBtn" href="https://instagram.com/marutoseptriono" target="_blank" class="btn btn-dm">✉ DM Instagram</a>
                    <a id="mEmailBtn" href="#" class="btn btn-email">✉ Order via Email</a>
                </div>
            </div>
        </div>
    </div>

    <footer>
        <p id="footerTxt">&copy; 2026 Maruto Art Studio. Arsip Kuratorial & Portofolio Komersial Seniman.</p>
    </footer>

    <script>
        const catalogData = {catalog_json_str};
        let currentLang = 'ID';
        let currentModalArtId = null;

        const I18N = {{
            ID: {{
                mainTitle: "Katalog Karya Maruto Septriono",
                mainSubtitle: "Arsip Digital, Portofolio & Etalase Komersial Internasional",
                searchPlaceholder: "Cari judul karya, medium, tahun, atau ID (misal: ART-073, tinta)...",
                txtTotal: "Total Terarsip",
                txtUnit: "Karya Seni",
                badge_status: "Koleksi Pribadi",
                label_softfile: "Soft File",
                label_license: "Lisensi Cetak",
                btn_curatorial: "• Catatan Kuratorial ›",
                mYearLabel: "Tahun",
                mMediaLabel: "Media",
                mSizeLabel: "Ukuran Fisik",
                mStatusLabel: "Status Fisik",
                mStatusVal: "Koleksi Pribadi",
                mP1Label: "Soft File High-Res",
                mP2Label: "Lisensi Cetak Royalti",
                footerTxt: "© 2026 Maruto Art Studio. Arsip Kuratorial & Portofolio Komersial Seniman."
            }},
            EN: {{
                mainTitle: "Maruto Septriono Art Catalog",
                mainSubtitle: "Official Curatorial Archive & International Commercial Portfolio",
                searchPlaceholder: "Search artwork title, medium, year, or ID (e.g., ART-073, ink)...",
                txtTotal: "Total Archived",
                txtUnit: "Artworks",
                badge_status: "Private Collection",
                label_softfile: "Digital File",
                label_license: "Print License",
                btn_curatorial: "• Curatorial Notes ›",
                mYearLabel: "Year",
                mMediaLabel: "Medium",
                mSizeLabel: "Physical Dimensions",
                mStatusLabel: "Physical Status",
                mStatusVal: "Private Collection",
                mP1Label: "High-Res Digital File",
                mP2Label: "Commercial Print License",
                footerTxt: "© 2026 Maruto Art Studio. Curatorial Archive & Commercial Portfolio."
            }}
        }};

        function switchLanguage(lang) {{
            currentLang = lang;
            document.getElementById('btnLangID').className = (lang === 'ID' ? 'active' : '');
            document.getElementById('btnLangEN').className = (lang === 'EN' ? 'active' : '');

            const dict = I18N[lang];
            document.getElementById('mainTitle').innerText = dict.mainTitle;
            document.getElementById('mainSubtitle').innerText = dict.mainSubtitle;
            document.getElementById('searchInput').placeholder = dict.searchPlaceholder;
            document.getElementById('txtTotal').innerText = dict.txtTotal;
            document.getElementById('txtUnit').innerText = dict.txtUnit;
            document.getElementById('footerTxt').innerText = dict.footerTxt;

            document.querySelectorAll('[data-i18n]').forEach(el => {{
                const key = el.getAttribute('data-i18n');
                if (dict[key]) el.innerText = dict[key];
            }});

            document.querySelectorAll('.art-card').forEach(card => {{
                const titleEl = card.querySelector('.art-title');
                const specEl = card.querySelector('.art-spec');
                const stmtEl = card.querySelector('.card-statement');

                if (lang === 'EN') {{
                    titleEl.innerText = titleEl.getAttribute('data-title-en');
                    specEl.innerHTML = specEl.getAttribute('data-spec-en');
                    stmtEl.innerText = stmtEl.getAttribute('data-stmt-en');
                }} else {{
                    titleEl.innerText = titleEl.getAttribute('data-title-id');
                    specEl.innerHTML = specEl.getAttribute('data-spec-id');
                    stmtEl.innerText = stmtEl.getAttribute('data-stmt-id');
                }}
            }});

            if (currentModalArtId) renderModalData(currentModalArtId);
        }}

        function filterGallery() {{
            const query = document.getElementById('searchInput').value.toLowerCase().trim();
            const cards = document.querySelectorAll('.art-card');
            cards.forEach(card => {{
                const searchData = card.getAttribute('data-search') || '';
                card.style.display = searchData.includes(query) ? 'flex' : 'none';
            }});
        }}

        function renderModalData(artId) {{
            const item = catalogData.find(x => (x.ID === artId || x.id === artId));
            if (!item) return;

            const dict = I18N[currentLang];
            document.getElementById('mYearLabel').innerText = dict.mYearLabel;
            document.getElementById('mMediaLabel').innerText = dict.mMediaLabel;
            document.getElementById('mSizeLabel').innerText = dict.mSizeLabel;
            document.getElementById('mStatusLabel').innerText = dict.mStatusLabel;
            document.getElementById('mStatusVal').innerText = dict.mStatusVal;
            document.getElementById('mP1Label').innerText = dict.mP1Label;
            document.getElementById('mP2Label').innerText = dict.mP2Label;

            document.getElementById('mId').innerText = item.ID || item.id || '';
            const title = (currentLang === 'EN' ? (item.Judul_EN || item.Judul) : item.Judul) || 'Untitled';
            document.getElementById('mTitle').innerText = title;
            document.getElementById('mYear').innerText = item.Tahun || item.tahun || '-';
            document.getElementById('mMedia').innerText = (currentLang === 'EN' ? (item.Media_EN || item.Media) : item.Media) || '-';
            document.getElementById('mSize').innerText = item.Ukuran || item.ukuran || '-';

            const webImg = item.web_image || '';
            document.getElementById('mImg').src = webImg ? ('images/' + webImg) : '';

            const stmt = (currentLang === 'EN' ? (item.artist_statement_en || item.artist_statement_id) : item.artist_statement_id) || 'Visual contemplation.';
            const curat = (currentLang === 'EN' ? (item.deskripsi_kuratorial_en || item.deskripsi_kuratorial) : item.deskripsi_kuratorial) || 'No detailed curatorial notes yet.';

            document.getElementById('mStatement').innerText = '"' + stmt + '"';
            document.getElementById('mCuratorial').innerText = curat;

            document.getElementById('mEmailBtn').href = 'mailto:marutoseptriono@gmail.com?subject=Inquiry Artwork ' + (item.ID || '') + ' - ' + title;

            const tagsDiv = document.getElementById('mTags');
            tagsDiv.innerHTML = '';
            const tagSource = item.tags || item.Tags || '';
            if (tagSource) {{
                tagSource.split(',').forEach(t => {{
                    const clean = t.trim().replace('#', '');
                    if (clean) {{
                        const span = document.createElement('span');
                        span.className = 'tag';
                        span.innerText = '#' + clean;
                        tagsDiv.appendChild(span);
                    }}
                }});
            }}
        }}

        function openModal(artId) {{
            currentModalArtId = artId;
            renderModalData(artId);
            document.getElementById('artModal').style.display = 'flex';
            document.body.style.overflow = 'hidden';
        }}

        function closeModal() {{
            document.getElementById('artModal').style.display = 'none';
            document.body.style.overflow = 'auto';
            currentModalArtId = null;
        }}

        function closeModalOnOutside(e) {{
            if (e.target.id === 'artModal') closeModal();
        }}

        document.addEventListener('keydown', (e) => {{ if (e.key === 'Escape') closeModal(); }});
    </script>
</body>
</html>
"""

    with open(os.path.join(OUTPUT_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"[OK] Selesai! Web Galeri Compact 2-Kolom Mobile berhasil dibangun.")

if __name__ == "__main__":
    build_bilingual_gallery()
