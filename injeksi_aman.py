with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Tambahkan styling tombol
css_addon = """
    <style>
        .contact-actions {
            display: flex;
            gap: 8px;
            margin: 12px 0 10px 0;
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
    </style>
</head>"""

if '.contact-actions' not in html:
    html = html.replace('</head>', css_addon)

# 2. Skrip otomatis yang menyisipkan tombol ke seluruh kartu karya di halaman
js_addon = """
<script>
document.addEventListener("DOMContentLoaded", function () {
    const cards = document.querySelectorAll(".card");
    cards.forEach(card => {
        if (card.querySelector(".contact-actions")) return;
        
        const titleEl = card.querySelector("h3, .card-title, [data-title]");
        const title = titleEl ? (titleEl.innerText || titleEl.getAttribute("data-title") || "Artwork").trim() : "Artwork";
        
        const badgeEl = card.querySelector(".badge-row, .badge, [class*='id']");
        const artId = badgeEl ? badgeEl.innerText.split("\\n")[0].trim() : "";
        const labelKarya = artId ? `${title} (${artId})` : title;
        
        const container = document.createElement("div");
        container.className = "contact-actions";
        container.innerHTML = `
            <a href="https://ig.me/m/maruto.septriono" target="_blank" rel="noopener noreferrer" class="btn-contact btn-ig">
                💬 DM Instagram
            </a>
            <a href="mailto:studiowizhclop@gmail.com?subject=Order / License - ${encodeURIComponent(labelKarya)}&body=Halo Maruto Septriono,%0D%0A%0D%0ASaya tertarik dengan lisensi karya: ${encodeURIComponent(labelKarya)}.%0D%0AMohon informasi ketersediaannya.%0D%0A%0D%0ATerima kasih." class="btn-contact btn-mail">
                ✉️ Order Email
            </a>
        `;
        
        const targetPoint = card.querySelector(".statement, p.trans-block, details");
        if (targetPoint) {
            targetPoint.parentNode.insertBefore(container, targetPoint);
        } else {
            card.querySelector(".card-content")?.appendChild(container);
        }
    });
});
</script>
</body>"""

if 'maruto.septriono' not in html:
    html = html.replace('</body>', js_addon)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("SUKSES: Tombol kontak otomatis diterapkan ke seluruh kartu tanpa merusak struktur!")
