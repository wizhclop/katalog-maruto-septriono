import os
import json
import re
import subprocess

art_dir = r"F:\DATABASE_AI ART\ART"
web_dir = os.path.join(art_dir, "web_galeri")
catalog_path = os.path.join(art_dir, "art_catalog.json")
index_html_path = os.path.join(web_dir, "index.html")

if not os.path.exists(catalog_path):
    print("[ERROR] art_catalog.json tidak ditemukan!")
    exit(1)

with open(catalog_path, "r", encoding="utf-8-sig") as f:
    catalog = json.load(f)

def get_num(item):
    m = re.search(r"(\d+)", str(item.get("ID", "")))
    return int(m.group(1)) if m else 0

catalog.sort(key=get_num, reverse=True)
total_karya = len(catalog)

cards_list = []
for item in catalog:
    item_id = str(item.get("ID", ""))
    judul = str(item.get("Judul", "Tanpa Judul"))
    tahun = str(item.get("Tahun", 2026))
    ukuran = str(item.get("Ukuran", "Standar"))
    media = str(item.get("Media", "Tinta di atas kertas"))
    statement = str(item.get("artist_statement_id", item.get("artist_statement", "")))
    kuratorial = str(item.get("deskripsi_kuratorial", ""))
    
    img_name = f"{item_id}.jpg"
    
    s_title = judul.replace("'", "\\'").replace('"', '&quot;')
    s_stmt = statement.replace("'", "\\'").replace('"', '&quot;')
    s_kur = kuratorial.replace("'", "\\'").replace('"', '&quot;')

    card = f"""
        <div class="card" id="{item_id}">
            <div class="card-thumb">
                <span class="card-badge">{item_id}</span>
                <span class="card-year">{tahun}</span>
                <img src="images/{img_name}" alt="{s_title}" loading="lazy" onerror="this.onerror=null;this.src='https://katalog-maruto-septriono.vercel.app/images/{img_name}';">
            </div>
            <div class="card-body">
                <h3 class="card-title">{judul}</h3>
                <div class="card-meta"><span>{ukuran}</span> • <span>{media}</span></div>
                <div class="card-price-row">
                    <div>
                        <div class="price-label">Soft Files</div>
                        <div class="price-val">$250</div>
                    </div>
                    <div style="text-align: right;">
                        <div class="price-label">Digital Print Bebas Ongkir</div>
                        <div class="shipping-val">$100</div>
                    </div>
                </div>
                <div class="card-actions">
                    <a href="https://ig.me/m/maruto.septriono?text=Halo%20Mas%20Maruto,%20saya%20tertarik%20dengan%20karya%20{item_id}%20di%20Vercel" target="_blank" class="btn-action btn-dm">✉ DM</a>
                    <a href="mailto:kirimdoa@gmail.com?subject=[VERCEL%20INQUIRY]%20Karya%20{item_id}%20-%20{s_title}&body=Halo%20Maruto%20Septriono,%0D%0ASaya%20tertarik%20dengan%20karya%20{item_id}%20di%20katalog-maruto-septriono.vercel.app/%23{item_id}" class="btn-action btn-email">✉ Beli via Email</a>
                </div>
                <div class="statement-box">
                    "{statement}"
                </div>
                <div class="card-footer-links">
                    <span class="btn-kuratorial" onclick="bukaModalKuratorial('{item_id}', '{s_title}', '{s_stmt}', '{s_kur}')">Kuratorial &rsaquo;</span>
                    <span class="btn-copy-link" onclick="salinLink('{item_id}')">🔗 Salin Link</span>
                </div>
            </div>
        </div>"""
    cards_list.append(card)

cards_html = "\n".join(cards_list)

