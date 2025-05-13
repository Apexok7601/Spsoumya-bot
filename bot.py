import os
import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

def search_movie_on_filmyfly(movie_name):
    search_url = f"https://filmyfly.stream/?s={movie_name.replace(' ', '+')}"
    response = requests.get(search_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    first_post = soup.select_one("h2.entry-title a")
    if first_post:
        return first_post['href']
    return None

def get_download_links(page_url):
    response = requests.get(page_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    links = []
    for a in soup.find_all('a', href=True):
        text = a.get_text(strip=True).lower()
        if any(x in text for x in ['download', '480p', '720p', '1080p']):
            links.append(f"{a.get_text(strip=True)}: {a['href']}")
    return links

async def movie_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("মুভির নাম লিখুন, যেমনঃ /movie Inception")
        return

    movie_name = ' '.join(context.args)
    await update.message.reply_text(f"🔍 খোঁজা হচ্ছে: {movie_name}")

    movie_url = search_movie_on_filmyfly(movie_name)
    if not movie_url:
        await update.message.reply_text("দুঃখিত, কিছুই পাওয়া যায়নি!")
        return

    download_links = get_download_links(movie_url)
    if not download_links:
        await update.message.reply_text("ডাউনলোড লিংক পাওয়া যায়নি।")
        return

    reply_text = f"🎬 *{movie_name}* এর ডাউনলোড লিংক:\n\n" + "\n".join(download_links)
    await update.message.reply_text(reply_text, parse_mode='Markdown')

def main():
    bot_token = os.environ.get("BOT_TOKEN")  # টোকেন এখন ENV ভ্যারিয়েবল থেকে নিচ্ছে
    app = ApplicationBuilder().token(bot_token).build()
    app.add_handler(CommandHandler("movie", movie_command))
    print("বট চলছে...")
    app.run_polling()

if __name__ == "__main__":
    main()
