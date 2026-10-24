import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Bersihkan sisa tombol yang menempel tidak teratur
html = re.sub(r'<div class="contact-actions">[\s\S]*?✉️ Order Email\s*</a>\s*</div>', '', html)

# 2. Pastikan CSS tombol kontak dan grid tetap rapi
style_tambahan = """
        .contact-actions {
            display: flex;
            gap: 8px;
            margin: 12px 0 8px 0;
            width: 100%;
        }
        .btn-contact {
            flex: 1;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            padding: 8px 6px;
            border-radius: 6px;
            font-size: 0.8rem;
            font-weight: 600;
            text-decoration: none;
            transition: all 0.2s ease;
            text-align: center;
            box-sizing: border-box;
        }
        .btn-ig {
            background: linear-gradient(45deg, #f09433 0%, #e6683c 25%, #dc2743 50%, #cc2366 75%, #bc1888 100%);
            color: #ffffff !important;
        }
        .btn-mail {
            background: #24292e;
            color: #ffffff !important;
            border: 1px solid rgba(255,255,255,0.25);
        }
        .btn-contact:hover {
            opacity: 0.88;
            transform: translateY(-1px);
        }
    </style>"""

if '.contact-actions' not in html:
    html = html.replace('</style>', style_tambahan)

# 3. Cari setiap kemunculan tag <p class="statement trans-block"
# lalu selipkan tombol kontak tepat di atasnya untuk setiap kartu secara berulang
def sisipkan_tombol(match):
    # Ambil konteks teks di belakang untuk mengekstrak judul karya terdekat jika ada
    pos = match.start()
    teks_sebelum = html[max(0, pos-2000):pos]
    
    # Cari judul dari alt="..." atau data-title="..." terdekat
    alt_match = list(re.finditer(r'alt="([^"]+)"', teks_sebelum))
    judul = alt_match[-1].group(1) if alt_match else "Artwork"
    
    # Cari ID karya terdekat (ART-xxx)
    id_match = list(re.finditer(r'(ART-\d+)', teks_sebelum))
    art_id = id_match[-1].group(1) if id_match else ""
    
    label_judul = f"{judul} ({art_id})" if art_id else judul
    
    tombol_html = f"""<div class="contact-actions">
                <a href="https://ig.me/m/maruto.septriono" target="_blank" rel="noopener noreferrer" class="btn-contact btn-ig">
                    💬 DM Instagram
                </a>
                <a href="mailto:studiowizhclop@gmail.com?subject=Order / License - {label_judul}&body=Halo Maruto Septriono,%0D%0A%0D%0ASaya tertarik dengan lisensi karya: {label_judul}.%0D%0AMohon informasi ketersediaannya.%0D%0A%0D%0ATerima kasih." class="btn-contact btn-mail">
                    ✉️ Order Email
                </a>
            </div>
            """
    return tombol_html + match.group(0)

pattern_target = re.compile(r'<p class="statement trans-block"')
total_kartu = len(pattern_target.findall(html))
print(f"Ditemukan {total_kartu} titik kartu karya.")

html_hasil = pattern_target.sub(sisipkan_tombol, html)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html_hasil)

print("BERHASIL: Grid kartu telah dipulihkan dan tombol kontak aktif di SEMUA kartu!")
