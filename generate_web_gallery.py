import os
import json
import shutil

CATALOG_PATH = r"F:\DATABASE_AI ART\ART\art_catalog.json"
SOURCE_IMAGE_DIR = r"F:\DATABASE_AI ART\ART\ART_70"
OUTPUT_DIR = r"F:\DATABASE_AI ART\ART\web_galeri"
OUTPUT_IMG_DIR = os.path.join(OUTPUT_DIR, "images")

os.makedirs(OUTPUT_IMG_DIR, exist_ok=True)

def build_gallery():
    print("==================================================")
    print("  MEMBANGUN GALERI WEB PORTOFOLIO SENI (GOTHIC)")
    print("==================================================")

    if not os.path.exists(CATALOG_PATH):
        print("ERROR: art_catalog.json tidak ditemukan!")
        return

    with open(CATALOG_PATH, "r", encoding="utf-8-sig") as f:
        catalog = json.load(f)

    # Urutkan karya secara terbalik (karya terbaru seperti ART-072 muncul paling atas)
    catalog_reversed = list(reversed(catalog))

    cards_html = []
    copied_count = 0

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

        # Format Tagar
        tags_badge = ""
        if raw_tags:
            for t in raw_tags.split(","):
                clean_t = t.strip().replace("#", "")
                if clean_t:
                    tags_badge += f'<span class="tag">#{clean_t}</span> '

        # Salin gambar ke direktori web jika ada
        src_img = os.path.join(SOURCE_IMAGE_DIR, filename)
        web_img_rel = f"images/{filename}"
        dst_img = os.path.join(OUTPUT_IMG_DIR, filename)

        if os.path.exists(src_img) and not os.path.exists(dst_img):
            try:
                shutil.copy2(src_img, dst_img)
                copied_count += 1
            except Exception as e:
                pass

        card = f"""
        <div class="art-card" onclick="openModal('{art_id}')">
            <div class="img-container">
                <img src="{web_img_rel}" alt="{title}" loading="lazy" onerror="this.src='https://via.placeholder.com/400x500/111/444?text=Karya+Seni'">
                <div class="art-id-badge">{art_id}</div>
            </div>
            <div class="card-info">
                <h3 class="art-title">{title}</h3>
                <p class="art-meta">{year} &bull; {media}</p>
                <p class="art-size">{size}</p>
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
    <title>Maruto Art Studio & Gallery</title>
    <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@500;700;900&family=Plus+Jakarta+Sans:wght@300;400;600&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-color: #0a0a0c;
            --surface-color: #121216;
            --card-color: #181820;
            --accent-gold: #c5a059;
            --accent-crimson: #8b1e2f;
            --text-main: #e8e8ed;
            --text-muted: #8e8e9f;
            --border-color: #272733;
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
            line-height: 1.6;
        }}

        header {{
            text-align: center;
            padding: 80px 20px 40px;
            background: radial-gradient(circle at center, #1c1524 0%, var(--bg-color) 70%);
            border-bottom: 1px solid var(--border-color);
        }}

        header h1 {{
            font-family: 'Cinzel', serif;
            font-size: 2.8rem;
            letter-spacing: 4px;
            color: var(--accent-gold);
            text-transform: uppercase;
            margin-bottom: 8px;
        }}

        header p.subtitle {{
            font-size: 1.1rem;
            color: var(--text-muted);
            letter-spacing: 2px;
            text-transform: uppercase;
        }}

        .stats-bar {{
            margin-top: 25px;
            display: inline-block;
            padding: 8px 24px;
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid var(--border-color);
            border-radius: 30px;
            font-size: 0.9rem;
            color: var(--accent-gold);
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 50px 25px;
        }}

        /* Masonry Grid */
        .gallery-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 30px;
        }}

        .art-card {{
            background: var(--card-color);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            overflow: hidden;
            transition: all 0.3s ease;
            cursor: pointer;
            display: flex;
            flex-direction: column;
        }}

        .art-card:hover {{
            transform: translateY(-8px);
            border-color: var(--accent-gold);
            box-shadow: 0 15px 30px rgba(0, 0, 0, 0.6);
        }}

        .img-container {{
            position: relative;
            background: #000;
            width: 100%;
            height: 380px;
            overflow: hidden;
        }}

        .img-container img {{
            width: 100%;
            height: 100%;
            object-fit: cover;
            transition: transform 0.5s ease;
        }}

        .art-card:hover .img-container img {{
            transform: scale(1.05);
        }}

        .art-id-badge {{
            position: absolute;
            top: 12px;
            left: 12px;
            background: rgba(10, 10, 12, 0.85);
            color: var(--accent-gold);
            border: 1px solid rgba(197, 160, 89, 0.3);
            padding: 4px 10px;
            font-size: 0.75rem;
            font-family: 'Cinzel', serif;
            font-weight: 700;
            border-radius: 4px;
            backdrop-filter: blur(4px);
        }}

        .card-info {{
            padding: 20px;
            flex-grow: 1;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }}

        .art-title {{
            font-family: 'Cinzel', serif;
            font-size: 1.2rem;
            color: #fff;
            margin-bottom: 6px;
        }}

        .art-meta {{
            font-size: 0.85rem;
            color: var(--text-muted);
            margin-bottom: 4px;
        }}

        .art-size {{
            font-size: 0.8rem;
            color: var(--accent-gold);
            font-weight: 600;
        }}

        /* MODAL POP-UP */
        .modal {{
            display: none;
            position: fixed;
            z-index: 9999;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(5, 5, 8, 0.95);
            backdrop-filter: blur(8px);
            align-items: center;
            justify-content: center;
            padding: 20px;
        }}

        .modal-content {{
            background: var(--surface-color);
            border: 1px solid var(--accent-gold);
            border-radius: 12px;
            max-width: 1000px;
            width: 100%;
            max-height: 90vh;
            overflow-y: auto;
            display: grid;
            grid-template-columns: 1fr 1fr;
            box-shadow: 0 25px 50px rgba(0,0,0,0.8);
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
            transition: color 0.2s;
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
            gap: 16px;
        }}

        .modal-id {{
            font-family: 'Cinzel', serif;
            color: var(--accent-gold);
            font-size: 0.9rem;
            letter-spacing: 2px;
        }}

        .modal-title {{
            font-family: 'Cinzel', serif;
            font-size: 1.8rem;
            color: #fff;
            line-height: 1.3;
        }}

        .modal-specs {{
            border-top: 1px solid var(--border-color);
            border-bottom: 1px solid var(--border-color);
            padding: 12px 0;
            display: flex;
            flex-direction: column;
            gap: 6px;
            font-size: 0.9rem;
            color: var(--text-muted);
        }}

        .modal-specs span {{
            color: var(--text-main);
            font-weight: 600;
        }}

        .statement-box {{
            background: rgba(197, 160, 89, 0.05);
            border-left: 3px solid var(--accent-gold);
            padding: 12px 16px;
            font-style: italic;
            font-size: 0.95rem;
            color: #dedede;
        }}

        .curatorial-box {{
            font-size: 0.9rem;
            color: var(--text-muted);
            line-height: 1.7;
        }}

        .tag {{
            display: inline-block;
            background: rgba(255, 255, 255, 0.05);
            color: #b0b0c5;
            padding: 4px 10px;
            border-radius: 4px;
            font-size: 0.75rem;
            margin: 3px 2px;
            border: 1px solid var(--border-color);
        }}

        footer {{
            text-align: center;
            padding: 40px 20px;
            border-top: 1px solid var(--border-color);
            color: var(--text-muted);
            font-size: 0.85rem;
        }}

        @media (max-width: 900px) {{
            .modal-content {{
                grid-template-columns: 1fr;
            }}
            .modal-img-wrap {{
                height: 350px;
            }}
            header h1 {{
                font-size: 2rem;
            }}
        }}
    </style>
</head>
<body>

    <header>
        <h1>Maruto Art Studio</h1>
        <p class="subtitle">Official Curatorial Archive & Fine Art Portfolio</p>
        <div class="stats-bar">
            Total Terarsip: <strong>{len(catalog)} Karya Seni</strong>
        </div>
    </header>

    <main class="container">
        <div class="gallery-grid">
            {''.join(cards_html)}
        </div>
    </main>

    <!-- MODAL POPUP -->
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
                    <div>Media: <span id="mMedia">Tinta di atas kertas</span></div>
                    <div>Ukuran Fisik: <span id="mSize">38 cm x 42 cm</span></div>
                </div>
                <div class="statement-box" id="mStatement">
                    "Artist Statement..."
                </div>
                <div class="curatorial-box" id="mCuratorial">
                    Catatan kuratorial mendalam...
                </div>
                <div id="mTags"></div>
            </div>
        </div>
    </div>

    <footer>
        <p>&copy; 2026 Maruto Art Studio. Didukung oleh AI Kurator Lokal.</p>
    </footer>

    <script>
        const catalogData = {catalog_json_str};

        function openModal(artId) {{
            const item = catalogData.find(x => (x.ID === artId || x.id === artId));
            if (!item) return;

            document.getElementById('mId').innerText = item.ID || item.id || '';
            document.getElementById('mTitle').innerText = item.Judul || item.judul || 'Tanpa Judul';
            document.getElementById('mYear').innerText = item.Tahun || item.tahun || '-';
            document.getElementById('mMedia').innerText = item.Media || item.media || '-';
            document.getElementById('mSize').innerText = item.Ukuran || item.ukuran || '-';
            
            const filename = item.Nama_File || item.file || '';
            document.getElementById('mImg').src = 'images/' + filename;

            document.getElementById('mStatement').innerText = '"' + (item.artist_statement_id || 'Refleksi artistik.') + '"';
            document.getElementById('mCuratorial').innerText = item.deskripsi_kuratorial || 'Belum ada catatan kuratorial rinci.';

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
            if (e.target.id === 'artModal') {{
                closeModal();
            }}
        }}

        document.addEventListener('keydown', (e) => {{
            if (e.key === 'Escape') closeModal();
        }});
    </script>
</body>
</html>
"""

    index_html_path = os.path.join(OUTPUT_DIR, "index.html")
    with open(index_html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"[OK] Website portofolio berhasil dibangun di folder:")
    print(f"     📂 {OUTPUT_DIR}")
    print(f"[OK] Berkas gambar tersinkron: {copied_count} file baru.")
    print(f"[OK] Siap dibuka di browser atau dipublikasikan ke GitHub Pages!")

if __name__ == "__main__":
    build_gallery()
