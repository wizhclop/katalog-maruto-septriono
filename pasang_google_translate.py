import os
import subprocess

BASE_DIR = r"F:\DATABASE_AI ART\ART"
HTML_PATH = os.path.join(BASE_DIR, "index.html")
if not os.path.exists(HTML_PATH):
    HTML_PATH = os.path.join(BASE_DIR, "web_galeri", "index.html")

print(f"[*] Memperbaiki file: {HTML_PATH}")

with open(HTML_PATH, "r", encoding="utf-8") as f:
    html = f.read()

# 1. Ganti tombol lama dan pasang widget resmi Google Translate
google_widget_code = """
    <!-- WIDGET GOOGLE TRANSLATE OTOMATIS -->
    <div id="google_translate_element" style="position: fixed; top: 15px; right: 20px; z-index: 9999;"></div>
    <script type="text/javascript">
      function googleTranslateElementInit() {
        new google.translate.TranslateElement({
          pageLanguage: 'id',
          includedLanguages: 'en,ja,de,fr,es,ko,zh-CN',
          layout: google.translate.TranslateElement.InlineLayout.SIMPLE,
          autoDisplay: false
        }, 'google_translate_element');
      }
    </script>
    <script type="text/javascript" src="//translate.google.com/translate_a/element.js?cb=googleTranslateElementInit"></script>
    <style>
      /* Rapikan tampilan Google Translate agar selaras dengan tema gelap */
      #google_translate_element select {
        background-color: #1e1e1e !important;
        color: #e0e0e0 !important;
        border: 1px solid #444 !important;
        padding: 6px 10px !important;
        border-radius: 6px !important;
        font-family: inherit !important;
        font-size: 13px !important;
        cursor: pointer;
      }
      .goog-te-gadget {
        color: #888 !important;
        font-size: 11px !important;
      }
      .goog-te-gadget .goog-te-combo {
        margin: 4px 0 !important;
      }
      .goog-logo-link {
        display: none !important;
      }
      .goog-te-banner-frame.skiptranslate {
        display: none !important;
      }
      body {
        top: 0px !important;
      }
    </style>
"""

# Hapus panggilan alert lama jika masih ada
html = html.replace('alert("Versi terjemahan bahasa Inggris kuratorial sedang disiapkan!");', '')
html = html.replace("alert('Versi terjemahan bahasa Inggris kuratorial sedang disiapkan!');", '')

# Ganti area tombol bahasa lama di navbar dengan widget Google
if 'id="google_translate_element"' not in html:
    if '</header>' in html:
        html = html.replace('</header>', google_widget_code + '\n</header>')
    elif '<body>' in html:
        html = html.replace('<body>', '<body>\n' + google_widget_code)
    else:
        html = google_widget_code + html

with open(HTML_PATH, "w", encoding="utf-8") as f:
    f.write(html)

print("[OK] Widget Google Translate berhasil dipasang ke index.html!")

# 2. Sinkronkan dan Dorong langsung ke GitHub & Vercel
subprocess.run(["git", "add", "."], cwd=BASE_DIR, check=True)
status = subprocess.run(["git", "status", "--porcelain"], cwd=BASE_DIR, capture_output=True, text=True)
if status.stdout.strip():
    subprocess.run(["git", "commit", "-m", "Integrasi resmi Google Translate otomatis untuk seluruh katalog"], cwd=BASE_DIR, check=True)
    subprocess.run(["git", "push", "origin", "main"], cwd=BASE_DIR, check=True)
    print("\n[BERHASIL] Web Galeri dengan Google Translate resmi sudah terbit di Vercel!")
else:
    print("\n[INFO] Berkas sudah dalam keadaan terunggah.")
