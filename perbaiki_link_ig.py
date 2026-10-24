with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Ganti tautan ig.me/m/ menjadi format profil langsung instagram.com/
html = html.replace('https://ig.me/m/maruto.septriono', 'https://instagram.com/maruto.septriono')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("SUKSES: Tautan Instagram berhasil diubah ke profil langsung agar langsung membuka aplikasi HP!")
