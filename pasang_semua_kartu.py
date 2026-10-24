import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Pastikan style CSS tombol kontak terpasang
css_style = """
        .contact-actions {
            display: flex;
            gap: 10px;
            margin: 14px 0 10px 0;
        }
        .btn-contact {
            flex: 1;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            padding: 9px 8px;
            border-radius: 6px;
            font-size: 0.82rem;
            font-weight: 600;
            text-decoration: none;
            transition: all 0.2s ease;
            text-align: center;
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
            opacity: 0.9;
            transform: translateY(-1px);
        }
    </style>"""

if '.contact-actions' not in html:
    html = html.replace('</style>', css_style)

# 2. Bersihkan dulu blok contact-actions yang sempat terpasang di ART-001 agar rapi
html = re.sub(r'\s*<div class="contact-actions">[\s\S]*?</div>\s*</div>\s*(?=<p class="statement)', '', html)

# 3. Fungsi untuk menyisipkan tombol interaktif ke setiap kartu secara dinamis (mengambil judul karya dari tiap kartu)
def replace_card(match):
    full_card = match.group(0)
    
    # Ambil judul karya dari atribut data-title atau dari tag alt gambar
    m_title = re.search(r'data-title="([^"]+)"', full_card, re.I)
    title = m_title.group(1).title() if m_title else "Artwork"
    
    # Ambil ID karya (misal ART-001)
    m_id = re.search(r'(ART-\d+)', full_card)
    art_id = m_id.group(1) if m_id else ""
    
    # Template tombol kontak khusus untuk karya ini
    buttons = f"""
                <div class="contact-actions">
                    <a href="https://ig.me/m/maruto.septriono" target="_blank" rel="noopener noreferrer" class="btn-contact btn-ig">
                        💬 DM Instagram
                    </a>
                    <a href="mailto:studiowizhclop@gmail.com?subject=Order / License - {title} ({art_id})&body=Halo Maruto Septriono,%0D%0A%0D%0ASaya tertarik dengan lisensi komersial untuk karya: {title} ({art_id}).%0D%0AMohon informasi ketersediaannya.%0D%0A%0D%0ATerima kasih." class="btn-contact btn-mail">
                        ✉️ Order Email
                    </a>
                </div>"""
    
    # Sisipkan tombol tepat sebelum teks artist statement
    sub_pattern = r'(</div>\s*</div>\s*)(<p class="statement)'
    return re.sub(sub_pattern, r'\1' + buttons + r'\n            \2', full_card, count=1)

# Pola pembungkus kartu dari awal <div class="card" hingga penutupnya
card_pattern = re.compile(r'<div class="card"[\s\S]*?</div>\s*</div>\s*</div>', re.M)

cards_found = len(card_pattern.findall(html))
print(f"Mendeteksi {cards_found} kartu karya di index.html...")

html_updated = card_pattern.sub(replace_card, html)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html_updated)

print("SUKSES: Tombol DM Instagram dan Order Email terpasang di SEMUA kartu karya!")
