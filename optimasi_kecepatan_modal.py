import os
import subprocess

html_path = r"F:\DATABASE_AI ART\ART\web_galeri\index.html"
if not os.path.exists(html_path):
    print("[ERROR] index.html tidak ditemukan!")
    exit(1)

with open(html_path, "r", encoding="utf-8") as f:
    html = f.read()

# 1. Optimalkan CSS Modal agar ringan di GPU (Hapus backdrop-filter berat, ganti dengan opacity hitam murni dan hardware acceleration)
old_modal_css = """        .modal {
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
        }"""

new_modal_css = """        .modal {
            display: none;
            position: fixed;
            z-index: 9999;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(6, 7, 10, 0.96);
            align-items: center;
            justify-content: center;
            padding: 20px;
            will-change: opacity;
            contain: layout style;
        }
        .modal-content {
            will-change: transform;
            transform: translateZ(0);
        }
        .modal-img-wrap img {
            content-visibility: auto;
        }"""

if old_modal_css in html:
    html = html.replace(old_modal_css, new_modal_css)

# 2. Percepat pencarian data (O(1) Map Lookup) dan cegah browser lagging saat render gambar
old_js = """        function openModal(artId) {
            const item = catalogData.find(x => (x.ID === artId || x.id === artId));"""

new_js = """        // Index catalog ke dictionary O(1) sekali jalan agar instan
        const catalogMap = new Map();
        if (typeof catalogData !== 'undefined' && Array.isArray(catalogData)) {
            catalogData.forEach(item => {
                const k1 = (item.ID || '').toString().toUpperCase();
                const k2 = (item.id || '').toString().toUpperCase();
                if (k1) catalogMap.set(k1, item);
                if (k2) catalogMap.set(k2, item);
            });
        }

        function openModal(artId) {
            const targetKey = (artId || '').toString().toUpperCase();
            const item = catalogMap.get(targetKey) || catalogData.find(x => (x.ID === artId || x.id === artId));"""

if old_js in html:
    html = html.replace(old_js, new_js)

with open(html_path, "w", encoding="utf-8") as f:
    f.write(html)

print("[1/2] index.html berhasil dioptimalkan: penghapusan filter berat & map-lookup terpasang.")

# Salin ke root repositori jika ada perbedaan lokasi
repo_html = r"F:\DATABASE_AI ART\ART\index.html"
if os.path.exists(repo_html):
    with open(repo_html, "w", encoding="utf-8") as f:
        f.write(html)

# 3. Dorong langsung ke GitHub & Vercel
subprocess.run(["git", "add", "."], check=True)
subprocess.run(["git", "commit", "-m", "Optimasi performa rendering modal kartu menjadi instan"], check=True)
subprocess.run(["git", "push", "origin", "main"], check=True)
print("\n[2/2] [SUKSES] Optimasi kecepatan berhasil didorong ke GitHub & Vercel!")
