import subprocess
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from shazamio import Shazam

TOKEN = "8678235560:AAGZC8TVzmc5sT94IHJKj1TtD6Nf4AHCr1I"

shazam = Shazam()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Отправь музыку или видео 🎧")


async def recognize_music(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message

    await message.reply_text("Слушаю музыку... 🎧")

    file = None
    input_path = "input_file"
    output_path = "audio.wav"

    # определяем тип файла
    if message.audio:
        file = await message.audio.get_file()
    elif message.voice:
        file = await message.voice.get_file()
    elif message.video:
        file = await message.video.get_file()
    else:
        await message.reply_text("Отправь аудио, голосовое или видео.")
        return

    # скачиваем файл
    await file.download_to_drive(input_path)

    try:
        # конвертация в WAV (важно для Shazam)
        subprocess.run([
            "ffmpeg",
            "-y",
            "-i", input_path,
            "-ar", "44100",
            "-ac", "2",
            output_path
        ], check=True)

        # распознавание
        result = await shazam.recognize(output_path)
        track = result.get("track")

        if not track:
            await message.reply_text("Трек не найден 😢")
            return

        title = track.get("title", "Неизвестно")
        artist = track.get("subtitle", "Неизвестно")

        await message.reply_text(f"🎵 {title}\n👤 {artist}")

    except Exception as e:
        await message.reply_text(f"Ошибка:\n{e}")


app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.AUDIO | filters.VOICE | filters.VIDEO, recognize_music))

print("Бот запущен...")

app.run_polling()