import os
import requests
import feedparser

from moviepy.video.VideoClip import ImageClip
from moviepy.video.fx.resize import resize
from moviepy.editor import concatenate_videoclips
from PIL import Image, ImageDraw, ImageFont

RSS_URL = "https://feeds.bbci.co.uk/news/rss.xml"

# ---------------- GET NEWS ----------------
def get_news():
    feed = feedparser.parse(RSS_URL)
    articles = []

    for entry in feed.entries[:3]:  # multiple news
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
def download_image(url, index):
    os.makedirs("images", exist_ok=True)

    try:
        data = requests.get(url, timeout=10).content
        path = f"images/news_{index}.jpg"

        with open(path, "wb") as f:
            f.write(data)

        if os.path.getsize(path) > 5000:
            return path
    except:
        pass

    return None

# ---------------- ADD TEXT ON IMAGE ----------------
def add_text(image_path, text, index):
    img = Image.open(image_path).convert("RGB")
    draw = ImageDraw.Draw(img)

    width, height = img.size

    # simple font
    font = ImageFont.load_default()

    # draw black box
    draw.rectangle([(0, height-120), (width, height)], fill=(0, 0, 0))

    # add text
    draw.text((20, height-100), text[:80], fill=(255, 255, 255), font=font)

    new_path = f"images/text_{index}.jpg"
    img.save(new_path)

    return new_path

# ---------------- CREATE VIDEO ----------------
def create_video(news_list):
    clips = []

    for i, news in enumerate(news_list):
        img_path = download_image(news["image"], i)

        if not img_path:
            continue

        img_with_text = add_text(img_path, news["title"], i)

        clip = ImageClip(img_with_text)
        clip = clip.fx(resize, (1280, 720)).set_duration(4)

        clips.append(clip)

    if not clips:
        print("No clips created")
        return

    final_video = concatenate_videoclips(clips)

    os.makedirs("output", exist_ok=True)
    final_video.write_videofile("output/news_video.mp4", fps=24)

# ---------------- MAIN ----------------
def main():
    news = get_news()
    create_video(news)

if __name__ == "__main__":
    main()
