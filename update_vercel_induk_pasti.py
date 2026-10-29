import os
import re
import subprocess

# Cari folder repositori Git katalog-maruto-septriono yang aktif
repo_dir = None
for root_scan in [r"C:\Users", r"F:\\"]:
    if os.path.exists(root_scan):
        for root, dirs, files in os.walk(root_scan):
            if ".git" in dirs:
                cfg = os.path.join(root, ".git", "config")
                if os.path.exists(cfg):
                    try:
                        with open(cfg, "r", encoding="utf-8", errors="ignore") as f:
                            if "katalog-maruto-septriono" in f.read():
                                repo_dir = root
                                break
                    except Exception:
                        pass
        if repo_dir:
            break

if not repo_dir:
    repo_dir = r"F:\DATABASE_AI ART\ART\web_galeri"

print(f"[INFO] Folder Repositori Git: {repo_dir}")

index_file = os.path.join(repo_dir, "index.html")
if not os.path.exists(index_file):
    print("[ERROR] index.html tidak ditemukan di repositori!")
    exit(1)

with open(index_file, "r", encoding="utf-8") as f:
    html = f.read()

# 1. Pasang Badge Kunjungan Riil tepat di bawah Total Terarsip / Search Box
badge_riil = """
        <div class="stats-bar" style="display:flex; justify-content:center; gap:10px; margin: 12px 0 20px 0; flex-wrap:wrap;">
            <div class="stat-badge" style="background:#161b22; border:1px solid #30363d; padding:5px 14px; border-radius:20px; font-size:0.82rem; color:#c9d1d9;">Karya Terarsip: <strong style="color:#58a6ff;">75 Karya</strong></div>
            <div class="stat-badge" style="background:#161b22; border:1px solid #238636; padding:5px 14px; border-radius:20px; font-size:0.82rem; color:#3fb950;">👁️ Kunjungan Riil: <strong id="real-hits-count" style="color:#3fb950;">1</strong></div>
        </div>
"""

# Ganti tombol lama 'Total Terarsip: 75 Karya Seni'
if "Total Terarsip: 75 Karya Seni" in html:
    html = re.sub(r'<div[^>]*Total Terarsip: 75 Karya Seni[^<]*<\/div>', badge_riil, html)
elif "real-hits-count" not in html:
    # Sisipkan tepat di bawah form pencarian
    html = html.replace('</header>', badge_riil + '\n</header>')

# 2. Ganti Label Harga: 'Lisensi $100' / 'License $100' menjadi 'Digital Print Bebas Ongkir $100'
html = re.sub(r'Lisensi\s*<\/div>\s*<div[^>]*>\s*\$100', 'Digital Print Bebas Ongkir</div><div class="price-val" style="color:#3fb950; font-weight:bold;">$100', html, flags=re.I)
html = re.sub(r'License\s*<\/div>\s*<div[^>]*>\s*\$100', 'Digital Print Bebas Ongkir</div><div class="price-val" style="color:#3fb950; font-weight:bold;">$100', html, flags=re.I)

# 3. Pasang Pelacak Riil GoatCounter sebelum </body>
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

print("[SUKSES] index.html berhasil diperbarui dengan tombol Kunjungan Riil dan Digital Print!")

# Git push langsung ke Vercel
try:
    subprocess.run(["git", "add", "index.html"], cwd=repo_dir, check=True)
    subprocess.run(["git", "commit", "-m", "Deploy Vercel: Tampilkan Kunjungan Riil & ubah label Digital Print Bebas Ongkir $100"], cwd=repo_dir, check=True)
    subprocess.run(["git", "push", "origin", "main"], cwd=repo_dir, check=True)
    print("\n[PUSH BERHASIL] Perubahan resmi dikirim ke Vercel!")
except Exception as e:
    print(f"[GIT ERROR]: {e}")
