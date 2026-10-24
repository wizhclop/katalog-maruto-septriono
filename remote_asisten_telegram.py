import os
import sys
import json
import base64
import re
import shutil
import subprocess
import tempfile
from io import BytesIO
from PIL import Image, PngImagePlugin
import piexif
import requests

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.request import HTTPXRequest
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

# --- PENGAMAN KUNCI TUNGGAL ---
LOCK_FILE = os.path.join(tempfile.gettempdir(), "maruto_bot_lock.lck")
if os.path.exists(LOCK_FILE):
    try:
        os.remove(LOCK_FILE)
    except Exception:
        pass

with open(LOCK_FILE, "w") as f:
    f.write(str(os.getpid()))

def cleanup_lock():
    if os.path.exists(LOCK_FILE):
        try:
            os.remove(LOCK_FILE)
        except Exception:
            pass

import atexit
atexit.register(cleanup_lock)

# --- KONFIGURASI PRIBADI ---
TELEGRAM_TOKEN = "8525326297:AAGnAmyTVsFyZ4zG4J5Y6DJE3RQOZRPPiVc"
AUTHORIZED_USER_ID = 6300301484

BASE_DIR = r"F:\DATABASE_AI ART\ART"
WATCH_DIR = os.path.join(BASE_DIR, "ART_70")
CATALOG_PATH = os.path.join(BASE_DIR, "art_catalog.json")
PROMO_DIR = os.path.join(BASE_DIR, "promosi_konten")
LM_STUDIO_URL = "http://localhost:1234/v1/chat/completions"
LM_MODELS_URL = "http://localhost:1234/v1/models"

# --- PROFIL RESMI SENIMAN ---
ARTIST_NAME = "Maruto Septriono"
ARTIST_EMAIL = "kirimdoa@gmail.com"
ARTIST_IG = "@maruto.septriono"
ARTIST_PIN = "@marutostudio"
ARTIST_PIN_URL = "https://id.pinterest.com/marutostudio"
ARTIST_BLOG = "https://artofdiary.blogspot.com/"
ARTIST_FB = "https://www.facebook.com/maruto.septriono"
CATALOG_WEB_URL = "http://wizhclop.github.io/katalog-maruto-septriono"

os.makedirs(WATCH_DIR, exist_ok=True)
os.makedirs(PROMO_DIR, exist_ok=True)

PENDING_SUBMISSIONS = {}
AWAITING_UKURAN = {}

