with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Bersihkan sisa tombol statis yang tadi sempat menempel hanya di ART-001
import re
html = re.sub(r'<div class="contact-actions">[\s\S]*?</div>\s*</div>', '</div>', html)

# 2. Template blok tombol interaktif yang membaca data dinamis tiap karya
markup_tombol = """
                <div class="contact-actions">
                    <a href="https://ig.me/m/maruto.septriono" target="_blank" rel="noopener noreferrer" class="btn-contact btn-ig">
                        💬 DM Instagram
                    </a>
                    <a href="mailto:studiowizhclop@gmail.com?subject=Order / License - ${encodeURIComponent(item.Judul || 'Artwork')} (${item.ID})&body=Halo Maruto Septriono,%0D%0A%0D%0ASaya tertarik dengan lisensi karya seni:%0D%0A- Judul: ${encodeURIComponent(item.Judul || '')}%0D%0A- ID: ${item.ID}%0D%0A%0D%0AMohon informasi ketersediaannya.%0D%0A%0D%0ATerima kasih." class="btn-contact btn-mail">
                        ✉️ Order Email
                    </a>
                </div>"""

# 3. Cari bagian perender JavaScript kartu (renderCard / createCard / forEach)
# Letakkan tombol tepat setelah penutup kontainer harga lisensi pada template literal
target_js_1 = "${isId ? 'Bebas Ongkos Kirim' : 'Free Worldwide Shipping'}</div>\n                </div>"
target_js_2 = "Bebas Ongkos Kirim</div>\n                </div>"
target_js_3 = "Free Worldwide Shipping</div>\n                </div>"

if target_js_1 in html:
    html = html.replace(target_js_1, target_js_1 + markup_tombol)
    print("Berhasil memasang tombol pada template dwibahasa untuk SEMUA kartu!")
elif target_js_2 in html:
    html = html.replace(target_js_2, target_js_2 + markup_tombol)
    print("Berhasil memasang tombol pada template untuk SEMUA kartu!")
elif target_js_3 in html:
    html = html.replace(target_js_3, target_js_3 + markup_tombol)
    print("Berhasil memasang tombol pada template untuk SEMUA kartu!")
else:
    # Pencarian fleksibel untuk penutup blok harga di dalam template string (`)
    pattern = r'(\$\{\s*item\.harga_cetak_usd[\s\S]*?<\/div>\s*<\/div>)'
    if re.search(pattern, html):
        html = re.sub(pattern, r'\1' + markup_tombol, html, count=1)
        print("Berhasil memasang tombol via pola dinamis untuk SEMUA kartu!")
    else:
        print("Pola target perender kartu tidak ditemukan.")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)
