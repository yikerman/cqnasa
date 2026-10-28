import json
import urllib.request


class OneBotError(Exception):
    pass


def load_config():
    with open("config.json") as f:
        return json.load(f)


def onebot_call(action, params):
    """Call a OneBot 11 action over NapCat's HTTP server and return its data."""
    config = load_config()
    url = "http://" + config["ONEBOT_API"] + "/" + action
    headers = {"Content-Type": "application/json"}
    if config.get("ACCESS_TOKEN"):
        headers["Authorization"] = "Bearer " + config["ACCESS_TOKEN"]
    body = json.dumps(params).encode("utf-8")
    print("Calling OneBot " + action + ": " + body.decode("utf-8"))
    req = urllib.request.Request(url, data=body, headers=headers, method="POST")
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read())
    print("Result: " + json.dumps(result, ensure_ascii=False))
    if result["status"] == "failed":
        raise OneBotError(action + " failed: " + result.get("message", ""))
    return result["data"]


def text(content):
    return {"type": "text", "data": {"text": content}}


def image(url):
    return {"type": "image", "data": {"file": url}}


def at_all():
    return {"type": "at", "data": {"qq": "all"}}


def send_group_msg(group, *segments):
    onebot_call("send_group_msg", {"group_id": int(group), "message": list(segments)})


def send_group_file(group, file_url, file_name, retries=3):
    for attempt in range(1, retries + 1):
        try:
            file = onebot_call("download_file", {"url": file_url})["file"]
            break
        except Exception as e:
            print(f"Download attempt {attempt}/{retries} failed: {e}")
    else:
        raise OneBotError("Failed to download file: " + file_url)
    onebot_call(
        "upload_group_file",
        {"group_id": int(group), "file": file, "name": file_name},
    )