def safe_save_catalog(data, target_path):
    temp_path = target_path + ".tmp"
    with open(temp_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    os.replace(temp_path, target_path)

def get_next_art_id(catalog_data):
    max_id = 0
    for item in catalog_data:
        raw_id = item.get("ID") or item.get("id") or ""
        match = re.search(r"(\d+)", raw_id)
        if match:
            num = int(match.group(1))
            if num > max_id:
                max_id = num
    return f"ART-{max_id + 1:03d}"

def resize_image_bytes(image_bytes, max_dim=800):
    with Image.open(BytesIO(image_bytes)) as img:
        img = img.convert("RGB")
        img.thumbnail((max_dim, max_dim), Image.Resampling.LANCZOS)
        buf = BytesIO()
        img.save(buf, format="JPEG", quality=80)
        return buf.getvalue()

def inject_metadata_single(img_path, art_id, title, statement, curatorial, tags):
    ext = os.path.splitext(img_path)[1].lower()
    copyright_notice = f"© 2026 {ARTIST_NAME}. Portfolio: {CATALOG_WEB_URL} | Blog: {ARTIST_BLOG}"
    full_desc = f"{statement}\n\nCatatan Kuratorial:\n{curatorial}\n\nKode Arsip: {art_id}\nKontak: {ARTIST_EMAIL}"[:1500]
    safe_tags = tags[:1000]

    try:
        if ext in [".jpg", ".jpeg"]:
            im = Image.open(img_path)
            im_rgb = im.convert("RGB")
            exif_dict = {"0th": {}, "Exif": {}, "GPS": {}, "1st": {}, "thumbnail": None}
            if "exif" in im.info:
                try:
                    exif_dict = piexif.load(im.info["exif"])
                except Exception:
                    pass

            exif_dict["0th"][piexif.ImageIFD.Artist] = ARTIST_NAME.encode("utf-8", errors="ignore")
            exif_dict["0th"][piexif.ImageIFD.Copyright] = copyright_notice.encode("utf-8", errors="ignore")
            exif_dict["0th"][piexif.ImageIFD.ImageDescription] = full_desc.encode("utf-8", errors="ignore")
            exif_dict["0th"][piexif.ImageIFD.XPTitle] = title.encode("utf-16le", errors="ignore")
            exif_dict["0th"][piexif.ImageIFD.XPAuthor] = ARTIST_NAME.encode("utf-16le", errors="ignore")
            exif_dict["0th"][piexif.ImageIFD.XPKeywords] = safe_tags.encode("utf-16le", errors="ignore")
            exif_dict["0th"][piexif.ImageIFD.XPComment] = statement[:500].encode("utf-16le", errors="ignore")

            exif_bytes = piexif.dump(exif_dict)
            fd, tmp_file = tempfile.mkstemp(suffix=".jpg")
            os.close(fd)
            im_rgb.save(tmp_file, format="JPEG", quality=95, exif=exif_bytes)
            im.close()
            im_rgb.close()
            shutil.move(tmp_file, img_path)

        elif ext == ".png":
            im = Image.open(img_path)
            meta = PngImagePlugin.PngInfo()
            meta.add_text("Title", title)
            meta.add_text("Author", ARTIST_NAME)
            meta.add_text("Copyright", copyright_notice)
            meta.add_text("Description", full_desc)
            meta.add_text("Comment", statement)
            meta.add_text("Keywords", safe_tags)

            fd, tmp_file = tempfile.mkstemp(suffix=".png")
            os.close(fd)
            im.save(tmp_file, format="PNG", pnginfo=meta)
            im.close()
            shutil.move(tmp_file, img_path)
    except Exception as e:
        print(f"Peringatan injeksi EXIF: {e}")

def generate_promo_files(art_id, title, year, media, size, statement, curatorial, tags):
    tags_formatted = " ".join([f"#{t.strip().replace('#','')}" for t in tags.split(",") if t.strip()])
    pin_title = f"{title} - Gothic Surrealism by {ARTIST_NAME}"[:100]
    pin_desc = f'"{statement}" Karya orisinal "{title}" ({year}) oleh {ARTIST_NAME}. Medium: {media}, Dimensi: {size}. Inquiry: {ARTIST_EMAIL} | Web: {CATALOG_WEB_URL}'[:450]

    # 1. Instagram
    ig_text = (
        f"\"{statement}\"\n\n"
        f"{title} ({year})\n"
        f"Karya ini mengalirkan ketegangan visual antara ruang sunyi dan detail organik, "
        f"merefleksikan dialog batin seniman melalui tarikan {media.lower()}.\n\n"
        f"📐 Rincian Teknis & Arsip:\n"
        f"• Kode Arsip: {art_id}\n"
        f"• Medium: {media}\n"
        f"• Dimensi Fisik: {size}\n"
        f"• Status: Koleksi Pribadi / Karya Orisinal\n\n"
        f"💼 Ketersediaan Lisensi & Format Digital:\n"
        f"• High-Res Digital Master: $ 250 USD\n"
        f"• Commercial Print License: $ 100 USD (Bebas Royalti)\n\n"
        f"Inquiry lisensi atau koleksi:\n"
        f"DM Instagram: {ARTIST_IG}\n"
        f"Email: {ARTIST_EMAIL}\n"
        f"Katalog Web: {CATALOG_WEB_URL}\n"
        f"Blog Diary: {ARTIST_BLOG}\n\n"
        f"{tags_formatted}"
    )

    # 2. Pinterest
    pin_text = (
        f"📌 JUDUL PIN:\n{pin_title}\n\n"
        f"📝 DESKRIPSI:\n{pin_desc}\n\n"
        f"🔗 TAUTAN TUJUAN:\n{CATALOG_WEB_URL}\n\n"
        f"👤 AKUN PINTEREST: {ARTIST_PIN} ({ARTIST_PIN_URL})\n"
        f"🏷 REKOMENDASI PAPAN: Gothic Surrealism, Dark Fantasy Ink Art"
    )

    # 3. Blogspot / Facebook Draft
    blog_fb_text = (
        f"📝 DRAF BLOGSPOT & FACEBOOK:\n\n"
        f"Judul Post: {title} ({year}) - Catatan Visual {ARTIST_NAME}\n\n"
        f"{statement}\n\n"
        f"Catatan Kuratorial:\n{curatorial}\n\n"
        f"Detail Karya:\n"
        f"- Arsip: {art_id}\n"
        f"- Media: {media}\n"
        f"- Ukuran: {size}\n\n"
        f"Galeri Portofolio: {CATALOG_WEB_URL}\n"
        f"Profil Seniman: {ARTIST_FB} | IG: {ARTIST_IG}\n"
        f"Kontak: {ARTIST_EMAIL}"
    )

    full_content = f"{ig_text}\n\n{'='*50}\n\n{pin_text}\n\n{'='*50}\n\n{blog_fb_text}"
    with open(os.path.join(PROMO_DIR, f"{art_id}_promosi.txt"), "w", encoding="utf-8") as f:
        f.write(full_content)

    return ig_text, pin_text, blog_fb_text

def get_active_model_name():
    try:
        r = requests.get(LM_MODELS_URL, timeout=5)
        if r.status_code == 200:
            data = r.json().get("data", [])
            for m in data:
                m_id = m.get("id", "")
                if "vl" in m_id.lower() or "vision" in m_id.lower():
                    return m_id
            if data:
                return data[0].get("id")
    except Exception:
        pass
    return "qwen3-vl-2b-instruct"

def analyze_with_local_ai(img_bytes):
    b64_img = base64.b64encode(img_bytes).decode("utf-8")
    model_name = get_active_model_name()

    prompt_text = (
        "Kamu adalah kurator seni rupa ahli surealisme gotik. "
        "Lihat gambar ini dan berikan analisis kuratorial orisinal yang puitis dan mendalam. "
        "DILARANG keras menyalin teks contoh. Tuliskan analisis asli dari gambar. "
        "Kembalikan HANYA format JSON murni tanpa pengantar:\n"
        "{\n"
        '  "Judul": "Tulis judul puitis/mistis spesifik untuk gambar ini",\n'
        '  "Tahun": "2026",\n'
        '  "Media": "Tinta di atas kertas",\n'
        '  "artist_statement_id": "Tulis 1-2 kalimat refleksi filosofis puitis mengenai esensi gambar ini",\n'
        '  "deskripsi_kuratorial": "Tulis 1 paragraf analisis detail mengenai arsitektur imajinatif, ritme arsir tinta, dan suasana gotik dalam karya ini",\n'
        '  "tags": "art, sketch, drawing, indonesia, darkart, contemporaryart, surealisgothic, gothic"\n'
        "}"
    )

    payload = {
        "model": model_name,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt_text},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_img}"}}
                ]
            }
        ],
        "temperature": 0.5,
        "max_tokens": 800
    }

    resp = requests.post(LM_STUDIO_URL, json=payload, timeout=120)
    if resp.status_code != 200:
        raise Exception(f"LM Studio Error ({resp.status_code}): {resp.text}")

    raw_content = resp.json()["choices"][0]["message"]["content"].strip()
    if "```" in raw_content:
        raw_content = re.sub(r"```(?:json)?", "", raw_content).strip()
    return json.loads(raw_content)

