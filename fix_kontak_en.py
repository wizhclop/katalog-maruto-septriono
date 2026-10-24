with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

import re

# Cari fungsi atau blok pembentuk elemen tombol kontak di skrip index.html
old_block_pattern = r'container\.innerHTML\s*=\s*`[\s\S]*?`;'

new_block = """container.innerHTML = `
            <a href="intent://instagram.com/_u/maruto.septriono/#Intent;package=com.instagram.android;scheme=https;end" 
               onclick="window.location.href='https://instagram.com/maruto.septriono'; return false;"
               target="_blank" rel="noopener noreferrer" class="btn-contact btn-ig">
                💬 DM Instagram
            </a>
            <a href="mailto:studiowizhclop@gmail.com?subject=Inquiry / License Order - ${encodeURIComponent(labelKarya)}&body=Dear Maruto Septriono,%0D%0A%0D%0AI am interested in acquiring a commercial license / print for your artwork:%0D%0A- Title: ${encodeURIComponent(labelKarya)}%0D%0A%0D%0ACould you please provide details regarding licensing terms and availability?%0D%0A%0D%0ABest regards." class="btn-contact btn-mail">
                ✉️ Order Email
            </a>
        `;"""

if re.search(old_block_pattern, html):
    html = re.sub(old_block_pattern, new_block, html)
    print("Berhasil memperbarui tautan Instagram & draf email ke bahasa Inggris!")
else:
    # Penggantian fallback jika polanya sedikit berbeda
    html = html.replace('Halo Maruto Septriono,%0D%0A%0D%0ASaya tertarik dengan lisensi karya: ${encodeURIComponent(labelKarya)}.%0D%0AMohon informasi ketersediaannya.%0D%0A%0D%0ATerima kasih.',
                        'Dear Maruto Septriono,%0D%0A%0D%0AI am interested in acquiring a commercial license for: ${encodeURIComponent(labelKarya)}.%0D%0APlease provide information regarding terms and availability.%0D%0A%0D%0ABest regards.')
    html = html.replace('subject=Order / License -', 'subject=Inquiry / License Order -')
    html = html.replace('https://instagram.com/maruto.septriono', 'https://ig.me/m/maruto.septriono')
    print("Fallback diterapkan.")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)
