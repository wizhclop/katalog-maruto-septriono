import os
import json
import base64
import re
import shutil
import subprocess
from io import BytesIO
from PIL import Image
import requests

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

# --- KONFIGURASI PRIBADI ---
TELEGRAM_TOKEN = "8525326297:AAF1jAnSrJbfZ0SVOg0nCVNrIbi3L5c5E4U"
AUTHORIZED_USER_ID = 6300301484

BASE_DIR = r"F:\DATABASE_AI ART\ART"
WATCH_DIR = os.path.join(BASE_DIR, "ART_70")
CATALOG_PATH = os.path.join(BASE_DIR, "art_catalog.json")
LM_STUDIO_URL = "http://localhost:1234/v1/chat/completions"

os.makedirs(WATCH_DIR, exist_ok=True)

# Status antrean & input ukuran manual
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

def resize_image_bytes(image_bytes, max_dim=1024):
    with Image.open(BytesIO(image_bytes)) as img:
        img = img.convert("RGB")
        img.thumbnail((max_dim, max_dim), Image.Resampling.LANCZOS)
        buf = BytesIO()
        img.save(buf, format="JPEG", quality=85)
        return buf.getvalue()

def analyze_with_local_ai(img_bytes):
    b64_img = base64.b64encode(img_bytes).decode("utf-8")
    prompt_text = (
        "Analisis karya seni ini secara mendalam sebagai kurator dan arsiparis profesional. "
        "Kembalikan jawaban HANYA dalam format JSON valid tanpa teks pengantar atau markdown lainnya. "
        "Struktur JSON yang wajib:\n"
        "{\n"
        '  "Judul": "Judul puitis/filosofis yang sesuai",\n'
        '  "Tahun": "2026",\n'
        '  "Media": "Tinta di atas kertas / Akrilik di kanvas / Conte / AI Generated",\n'
        '  "artist_statement_id": "1-2 kalimat refleksi personal dan esensi filosofis karya.",\n'
        '  "deskripsi_kuratorial": "Catatan kuratorial mengenai teknik arsir, komposisi visual, dan makna karya.",\n'
        '  "tags": "art, sketch, drawing, indonesia, darkart, contemporaryart"\n'
        "}"
    )

    payload = {
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt_text},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_img}"}}
                ]
            }
        ],
        "temperature": 0.4,
        "max_tokens": 800
    }

    resp = requests.post(LM_STUDIO_URL, json=payload, timeout=120)
    resp.raise_for_status()
    raw_content = resp.json()["choices"][0]["message"]["content"].strip()
    if "```" in raw_content:
        raw_content = re.sub(r"```(?:json)?", "", raw_content).strip()
    return json.loads(raw_content)