template_html = """<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Katalog Karya Maruto Septriono</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { background: #0d1117; color: #e6edf3; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; padding-bottom: 60px; }
        .goog-te-banner-frame.skiptranslate, .goog-te-banner-frame { display: none !important; }
        #goog-gt-tt, .goog-te-balloon-frame { display: none !important; }
        .goog-text-highlight { background: none !important; box-shadow: none !important; }
        #google_translate_element { display: none; }
        header { text-align: center; padding: 25px 12px 15px; position: relative; }
        .lang-switch { display: inline-flex; gap: 4px; background: #161b22; border: 1px solid #30363d; border-radius: 20px; padding: 3px; margin-bottom: 12px; }
        .lang-btn { background: transparent; border: none; color: #8b949e; padding: 5px 14px; font-size: 0.78rem; font-weight: bold; border-radius: 16px; cursor: pointer; transition: all 0.2s; }
        .lang-btn.active { background: #1f6feb; color: #fff; }
        header h1 { font-size: 1.8rem; color: #58a6ff; margin-bottom: 6px; }
        header p { font-size: 0.9rem; color: #8b949e; margin-bottom: 12px; }
        .stats-bar { display: flex; justify-content: center; gap: 8px; flex-wrap: wrap; margin-bottom: 10px; }
        .stat-badge { background: #161b22; border: 1px solid #30363d; padding: 5px 12px; border-radius: 20px; font-size: 0.8rem; color: #c9d1d9; }
        .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 16px; max-width: 1200px; margin: 20px auto; padding: 0 12px; }
        .card { background: #161b22; border: 1px solid #30363d; border-radius: 10px; overflow: hidden; display: flex; flex-direction: column; transition: transform 0.2s; width: 100%; }
        .card:hover { transform: translateY(-3px); border-color: #58a6ff; }
        .card-thumb { position: relative; width: 100%; aspect-ratio: 1/1.2; background: #010409; overflow: hidden; display: flex; align-items: center; justify-content: center; }
        .card-thumb img { width: 100%; height: 100%; object-fit: contain; }
        .card-badge { position: absolute; top: 8px; left: 8px; background: #1f6feb; color: #fff; font-size: 0.7rem; font-weight: bold; padding: 2px 7px; border-radius: 5px; }
        .card-year { position: absolute; top: 8px; right: 8px; background: rgba(0,0,0,0.6); color: #fff; font-size: 0.7rem; padding: 2px 7px; border-radius: 5px; }
        .card-body { padding: 12px; display: flex; flex-direction: column; flex-grow: 1; }
        .card-title { font-size: 1.05rem; color: #fff; margin-bottom: 4px; }
        .card-meta { font-size: 0.75rem; color: #8b949e; margin-bottom: 10px; }
        .card-price-row { display: flex; justify-content: space-between; background: #0d1117; padding: 6px 10px; border-radius: 6px; margin-bottom: 10px; }
        .price-label { font-size: 0.65rem; color: #8b949e; }
        .price-val { font-size: 0.95rem; font-weight: bold; color: #58a6ff; }
        .shipping-val { font-size: 0.85rem; font-weight: bold; color: #3fb950; }
        .card-actions { display: flex; gap: 6px; margin-bottom: 10px; }
        .btn-action { flex: 1; text-align: center; padding: 6px 3px; border-radius: 6px; text-decoration: none; font-size: 0.75rem; font-weight: 600; color: #fff; }
        .btn-dm { background: #e1306c; }
        .btn-email { background: #238636; }
        .statement-box { background: rgba(255,255,255,0.03); border-left: 2px solid #58a6ff; padding: 6px 8px; font-size: 0.78rem; font-style: italic; color: #c9d1d9; margin-bottom: 10px; line-height: 1.35; }
        .card-footer-links { display: flex; justify-content: space-between; align-items: center; border-top: 1px solid #21262d; padding-top: 8px; margin-top: auto; font-size: 0.75rem; }
        .btn-kuratorial { color: #58a6ff; cursor: pointer; }
        .btn-copy-link { color: #8b949e; cursor: pointer; }
        .modal { display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.85); z-index: 999999; align-items: center; justify-content: center; padding: 15px; }
        .modal-box { background: #161b22; border: 1px solid #38bdf8; border-radius: 12px; width: 100%; max-width: 480px; padding: 20px; position: relative; color: #e6edf3; }
        .modal-close { position: absolute; top: 10px; right: 14px; font-size: 24px; color: #8b949e; cursor: pointer; font-weight: bold; }
        @media screen and (max-width: 768px) {
            .grid { grid-template-columns: repeat(2, 1fr) !important; gap: 8px !important; padding: 0 6px !important; }
            .card-body { padding: 8px 6px; }
            .card-title { font-size: 0.85rem; line-height: 1.2; margin-bottom: 2px; }
            .card-meta { font-size: 0.65rem; margin-bottom: 6px; }
            .card-price-row { padding: 4px 6px; margin-bottom: 6px; }
            .price-val { font-size: 0.85rem; }
            .shipping-val { font-size: 0.75rem; }
            .card-actions { flex-direction: column; gap: 4px; margin-bottom: 6px; }
            .btn-action { padding: 4px 2px; font-size: 0.68rem; }
            .statement-box { font-size: 0.68rem; padding: 4px 6px; margin-bottom: 6px; line-height: 1.25; }
            .card-footer-links { font-size: 0.68rem; padding-top: 6px; }
        }
    </style>
</head>
<body>
    <div id="google_translate_element"></div>
    <header>
        <div class="lang-switch">
            <button class="lang-btn active" id="btn-id" onclick="gantiBahasa('id')">🇮🇩 ID</button>
            <button class="lang-btn" id="btn-en" onclick="gantiBahasa('en')">🇬🇧 EN</button>
        </div>
        <h1>Katalog Karya Maruto Septriono</h1>
        <p>Arsip Digital Portofolio & Etalase Komersial Internasional</p>
        <div class="stats-bar">
            <div class="stat-badge">Karya Terarsip: <strong style="color:#58a6ff;">__TOTAL_KARYA__ Karya Seni</strong></div>
            <div class="stat-badge" style="border-color: #238636; color: #3fb950;">👁️ Kunjungan Riil: <strong id="real-hits-count">1</strong></div>
        </div>
    </header>

    <div class="grid">
__CARDS_GRID__
    </div>

    <div class="modal" id="modalKuratorial">
        <div class="modal-box">
            <span class="modal-close" onclick="tutupModal('modalKuratorial')">&times;</span>
            <h3 id="kurTitle" style="color:#58a6ff; margin-bottom:6px;">Ulasan Kuratorial</h3>
            <p id="kurMeta" style="font-size:0.78rem; color:#8b949e; margin-bottom:12px;"></p>
            <div id="kurStatement" style="font-style:italic; border-left:2px solid #58a6ff; padding-left:10px; margin-bottom:12px; color:#c9d1d9; font-size:0.85rem;"></div>
            <div id="kurText" style="line-height:1.5; font-size:0.88rem; color:#e6edf3; max-height:50vh; overflow-y:auto;"></div>
            <div style="margin-top:15px; text-align:right;">
                <button onclick="tutupModal('modalKuratorial')" style="background:#30363d; border:none; color:#fff; padding:6px 16px; border-radius:6px; cursor:pointer;">Tutup</button>
            </div>
        </div>
    </div>

    <script type="text/javascript">
        function googleTranslateElementInit() {
            new google.translate.TranslateElement({ pageLanguage: 'id', includedLanguages: 'id,en', autoDisplay: false }, 'google_translate_element');
        }
    </script>
    <script type="text/javascript" src="//translate.google.com/translate_a/element.js?cb=googleTranslateElementInit"></script>

    <script>
        function gantiBahasa(lang) {
            document.getElementById('btn-id').classList.toggle('active', lang === 'id');
            document.getElementById('btn-en').classList.toggle('active', lang === 'en');
            var selectEl = document.querySelector('select.goog-te-combo');
            if (selectEl) {
                selectEl.value = lang;
                selectEl.dispatchEvent(new Event('change'));
            } else {
                document.cookie = "googtrans=/id/" + lang + "; path=/";
                window.location.reload();
            }
        }
        function bukaModalKuratorial(id, title, stmt, kur) {
            document.getElementById('kurTitle').innerText = title;
            document.getElementById('kurMeta').innerText = "Kode Arsip: " + id;
            document.getElementById('kurStatement').innerText = '"' + stmt + '"';
            document.getElementById('kurText').innerText = kur;
            document.getElementById('modalKuratorial').style.display = 'flex';
        }
        function tutupModal(id) { document.getElementById(id).style.display = 'none'; }
        function salinLink(id) {
            const url = window.location.origin + window.location.pathname + "#" + id;
            navigator.clipboard.writeText(url).then(() => alert("Link karya " + id + " berhasil disalin!"));
        }
        window.onclick = (e) => { if (e.target.classList.contains('modal')) e.target.style.display = 'none'; };
        window.addEventListener('DOMContentLoaded', () => {
            const hash = window.location.hash.replace('#', '');
            if (hash) {
                const el = document.getElementById(hash);
                if (el) { el.scrollIntoView({ behavior: 'smooth' }); el.style.borderColor = '#58a6ff'; }
            }
        });
    </script>
    <script data-goatcounter="https://katalog-maruto.goatcounter.com/count" async src="//gc.zgo.at/count.js"></script>
    <script>
        fetch("https://katalog-maruto.goatcounter.com/counter/" + encodeURIComponent(location.pathname) + ".json")
            .then(r => r.json())
            .then(data => {
                var el = document.getElementById("real-hits-count");
                if (el && data && data.count) el.innerText = data.count;
            }).catch(() => {});
    </script>
</body>
</html>"""

final_html = template_html.replace("__TOTAL_KARYA__", str(total_karya)).replace("__CARDS_GRID__", cards_html)

with open(index_html_path, "w", encoding="utf-8") as f:
    f.write(final_html)

print(f"[OK] web_galeri/index.html dirakit ({total_karya} karya).")

try:
    subprocess.run(["git", "add", "-A"], cwd=art_dir, check=True)
    subprocess.run(["git", "commit", "-m", f"Publish ART: Total {total_karya} karya live di Vercel"], cwd=art_dir, check=True)
    subprocess.run(["git", "push", "origin", "main"], cwd=art_dir, check=True)
    print("\n[SUKSES LENGKAP] Berhasil didorong ke GitHub & Vercel!")
except Exception as e:
    print(f"[GIT LOG]: {e}")
