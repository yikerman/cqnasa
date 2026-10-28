# OneBot NASA Notification Bot

- NASA APoD (checked hourly, sent once per new image; video days are skipped)
- NASA SDO (a 48-hour video every 6 hours, rotating through 9 AIA wavelengths)

Sends to a QQ group through the OneBot 11 HTTP API of [NapCat](https://napneko.github.io/).

## Setup

1. In NapCat, enable an HTTP server (default port 3000) and set a token.
2. Clone this repo and run `uv sync`.
3. `cp config.json.template config.json` and fill in:
   - `API_KEY`: NASA API key (https://api.nasa.gov)
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
