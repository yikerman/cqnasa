"""Astronomy Picture of the Day from science.nasa.gov"""

import base64
import json
import re
import tempfile
import urllib.request
from html import unescape
from html.parser import HTMLParser
from pathlib import Path

import yt_dlp

from .common import (
    TIMEOUT,
    at_all,
    image,
    load_config,
    send_group_file,
    send_group_msg,
    text,
    upload_group_file,
)

# The api.nasa.gov APOD API broke when APOD moved to science.nasa.gov
# (https://github.com/nasa/apod-api/issues/184), so read the WordPress REST API
# behind the new site instead. Category 22766 is APOD.
APOD_URL = (
    "https://science.nasa.gov/wp-json/wp/v2/image-article"
    "?categories=22766&per_page=1&_fields=id,date,link,title,featured_image_url,content"
)
LAST_ID_FILE = Path("last_apod_id.txt")
MAX_VIDEO_BYTES = 100 * 1024 * 1024


class ExplanationParser(HTMLParser):
    """Collect the text of the <p class="media-detail-hero__description"> paragraph."""

    def __init__(self):
        super().__init__()
        self.inside = False
        self.parts = []

    def handle_starttag(self, tag, attrs):
        classes = dict(attrs).get("class") or ""
        if tag == "p" and "media-detail-hero__description" in classes:
            self.inside = True

    def handle_endtag(self, tag):
        if tag == "p":
            self.inside = False

    def handle_data(self, data):
        if self.inside:
            self.parts.append(data)


def get_explanation(content):
    parser = ExplanationParser()
    parser.feed(content)
    explanation = re.sub(r"\s+", " ", "".join(parser.parts)).strip()
    return explanation.removeprefix("Explanation:").strip()


def get_title(post):
    # "APOD: 2026 October 28 – The Mutual Occultation of Ganymede and Io"
    title = unescape(post["title"]["rendered"])
    return re.sub(r"^APOD: \d{4} \w+ \d{1,2} [–-] ", "", title)


def get_video(content):
    """Return ("file", url) for NASA-hosted videos, ("embed", url) for YouTube/Vimeo."""
    m = re.search(r'<source[^>]*\bsrc="([^"]+\.mp4)"', content)
    if m:
        return "file", unescape(m.group(1))
    m = re.search(
        r'<iframe[^>]*\bsrc="([^"]*(?:youtube|youtu\.be|vimeo)[^"]*)"', content
    )
    if m:
        return "embed", unescape(m.group(1))
    return None, None


def download_embed(url, directory):
    opts = {
        # Single-file formats only, so merging doesn't need ffmpeg
        "format": "best[ext=mp4]/best",
        "outtmpl": str(Path(directory) / "video.%(ext)s"),
        "max_filesize": MAX_VIDEO_BYTES,
        # YouTube needs a JS runtime; use whichever is installed
        "js_runtimes": {"deno": {}, "node": {}},
        "quiet": True,
        "noprogress": True,
    }
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=True)
        path = Path(ydl.prepare_filename(info))
    if not path.exists():
        raise RuntimeError("yt-dlp skipped " + url + " (larger than max_filesize?)")
    return path


def send_video(group, kind, url, name):
    if kind == "file":
        send_group_file(group, url, name + ".mp4")
        return
    with tempfile.TemporaryDirectory() as tmp:
        path = download_embed(url, tmp)
        data = base64.b64encode(path.read_bytes()).decode("ascii")
        upload_group_file(group, "base64://" + data, name + path.suffix)


def is_new(post_id):
    return not LAST_ID_FILE.exists() or LAST_ID_FILE.read_text() != str(post_id)


def send_apod():
    config = load_config()
    group = config["GROUP"]

    print("Fetching APOD...")
    with urllib.request.urlopen(APOD_URL, timeout=TIMEOUT) as resp:
        post = json.loads(resp.read())[0]
    print("Received " + post["link"])

    if not is_new(post["id"]):
        print("No new APOD")
        return
    date = post["date"][:10]
    content = post["content"]["rendered"]
    print("New APOD! " + date)

    # Upload videos before any text, so a failed upload doesn't leave half a post
    kind, video_url = get_video(content)
    if kind:
        try:
            send_video(group, kind, video_url, "APOD-" + date)
        except Exception as e:
            print("Video upload failed, falling back to still image: " + str(e))
            kind = None

    send_group_msg(group, at_all(), text(" Astronomy Picture of the Day: " + date))
    send_group_msg(group, text(get_title(post)))
    explanation = get_explanation(content)
    if explanation:
        send_group_msg(group, text(explanation))
    if not kind:
        # Full-size originals can be 6000px+; let NASA's image CDN scale it down
        image_url = post["featured_image_url"].split("?")[0] + "?w=2048&h=2048&fit=clip"
        send_group_msg(group, image(image_url))
        if video_url:
            send_group_msg(group, text("Video: " + post["link"]))
    LAST_ID_FILE.write_text(str(post["id"]))