def find_repo_folder():
    drives = [r"C:\Users", r"F:\\"]
    for d in drives:
        if os.path.exists(d):
            for root, dirs, files in os.walk(d):
                if ".git" in dirs:
                    git_cfg = os.path.join(root, ".git", "config")
                    if os.path.exists(git_cfg):
                        try:
                            with open(git_cfg, "r", encoding="utf-8", errors="ignore") as f:
                                if "katalog-maruto-septriono" in f.read():
                                    return root
                        except Exception:
                            pass
    return None

def trigger_build_and_push(art_id, title):
    gen_script = os.path.join(BASE_DIR, "generate_web_gallery.py")
    if os.path.exists(gen_script):
        subprocess.run(["python", gen_script], cwd=BASE_DIR, check=True)

    repo_dir = find_repo_folder()
    if not repo_dir:
        return False, "Folder repositori lokal tidak ditemukan."

    web_dir = os.path.join(BASE_DIR, "web_galeri")
    repo_img_dir = os.path.join(repo_dir, "images")
    os.makedirs(repo_img_dir, exist_ok=True)

    shutil.copy2(os.path.join(web_dir, "index.html"), os.path.join(repo_dir, "index.html"))
    web_imgs = os.path.join(web_dir, "images")
    if os.path.exists(web_imgs):
        for img_name in os.listdir(web_imgs):
            src_f = os.path.join(web_imgs, img_name)
            dst_f = os.path.join(repo_img_dir, img_name)
            if not os.path.exists(dst_f):
                shutil.copy2(src_f, dst_f)

    subprocess.run(["git", "add", "."], cwd=repo_dir, check=True)
    subprocess.run(["git", "commit", "-m", f"Auto-publish {art_id}: {title} via Multi-Platform Hub"], cwd=repo_dir, check=True)
    subprocess.run(["git", "push", "origin", "main"], cwd=repo_dir, check=True)

    return True, "Berhasil di-push ke GitHub Pages."

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != AUTHORIZED_USER_ID:
        return
    await update.message.reply_text(
        "👋 Halo Mas Maruto! Asisten AI Galeri Multi-Platform Siap.\n"
        "📸 Kirimkan foto lukisan/karya seni baru dari HP untuk dianalisis dan diterbitkan."
    )

