with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Pastikan style CSS tombol kontak terpasang
css_style = """
        .contact-actions {
            display: flex;
            gap: 10px;
            margin: 15px 0 10px 0;
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
tombol_markup = """Free Worldwide Shipping</div>
                </div>
                <div class="contact-actions">
                    <a href="https://ig.me/m/maruto.septriono" target="_blank" rel="noopener noreferrer" class="btn-contact btn-ig">
                        💬 DM Instagram
                    </a>
                    <a href="mailto:studiowizhclop@gmail.com?subject=Order / License - ${encodeURIComponent(item.Judul || 'Artwork')} (${item.ID})&body=Halo Maruto Septriono,%0D%0A%0D%0ASaya tertarik dengan lisensi komersial karya:%0D%0A- Judul: ${encodeURIComponent(item.Judul || '')}%0D%0A- ID: ${item.ID}%0D%0A%0D%0AMohon informasi lebih lanjut.%0D%0A%0D%0ATerima kasih." class="btn-contact btn-mail">
                        ✉️ Order Email
                    </a>
                </div>"""

# 3. Cari dan ganti target penutup div harga
if 'contact-actions' not in html or 'btn-ig' not in html:
    target = 'Free Worldwide Shipping</div>\n                </div>'
    if target in html:
        html = html.replace(target, tombol_markup, 1)
        print("SUKSES: Tombol kontak berhasil disuntikkan ke index.html!")
    else:
        # Jika ada spasi atau format newline berbeda
        target_alt = 'Free Worldwide Shipping</div>'
        idx = html.find(target_alt)
        if idx != -1:
            end_div = html.find('</div>', idx + len(target_alt))
            if end_div != -1:
                html = html[:idx] + tombol_markup + html[end_div + 6:]
                print("SUKSES (Metode Alternatif): Tombol kontak berhasil disuntikkan ke index.html!")
            else:
                print("Peringatan: Gagal menemukan penutup div harga.")
        else:
            print("Peringatan: Teks 'Free Worldwide Shipping' tidak ditemukan.")
else:
    print("Tombol kontak sudah terpasang di berkas index.html.")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)