def find_repo_folder():
    """Mencari folder lokal git repositori katalog-maruto-septriono"""
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
    """Membangun ulang galeri web dan melakukan push otomatis ke GitHub Pages"""
    # 1. Jalankan generator galeri
    gen_script = os.path.join(BASE_DIR, "generate_web_gallery.py")
    if os.path.exists(gen_script):
        subprocess.run(["python", gen_script], cwd=BASE_DIR, check=True)

    # 2. Cari folder repositori
    repo_dir = find_repo_folder()
    if not repo_dir:
        return False, "Folder repositori lokal 'katalog-maruto-septriono' tidak ditemukan."

    web_dir = os.path.join(BASE_DIR, "web_galeri")
    repo_img_dir = os.path.join(repo_dir, "images")
    os.makedirs(repo_img_dir, exist_ok=True)

    # 3. Salin index.html dan gambar
    shutil.copy2(os.path.join(web_dir, "index.html"), os.path.join(repo_dir, "index.html"))
    web_imgs = os.path.join(web_dir, "images")
    if os.path.exists(web_imgs):
        for img_name in os.listdir(web_imgs):
            src_f = os.path.join(web_imgs, img_name)
            dst_f = os.path.join(repo_img_dir, img_name)
            if not os.path.exists(dst_f):
                shutil.copy2(src_f, dst_f)

    # 4. Git Add, Commit, Push
    subprocess.run(["git", "add", "."], cwd=repo_dir, check=True)
    commit_msg = f"Auto-publish {art_id}: {title} via Telegram Assistant"
    subprocess.run(["git", "commit", "-m", commit_msg], cwd=repo_dir, check=True)
    subprocess.run(["git", "push", "origin", "main"], cwd=repo_dir, check=True)

    return True, "Berhasil di-push ke GitHub Pages."

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != AUTHORIZED_USER_ID:
        return
    await update.message.reply_text(
        "👋 Halo Mas Maruto! Asisten AI Galeri Aktif.\n"
        "📸 Kirimkan foto karya seni baru untuk diproses dan dipublikasikan otomatis."
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
        await status_msg.edit_text(f"⚠️ Terjadi kendala saat analisis AI di PC: {err}")

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
                    InlineKeyboardButton("🚀 Setuju & Langsung Publish ke Web", callback_data=f"approve_{submission_key}"),
                    InlineKeyboardButton("❌ Batalkan", callback_data=f"reject_{submission_key}")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await update.message.reply_text(
                f"📐 <b>Ukuran tercatat:</b> <code>{ukuran_input}</code> untuk {art_id}.\n\n"
                f"Tekan tombol di bawah untuk menyimpan ke database dan <b>langsung menayangkan ke GitHub Pages</b>:",
                reply_markup=reply_markup,
                parse_mode="HTML"
            )
    else:
        await update.message.reply_text("Kirimkan foto karya baru untuk dianalisis oleh AI.")

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

        await query.edit_message_text(f"⏳ Sedang menyimpan data {art_id} dan mengunggah ke GitHub Pages...")

        # 1. Simpan gambar ke folder ART_70
        safe_title = re.sub(r'[^a-zA-Z0-9_\- ]', '', ai_data.get("Judul", "Karya")).strip()
        filename = f"{art_id} - {safe_title}.jpg"
        save_file_path = os.path.join(WATCH_DIR, filename)

        with open(save_file_path, "wb") as f:
            f.write(img_bytes)

        # 2. Catat ke art_catalog.json
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

        # 3. Auto-Build Web & Push ke GitHub Pages
        try:
            ok, msg = trigger_build_and_push(art_id, new_entry['Judul'])
            publish_status = "🌐 <b>Karya LIVE di Web Galeri:</b>\nhttp://wizhclop.github.io/katalog-maruto-septriono" if ok else f"⚠️ Gagal upload web: {msg}"
        except Exception as e:
            publish_status = f"⚠️ Gagal sync otomatis: {e}"

        await query.message.reply_text(
            f"✅ <b>KARYA BERHASIL DIARSIPKAN & DITERBITKAN!</b>\n\n"
            f"• <b>ID:</b> {art_id}\n"
            f"• <b>Judul:</b> {new_entry['Judul']}\n"
            f"• <b>Ukuran:</b> {new_entry['Ukuran']}\n"
            f"• <b>Media:</b> {new_entry['Media']}\n"
            f"• <b>Tags:</b> #{new_entry['tags'].replace(', ', ' #')}\n\n"
            f"{publish_status}",
            parse_mode="HTML"
        )

    elif data.startswith("reject_"):
        sub_key = data.replace("reject_", "")
        if sub_key in PENDING_SUBMISSIONS:
            del PENDING_SUBMISSIONS[sub_key]
        if query.from_user.id in AWAITING_UKURAN:
            del AWAITING_UKURAN[query.from_user.id]
        await query.edit_message_text("❌ Proses dibatalkan. Data tidak dimasukkan ke database.")

def main():
    print("==================================================")
    print("  ASISTEN REMOTE TELEGRAM + AUTO-PUSH WEB AKTIF   ")
    print(f"  Direktori Basis : {BASE_DIR}")
    print(f"  Folder Pantau   : {WATCH_DIR}")
    print("  Mode Auto-Deploy ke GitHub Pages: AKTIF")
    print("  Menunggu kiriman karya baru dari HP...")
    print("  Tekan Ctrl+C untuk berhenti.")
    print("==================================================")

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(MessageHandler(filters.PHOTO | filters.Document.IMAGE, handle_incoming_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))
    app.add_handler(CallbackQueryHandler(handle_button_callback))

    app.run_polling()

if __name__ == "__main__":
    main()
