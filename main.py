import os
import requests
import feedparser
from bs4 import BeautifulSoup
from urllib.parse import urljoin

from moviepy.video.io.ImageSequenceClip import ImageSequenceClip
from moviepy.video.VideoClip import ImageClip

# ---------------- CONFIG ----------------
RSS_URL = "https://feeds.bbci.co.uk/news/rss.xml"

# ---------------- GET NEWS ----------------
def get_news():
    feed = feedparser.parse(RSS_URL)
    return [{"title": e.title, "link": e.link} for e in feed.entries[:1]]

# ---------------- GET IMAGES ----------------
def get_images(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")

    imgs = []
    for img in soup.find_all("img"):
        src = img.get("src")
        if src:
            full = urljoin(url, src)
            if full.startswith("http"):
                imgs.append(full)

    return imgs[:5]

# ---------------- DOWNLOAD IMAGES ----------------
def download(images):
    os.makedirs("images", exist_ok=True)
    paths = []

    for i, url in enumerate(images):
        try:
            data = requests.get(url).content
            path = f"images/img_{i}.jpg"
            with open(path, "wb") as f:
                f.write(data)
            paths.append(path)
        except:
            pass

    return paths

# ---------------- CREATE VIDEO ----------------
def create_video(title, image_paths):
    if not image_paths:
        print("No images to create video.")
        return

    print("Creating video...")

    clips = []

    for path in image_paths:
        try:
            clip = ImageClip(path).resize((1280, 720)).set_duration(3)
            clips.append(clip)
        except:
            pass

    if not clips:
        print("No valid clips.")
        return

    # Convert clips to image frames
    frames = [clip.get_frame(0) for clip in clips]

    video = ImageSequenceClip(frames, fps=1)

    os.makedirs("output", exist_ok=True)
    video.write_videofile("output/news_video.mp4", fps=24)

# ---------------- MAIN ----------------
def main():
    news = get_news()

    for n in news:
        print("Processing:", n["title"])

        images = get_images(n["link"])
        paths = download(images)

        create_video(n["title"], paths)

if __name__ == "__main__":
    main()
