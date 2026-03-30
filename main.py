import os
import requests
import feedparser

from moviepy.video.VideoClip import ImageClip
from moviepy.video.fx.resize import resize

# ---------------- CONFIG ----------------
RSS_URL = "https://feeds.bbci.co.uk/news/rss.xml"

# ---------------- GET NEWS ----------------
def get_news():
    feed = feedparser.parse(RSS_URL)
    articles = []

    for entry in feed.entries[:1]:
        image_url = None

        if "media_content" in entry:
            image_url = entry.media_content[0]["url"]
        elif "media_thumbnail" in entry:
            image_url = entry.media_thumbnail[0]["url"]

        articles.append({
            "title": entry.title,
            "image": image_url
        })

    return articles

# ---------------- DOWNLOAD IMAGE ----------------
def download_image(url):
    os.makedirs("images", exist_ok=True)

    try:
        data = requests.get(url, timeout=10).content
        path = "images/news.jpg"

        with open(path, "wb") as f:
            f.write(data)

        if os.path.getsize(path) > 5000:
            return path
    except:
        pass

    return None

# ---------------- CREATE VIDEO ----------------
def create_video(title, image_path):
    if not image_path:
        print("No valid image.")
        return

    print("Creating video...")

    clip = ImageClip(image_path)
    clip = clip.fx(resize, (1280, 720)).set_duration(5)

    os.makedirs("output", exist_ok=True)

    clip.write_videofile("output/news_video.mp4", fps=24)

# ---------------- MAIN ----------------
def main():
    news = get_news()

    for n in news:
        print("Processing:", n["title"])

        img_path = download_image(n["image"])
        create_video(n["title"], img_path)

if __name__ == "__main__":
    main()