async def handle_incoming_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != AUTHORIZED_USER_ID:
        return

    if update.message.photo:
        tg_file = await update.message.photo[-1].get_file()
    elif update.message.document and update.message.document.mime_type.startswith("image/"):
        tg_file = await update.message.document.get_file()
    else:
        return

    status_msg = await update.message.reply_text("📥 Foto diterima di PC! Sedang dianalisis AI Lokal (LM Studio)...")

    try:
        raw_bytes = await tg_file.download_as_bytearray()
        optimized_bytes = resize_image_bytes(raw_bytes)
        ai_data = analyze_with_local_ai(optimized_bytes)

        tag_list = ["art", "sketch", "drawing", "indonesia", "darkart", "contemporaryart", "surealisgothic", "gothic"]
        ai_raw_tags = ai_data.get("tags", "")
        for t in ai_raw_tags.split(","):
            cleaned_tag = t.strip().replace("#", "")
            if cleaned_tag and cleaned_tag not in tag_list:
                tag_list.append(cleaned_tag)
        ai_data["tags"] = ", ".join(tag_list)

        if os.path.exists(CATALOG_PATH):
            with open(CATALOG_PATH, "r", encoding="utf-8-sig") as f:
                catalog = json.load(f)
        else:
            catalog = []

        next_id = get_next_art_id(catalog)
        submission_key = f"sub_{next_id}"

        PENDING_SUBMISSIONS[submission_key] = {
            "id": next_id,
            "ai_data": ai_data,
            "image_bytes": optimized_bytes,
            "ukuran": "-"
        }

        AWAITING_UKURAN[user_id] = submission_key
        tag_display = " ".join([f"#{t}" for t in tag_list])

        card_text = (
            f"🎨 <b>DRAF KARYA BARU: {next_id}</b>\n\n"
            f"📌 <b>Judul:</b> {ai_data.get('Judul', 'Tanpa Judul')}\n"
            f"🖌 <b>Media:</b> {ai_data.get('Media', '-')}\n"
            f"📅 <b>Tahun:</b> {ai_data.get('Tahun', '2026')}\n\n"
            f"💬 <b>Artist Statement:</b>\n<i>\"{ai_data.get('artist_statement_id', '-')}\"</i>\n\n"
            f"📖 <b>Catatan Kuratorial:</b>\n{ai_data.get('deskripsi_kuratorial', '-')}\n\n"
            f"🏷 <b>Tags:</b> {tag_display}\n\n"
            f"👉 <b>Berapa ukuran karya fisik ini?</b>\n"
            f"Ketik ukurannya di chat sekarang (misal: <code>29.7 cm x 42 cm</code>):"
        )

        await status_msg.delete()
        await update.message.reply_text(card_text, parse_mode="HTML")

    except Exception as err:
        await status_msg.edit_text(f"⚠️ Terjadi kendala analisis AI di PC:\n{err}")

