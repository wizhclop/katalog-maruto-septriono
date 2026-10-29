import os
import re
import subprocess

art_dir = r"F:\DATABASE_AI ART\ART"
web_dir = os.path.join(art_dir, "web_galeri")

# Cari repositori Git yang menampung katalog-maruto-septriono
repo_dir = None
for root_scan in [art_dir, r"F:\\DATABASE_AI ART", r"C:\Users"]:
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
    repo_dir = art_dir

print(f"[INFO] Folder Repositori Git ART: {repo_dir}")

# Daftar target file index.html yang harus diperbarui
target_files = []
for p in [
    os.path.join(repo_dir, "index.html"),
    os.path.join(repo_dir, "web_galeri", "index.html"),
    os.path.join(art_dir, "web_galeri", "index.html")
]:
    if os.path.exists(p) and p not in target_files:
        target_files.append(p)

for fpath in target_files:
    with open(fpath, "r", encoding="utf-8") as f:
        html = f.read()

    # 1. Pasang Badge Kunjungan Riil tepat di bawah Search Box
    badge_riil = """
        <div class="stats-bar" style="display:flex; justify-content:center; gap:10px; margin: 12px 0 20px 0; flex-wrap:wrap;">
            <div class="stat-badge" style="background:#161b22; border:1px solid #30363d; padding:5px 14px; border-radius:20px; font-size:0.82rem; color:#c9d1d9;">Karya Terarsip: <strong style="color:#58a6ff;">75 Karya Seni</strong></div>
            <div class="stat-badge" style="background:#161b22; border:1px solid #238636; padding:5px 14px; border-radius:20px; font-size:0.82rem; color:#3fb950;">👁️ Kunjungan Riil: <strong id="real-hits-count" style="color:#3fb950;">1</strong></div>
        </div>
    """

    # Ganti elemen lama Total Terarsip: 75 Karya Seni
    html = re.sub(r'<div[^>]*class=[\'"]stats-tag[\'"][^>]*>[\s\S]*?<\/div>', badge_riil, html)
    html = re.sub(r'<div[^>]*Total Terarsip: 75 Karya Seni[^<]*<\/div>', badge_riil, html)

    # 2. Ganti teks Lisensi / License $100 menjadi Digital Print Bebas Ongkir $100
    html = re.sub(r'Lisensi\s*<\/div>\s*<div[^>]*>\s*\$100', 'Digital Print Bebas Ongkir</div><div class="price-val" style="color:#3fb950; font-weight:bold;">$100', html, flags=re.I)
    html = re.sub(r'License\s*<\/div>\s*<div[^>]*>\s*\$100', 'Digital Print Bebas Ongkir</div><div class="price-val" style="color:#3fb950; font-weight:bold;">$100', html, flags=re.I)
    html = re.sub(r'<span class=[\'"]price-label[\'"]>Lisensi<\/span>\s*<span class=[\'"]price-val[\'"]>\$\s*100<\/span>', '<span class="price-label">Digital Print Bebas Ongkir</span><span class="price-val" style="color:#3fb950; font-weight:bold;">$100</span>', html, flags=re.I)
    html = re.sub(r'Lisensi<\/span>\s*<span[^>]*>\$100<\/span>', 'Digital Print Bebas Ongkir</span><span class="price-val" style="color:#3fb950; font-weight:bold;">$100</span>', html, flags=re.I)
    html = re.sub(r'Lisensi\s*<\/span>', 'Digital Print Bebas Ongkir</span>', html, flags=re.I)

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

    with open(fpath, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[OK] Diperbarui: {fpath}")

# Git stage dan push
try:
    subprocess.run(["git", "add", "-A"], cwd=repo_dir, check=True)
    subprocess.run(["git", "commit", "-m", "Perbarui tampilan: Munculkan Kunjungan Riil & ubah Lisensi jadi Digital Print Bebas Ongkir"], cwd=repo_dir, check=True)
    subprocess.run(["git", "push", "origin", "main"], cwd=repo_dir, check=True)
    print("\n[SUKSES] Perubahan berhasil di-push langsung ke Vercel!")
except Exception as e:
    print(f"[GIT INFO]: {e}")
