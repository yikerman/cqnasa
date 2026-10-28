"""Image of the day from NASA APOD API"""

import json
import urllib.request
from pathlib import Path

from .common import at_all, image, load_config, send_group_msg, text

LAST_DATE_FILE = Path("last_image_date.txt")


def is_new(date):
    return not LAST_DATE_FILE.exists() or LAST_DATE_FILE.read_text() != date


def send_apod():
    config = load_config()

    print("Fetching image of the day...")
    content = urllib.request.urlopen(
        "https://api.nasa.gov/planetary/apod?api_key=" + config["API_KEY"]
    ).read()
    content_json = json.loads(content)
    print("Received ", content_json)

    date = content_json["date"]
    if not is_new(date):
        print("No new image of the day")
        return
    if content_json["media_type"] != "image":
        print("APOD " + date + " is a " + content_json["media_type"] + ", skipping")
        LAST_DATE_FILE.write_text(date)
        return
    print("New image of the day! " + date)

    group = config["GROUP"]
    send_group_msg(group, at_all(), text(" Astronomy Picture of the Day: " + date))
    send_group_msg(group, text(content_json["title"]))
    send_group_msg(group, text(content_json["explanation"]))
    send_group_msg(group, image(content_json["url"]))
    LAST_DATE_FILE.write_text(date)
