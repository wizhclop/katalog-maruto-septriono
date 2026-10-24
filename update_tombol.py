with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Styling tombol kontak interaktif
style_inject = """
        .contact-actions {
            display: flex;
            gap: 8px;
            margin-top: 14px;
        }
        .btn-contact {
            flex: 1;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            padding: 9px 10px;
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
        .btn-ig:hover {
            opacity: 0.9;
            transform: translateY(-1px);
        }
        .btn-mail {
            background: #24292e;
            color: #ffffff !important;
            border: 1px solid rgba(255,255,255,0.2);
        }
        .btn-mail:hover {
            background: #3b424a;
            transform: translateY(-1px);
        }
    </style>"""

if '.contact-actions' not in content:
    content = content.replace('</style>', style_inject)

# 2. Template Tombol DM Instagram (@maruto.septriono) & Email (studiowizhclop@gmail.com)
btn_markup = """${item.deskripsi_kuratorial || ""}
                </p>
                <div class="contact-actions">
                    <a href="https://ig.me/m/maruto.septriono" target="_blank" rel="noopener noreferrer" class="btn-contact btn-ig">
                        💬 DM Instagram
                    </a>
                    <a href="mailto:studiowizhclop@gmail.com?subject=Inquiry / License Order - ${encodeURIComponent(item.Judul || 'Artwork')} (${item.ID})&body=Halo Maruto Septriono,%0D%0A%0D%0ASaya tertarik dengan lisensi karya seni:%0D%0A- Judul: ${encodeURIComponent(item.Judul || '')}%0D%0A- ID: ${item.ID}%0D%0A%0D%0AMohon informasi detail lisensinya.%0D%0A%0D%0ATerima kasih." class="btn-contact btn-mail">
                        ✉️ Order Email
                    </a>
                </div>"""

# Sisipkan tombol ke dalam render kartu karya JavaScript
target = '${item.deskripsi_kuratorial || ""}</p>'
if target in content and 'contact-actions' not in content:
    content = content.replace(target, btn_markup)
elif '${item.deskripsi_kuratorial || ""}\n                </p>' in content and 'contact-actions' not in content:
    content = content.replace('${item.deskripsi_kuratorial || ""}\n                </p>', btn_markup)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("BERHASIL: index.html telah diperbarui dengan tombol DM & Email tanpa error sintaks!")
