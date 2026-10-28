# OneBot NASA Notification Bot

- NASA APoD (checked hourly, sent once per new post; videos are uploaded as group files)
- NASA SDO (a 48-hour video every 6 hours, rotating through 9 AIA wavelengths)

Sends to a QQ group through the OneBot 11 HTTP API of [NapCat](https://napneko.github.io/).

## Setup

1. In NapCat, enable an HTTP server (default port 3000) and set a token.
2. Clone this repo and run `uv sync`. Install [Deno](https://deno.com) or Node.js too:
   yt-dlp needs a JS runtime to download the occasional YouTube APOD.
3. `cp config.json.template config.json` and fill in:
   - `ONEBOT_API`: `host:port` of NapCat's HTTP server
   - `ACCESS_TOKEN`: the NapCat HTTP token (leave empty if none)
   - `GROUP`: target QQ group ID
4. Try it: `uv run cqnasa apod` / `uv run cqnasa sdo`

## Scheduling with systemd (user scope)

```sh
./install.sh
```

This copies the units in `systemd/` to `~/.config/systemd/user/` (pointed at this
checkout), enables the timers, and enables linger so they keep running while logged out.

Logs: `journalctl --user -u cqnasa-apod -u cqnasa-sdo`

## Notes

The official APOD API broke when APOD moved to science.nasa.gov
([nasa/apod-api#184](https://github.com/nasa/apod-api/issues/184)), so this reads the
WordPress REST API behind the new site instead. If a video can't be uploaded, the still
image and a link to the post are sent instead. Keep yt-dlp current with
`uv lock --upgrade-package yt-dlp && uv sync`.
