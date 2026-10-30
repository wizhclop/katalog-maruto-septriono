import os
import subprocess
import re

html_path = r"F:\DATABASE_AI ART\ART\web_galeri\index.html"
if not os.path.exists(html_path):
    print("[ERROR] index.html tidak ditemukan!")
    exit(1)

with open(html_path, "r", encoding="utf-8") as f:
    html = f.read()

# 1. Tambahkan deklarasi rendering modern pada kartu seni
css_card_old = ".art-card {"
css_card_turbo = """.art-card {
            content-visibility: auto;
            contain-intrinsic-size: 320px 480px;"""

if "content-visibility: auto;" not in html and css_card_old in html:
    html = html.replace(css_card_old, css_card_turbo, 1)

# 2. Pasang decoding async pada seluruh tag gambar kartu agar CPU HP tidak freeze
html = re.sub(r'(<img\s+[^>]*?loading="lazy")', r'\1 decoding="async"', html)

# 3. Optimasi performa CSS khusus Mobile (Ringankan beban render GPU/CPU HP)
mobile_css_add = """
        /* TURBO ENGINE PERFORMANCE UNTUK HP */
        @media (max-width: 768px) {
            .art-card {
                contain-intrinsic-size: 160px 320px !important;
                box-shadow: none !important;
                transform: none !important;
                transition: border-color 0.15s ease !important;
            }
            .art-card:hover {
                transform: none !important;
                box-shadow: none !important;
            }
            .img-container img {
                transform: none !important;
                transition: none !important;
            }
            .gallery-grid {
                will-change: scroll-position;
            }
        }
"""

if "/* TURBO ENGINE PERFORMANCE UNTUK HP */" not in html:
    html = html.replace("</style>", mobile_css_add + "\n    </style>")

with open(html_path, "w", encoding="utf-8") as f:
    f.write(html)

print("[1/2] index.html sukses dipasangi akselerasi Content-Visibility & Async Decoding.")

# Salin juga ke berkas root repositori jika ada
repo_html = r"F:\DATABASE_AI ART\ART\index.html"
if os.path.exists(repo_html):
    with open(repo_html, "w", encoding="utf-8") as f:
        f.write(html)

# 4. Dorong ke GitHub & Vercel
subprocess.run(["git", "add", "."], check=True)
subprocess.run(["git", "commit", "-m", "Akselerasi performa rendering mobile: async decoding dan virtualisasi content-visibility"], check=True)
subprocess.run(["git", "push", "origin", "main"], check=True)

print("\n[2/2] [BERHASIL] Pembaruan performa kencang telah terbit ke GitHub & Vercel!")
