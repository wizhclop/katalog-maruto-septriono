import os
import json
import base64
import re
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

WATCH_DIR = r"F:\DATABASE_AI ART\ART\ART_70"
CATALOG_PATH = r"F:\DATABASE_AI ART\ART\art_catalog.json"
LM_STUDIO_URL = "http://localhost:1234/v1/chat/completions"

os.makedirs(WATCH_DIR, exist_ok=True)

# Status antrean & proses input ukuran manual dari HP
PENDING_SUBMISSIONS = {}
AWAITING_UKURAN = {}

def safe_save_catalog(data, target_path):
    """Menyimpan database secara atomic agar kebal korup."""
    temp_path = target_path + ".tmp"
    with open(temp_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    os.replace(temp_path, target_path)

def get_next_art_id(catalog_data):
    """Menghitung ID berurutan otomatis (ART-xxx)."""
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
    """Mengecilkan gambar ke 1024px agar aman untuk VRAM GPU."""
    with Image.open(BytesIO(image_bytes)) as img:
        img = img.convert("RGB")
        img.thumbnail((max_dim, max_dim), Image.Resampling.LANCZOS)
        buf = BytesIO()
        img.save(buf, format="JPEG", quality=85)
        return buf.getvalue()

def analyze_with_local_ai(img_bytes):
    """Memanggil AI Vision lokal di LM Studio."""
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

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != AUTHORIZED_USER_ID:
        return
    await update.message.reply_text(
        "Halo Mas Maruto! Asisten AI Galeri aktif.\n"
        "Kirim foto karya seni baru ke sini untuk dianalisis."
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

    status_msg = await update.message.reply_text("📥 Foto diterima di PC! Sedang dianalisis AI Lokal...")

    try:
        raw_bytes = await tg_file.download_as_bytearray()
        optimized_bytes = resize_image_bytes(raw_bytes)
        ai_data = analyze_with_local_ai(optimized_bytes)

        # Sisipkan tag tambahan wajib
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
            "ukuran": "-" # Default sebelum diisi dari HP
        }

        # Menandai bahwa bot sedang menunggu input ukuran karya dari user
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
            f"👉 <b>Berapa ukuran karya ini?</b>\n"
            f"Ketik ukurannya di chat sekarang (misal: <code>29.7 cm x 42 cm</code> atau <code>38 x 42 cm</code>):"
        )

        await status_msg.delete()
        await update.message.reply_text(card_text, parse_mode="HTML")

    except Exception as err:
        await status_msg.edit_text(f"⚠️ Terjadi kendala saat analisis AI di PC: {err}")

async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != AUTHORIZED_USER_ID:
        return

    # Periksa apakah sedang menunggu input ukuran karya
    if user_id in AWAITING_UKURAN:
        submission_key = AWAITING_UKURAN.pop(user_id)
        ukuran_input = update.message.text.strip()

        if submission_key in PENDING_SUBMISSIONS:
            PENDING_SUBMISSIONS[submission_key]["ukuran"] = ukuran_input
            art_id = PENDING_SUBMISSIONS[submission_key]["id"]

            keyboard = [
                [
                    InlineKeyboardButton("✅ Setuju & Simpan ke Katalog", callback_data=f"approve_{submission_key}"),
                    InlineKeyboardButton("❌ Batalkan", callback_data=f"reject_{submission_key}")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await update.message.reply_text(
                f"📐 <b>Ukuran tercatat:</b> <code>{ukuran_input}</code> untuk {art_id}.\n\n"
                f"Tekan tombol di bawah untuk menyimpannya ke database:",
                reply_markup=reply_markup,
                parse_mode="HTML"
            )
    else:
        await update.message.reply_text("Kirimkan foto karya seni baru untuk memulai analisis.")

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
            await query.edit_message_text("Data pengajuan tidak ditemukan.")
            return

        art_id = item["id"]
        ai_data = item["ai_data"]
        img_bytes = item["image_bytes"]
        ukuran_final = item["ukuran"]

        safe_title = re.sub(r'[^a-zA-Z0-9_\- ]', '', ai_data.get("Judul", "Karya")).strip()
        filename = f"{art_id} - {safe_title}.jpg"
        save_file_path = os.path.join(WATCH_DIR, filename)

        with open(save_file_path, "wb") as f:
            f.write(img_bytes)

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

        await query.edit_message_text(
            f"✅ <b>BERHASIL DISIMPAN!</b>\n\n"
            f"• <b>ID:</b> {art_id}\n"
            f"• <b>Judul:</b> {new_entry['Judul']}\n"
            f"• <b>Ukuran:</b> {new_entry['Ukuran']}\n"
            f"• <b>Media:</b> {new_entry['Media']}\n"
            f"• <b>Tags:</b> #{new_entry['tags'].replace(', ', ' #')}\n"
            f"• <b>Status:</b> Tersimpan permanen di <code>art_catalog.json</code>",
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
    print("  ASISTEN REMOTE TELEGRAM GALERI MARUTO AKTIF")
    print(f"  Memantau folder : {WATCH_DIR}")
    print(f"  Target database : {CATALOG_PATH}")
    print("  Mode Ukuran Manual & Tag Gothic Siap.")
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
