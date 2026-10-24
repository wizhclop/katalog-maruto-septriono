with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Pastikan style tombol kontak ditambahkan
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

# 2. Template markup tombol interaktif
tombol_markup = """
                <div class="contact-actions">
                    <a href="https://ig.me/m/maruto.septriono" target="_blank" rel="noopener noreferrer" class="btn-contact btn-ig">
                        💬 DM Instagram
                    </a>
                    <a href="mailto:studiowizhclop@gmail.com?subject=Order / License - ${encodeURIComponent(item.Judul || 'Artwork')} (${item.ID})&body=Halo Maruto Septriono,%0D%0A%0D%0ASaya tertarik dengan lisensi komersial karya:%0D%0A- Judul: ${encodeURIComponent(item.Judul || '')}%0D%0A- ID: ${item.ID}%0D%0A%0D%0AMohon informasi lebih lanjut.%0D%0A%0D%0ATerima kasih." class="btn-contact btn-mail">
                        ✉️ Order Email
                    </a>
                </div>"""

# 3. Cari penutup kotak komersial (pricing)
# Cari teks Bebas Ongkos Kirim atau Free Worldwide Shipping
pos = html.find('Bebas Ongkos Kirim')
if pos == -1:
    pos = html.find('Free Worldwide Shipping')

if pos != -1:
    # Cari tag penutup div terdekat setelah teks ongkos kirim
    end_first = html.find('</div>', pos)
    if end_first != -1:
        # Cari penutup div kontainer utama harga
        end_second = html.find('</div>', end_first + 6)
        if end_second != -1:
            insert_pos = end_second + 6
            html = html[:insert_pos] + tombol_markup + html[insert_pos:]
            print("SUKSES: Tombol DM dan Email berhasil dipasang!")
        else:
            print("Gagal menemukan div penutup kedua.")
    else:
        print("Gagal menemukan div penutup pertama.")
else:
    print("Teks referensi ongkos kirim tidak ditemukan.")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)
