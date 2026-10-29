import os
import re
import subprocess

art_dir = r"F:\DATABASE_AI ART\ART"
index_file = os.path.join(art_dir, "web_galeri", "index.html")

if not os.path.exists(index_file):
    print("[ERROR] web_galeri/index.html tidak ditemukan!")
    exit(1)

with open(index_file, "r", encoding="utf-8") as f:
    html = f.read()

# 1. Pasang Badge Kunjungan Riil
badge_riil = """
        <div class="stats-bar" style="display:flex; justify-content:center; gap:10px; margin: 12px 0 20px 0; flex-wrap:wrap;">
            <div class="stat-badge" style="background:#161b22; border:1px solid #30363d; padding:5px 14px; border-radius:20px; font-size:0.82rem; color:#c9d1d9;">Karya Terarsip: <strong style="color:#58a6ff;">75 Karya Seni</strong></div>
            <div class="stat-badge" style="background:#161b22; border:1px solid #238636; padding:5px 14px; border-radius:20px; font-size:0.82rem; color:#3fb950;">👁️ Kunjungan Riil: <strong id="real-hits-count" style="color:#3fb950;">1</strong></div>
        </div>
"""

# Ganti stats-tag atau total terarsip lama
if "stats-tag" in html:
    html = re.sub(r'<div class=[\'"]stats-tag[\'"]>[\s\S]*?<\/div>', badge_riil, html)
elif "Total Terarsip: 75 Karya Seni" in html:
    html = re.sub(r'<div[^>]*Total Terarsip: 75 Karya Seni[^<]*<\/div>', badge_riil, html)
elif "real-hits-count" not in html:
    html = html.replace('</header>', badge_riil + '\n</header>')

# 2. Ganti teks Lisensi / License $100 menjadi Digital Print Bebas Ongkir $100
html = re.sub(r'<span class=[\'"]price-label[\'"]>Lisensi<\/span>\s*<span class=[\'"]price-val[\'"]>\$\s*100<\/span>', '<span class="price-label">Digital Print Bebas Ongkir</span><span class="price-val" style="color:#3fb950;">$ 100</span>', html, flags=re.I)
html = re.sub(r'<span class=[\'"]price-label[\'"]>License<\/span>\s*<span class=[\'"]price-val[\'"]>\$\s*100<\/span>', '<span class="price-label">Digital Print Bebas Ongkir</span><span class="price-val" style="color:#3fb950;">$ 100</span>', html, flags=re.I)
html = re.sub(r'Lisensi\s*<\/div>\s*<div[^>]*>\s*\$100', 'Digital Print Bebas Ongkir</div><div class="price-val" style="color:#3fb950; font-weight:bold;">$100', html, flags=re.I)
html = re.sub(r'License\s*<\/div>\s*<div[^>]*>\s*\$100', 'Digital Print Bebas Ongkir</div><div class="price-val" style="color:#3fb950; font-weight:bold;">$100', html, flags=re.I)

# 3. Suntikkan pelacak real-time jika belum ada
script_pelacak = """
    <!-- Pelacak Real-Time Riil (GoatCounter) -->
    <script data-goatcounter="https://katalog-maruto.goatcounter.com/count" async src="//gc.zgo.at/count.js"></script>
    <script>
        fetch("https://katalog-maruto.goatcounter.com/counter/" + encodeURIComponent(location.pathname) + ".json")
            .then(r => r.json())
            .then(data => {
                var el = document.getElementById("real-hits-count");
                if (el && data && data.count) {
                    el.innerText = data.count;
                }
            }).catch(() => {});
    </script>
"""

if "goatcounter.com/count" not in html:
    html = html.replace("</body>", script_pelacak + "\n</body>")

with open(index_file, "w", encoding="utf-8") as f:
    f.write(html)

print("[1/2] web_galeri/index.html berhasil diubah!")

# 4. Git stage seluruh folder web_galeri dan push ke Vercel
try:
    subprocess.run(["git", "add", "web_galeri/index.html"], cwd=art_dir, check=True)
    subprocess.run(["git", "commit", "-m", "Deploy Vercel: Pasang badge Kunjungan Riil dan ganti Lisensi jadi Digital Print Bebas Ongkir $100"], cwd=art_dir, check=True)
    subprocess.run(["git", "push", "origin", "main"], cwd=art_dir, check=True)
    print("\n[2/2] [BERHASIL] Perubahan resmi terkirim dan tayang di Vercel!")
except Exception as e:
    print(f"[GIT INFO]: {e}")