async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != AUTHORIZED_USER_ID:
        return

    if user_id in AWAITING_UKURAN:
        submission_key = AWAITING_UKURAN.pop(user_id)
        ukuran_input = update.message.text.strip()

        if submission_key in PENDING_SUBMISSIONS:
            PENDING_SUBMISSIONS[submission_key]["ukuran"] = ukuran_input
            art_id = PENDING_SUBMISSIONS[submission_key]["id"]

            keyboard = [
                [
                    InlineKeyboardButton("🚀 TERBITKAN KE SEMUA PLATFORM", callback_data=f"approve_{submission_key}"),
                    InlineKeyboardButton("❌ Batalkan", callback_data=f"reject_{submission_key}")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await update.message.reply_text(
                f"📐 <b>Ukuran tercatat:</b> <code>{ukuran_input}</code> untuk {art_id}.\n\n"
                f"Tekan tombol di bawah untuk <b>menyimpan, injeksi metadata EXIF, update web katalog, dan membuat draf medsos siap salin</b>:",
                reply_markup=reply_markup,
                parse_mode="HTML"
            )
    else:
        await update.message.reply_text("Kirimkan foto karya baru untuk memulai analisis AI.")

async def handle_button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.from_user.id != AUTHORIZED_USER_ID:
        return

    data = query.data
    if data.startswith("approve_"):
        sub_key = data.replace("approve_", "")
        item = PENDING_SUBMISSIONS.get(sub_key)
        if not item:
            await query.edit_message_text("Data submission tidak ditemukan.")
            return

        art_id = item["id"]
        ai_data = item["ai_data"]
        img_bytes = item["image_bytes"]
        ukuran_final = item["ukuran"]

        await query.edit_message_text(f"⏳ Sedang memproses {art_id} ke seluruh platform...")

        safe_title = re.sub(r'[^a-zA-Z0-9_\- ]', '', ai_data.get("Judul", "Karya")).strip()
        filename = f"{art_id} - {safe_title}.jpg"
        save_file_path = os.path.join(WATCH_DIR, filename)

        with open(save_file_path, "wb") as f:
            f.write(img_bytes)

        inject_metadata_single(
            save_file_path,
            art_id,
            ai_data.get("Judul", "Tanpa Judul"),
            ai_data.get("artist_statement_id", ""),
            ai_data.get("deskripsi_kuratorial", ""),
            ai_data.get("tags", "")
        )

        if os.path.exists(CATALOG_PATH):
            with open(CATALOG_PATH, "r", encoding="utf-8-sig") as f:
                catalog = json.load(f)
        else:
            catalog = []

        new_entry = {
            "ID": art_id,
            "Judul": ai_data.get("Judul", "Tanpa Judul"),
            "Tahun": ai_data.get("Tahun", "2026"),
            "Ukuran": ukuran_final,
            "Media": ai_data.get("Media", "-"),
            "Nama_File": filename,
            "artist_statement_id": ai_data.get("artist_statement_id", ""),
            "deskripsi_kuratorial": ai_data.get("deskripsi_kuratorial", ""),
            "tags": ai_data.get("tags", "")
        }

        catalog.append(new_entry)
        safe_save_catalog(catalog, CATALOG_PATH)
        del PENDING_SUBMISSIONS[sub_key]

        try:
            ok, msg = trigger_build_and_push(art_id, new_entry['Judul'])
            web_status = "🌐 <b>Katalog Web:</b> LIVE di GitHub Pages" if ok else f"⚠️ Web: {msg}"
        except Exception as e:
            web_status = f"⚠️ Web Sync: {e}"

        ig_caption, pin_info, blog_info = generate_promo_files(
            art_id,
            new_entry['Judul'],
            new_entry['Tahun'],
            new_entry['Media'],
            new_entry['Ukuran'],
            new_entry['artist_statement_id'],
            new_entry['deskripsi_kuratorial'],
            new_entry['tags']
        )

        # Balasan 1: Status Publikasi Web & Metadata
        await query.message.reply_text(
            f"✅ <b>KARYA {art_id} SUKSES DIPUBLIKASIKAN!</b>\n\n"
            f"• <b>Judul:</b> {new_entry['Judul']}\n"
            f"• <b>Ukuran:</b> {new_entry['Ukuran']}\n"
            f"• <b>Metadata EXIF:</b> Tersuntik aman hak cipta Maruto Septriono\n"
            f"• {web_status}\n\n"
            f"👇 <i>Draf konten siap salin di bawah ini:</i>",
            parse_mode="HTML"
        )

        # Balasan 2: Takarir Instagram
        await query.message.reply_text(
            f"📸 <b>TAKARIR INSTAGRAM (SIAP SALIN):</b>\n\n{ig_caption}",
            parse_mode="HTML"
        )

        # Balasan 3: Materi Pinterest
        await query.message.reply_text(
            f"📌 <b>MATERI PIN PINTEREST:</b>\n\n{pin_info}",
            parse_mode="HTML"
        )

        # Balasan 4: Materi Blogspot & Facebook
        await query.message.reply_text(
            f"🌐 <b>MATERI BLOGSPOT & FACEBOOK:</b>\n\n{blog_info}",
            parse_mode="HTML"
        )

    elif data.startswith("reject_"):
        sub_key = data.replace("reject_", "")
        if sub_key in PENDING_SUBMISSIONS:
            del PENDING_SUBMISSIONS[sub_key]
        if query.from_user.id in AWAITING_UKURAN:
            del AWAITING_UKURAN[query.from_user.id]
        await query.edit_message_text("❌ Proses dibatalkan. Berkas tidak dimasukkan ke database.")

def main():
    print("==================================================")
    print("  ASISTEN TELEGRAM MULTI-PLATFORM HUB AKTIF       ")
    print(f"  Direktori Basis : {BASE_DIR}")
    print("  Status: Standby menerima foto dari HP...")
    print("  Tekan Ctrl+C untuk berhenti.")
    print("==================================================")

    req = HTTPXRequest(
        connect_timeout=30.0,
        read_timeout=60.0,
        write_timeout=30.0,
        pool_timeout=30.0
    )

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).request(req).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(MessageHandler(filters.PHOTO | filters.Document.IMAGE, handle_incoming_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))
    app.add_handler(CallbackQueryHandler(handle_button_callback))

    app.run_polling(bootstrap_retries=5, timeout=30)

if __name__ == "__main__":
    main()
