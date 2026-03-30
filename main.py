import requests
import feedparser
from bs4 import BeautifulSoup
from moviepy.editor import *
from urllib.parse import urljoin
import os

RSS_URL = "https://feeds.bbci.co.uk/news/rss.xml"

def get_news():
    feed = feedparser.parse(RSS_URL)
    return [{"title": e.title, "link": e.link} for e in feed.entries[:1]]

def get_images(url):
    res = requests.get(url)
    soup = BeautifulSoup(res.text, "html.parser")

    imgs = []
    for img in soup.find_all("img"):
        src = img.get("src")
        if src and src.startswith("http"):
            imgs.append(src)

    return imgs[:3]

def download(imgs):
    paths = []
    os.makedirs("images", exist_ok=True)

    for i, url in enumerate(imgs):
        try:
            data = requests.get(url).content
            path = f"images/{i}.jpg"
            with open(path, "wb") as f:
                f.write(data)
            paths.append(path)
        except:
            pass

    return paths

def create_video(title, images):
    clips = []

    for img in images:
        clip = ImageClip(img).set_duration(3)
        txt = TextClip(title, fontsize=40, color="white").set_duration(3)
        clips.append(CompositeVideoClip([clip, txt.set_position("bottom")]))

    video = concatenate_videoclips(clips)
    video.write_videofile("output.mp4", fps=24)

def main():
    news = get_news()

    for n in news:
        imgs = get_images(n["link"])
        paths = download(imgs)

        if paths:
            create_video(n["title"], paths)

if __name__ == "__main__":
    main()
