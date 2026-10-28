#!/usr/bin/env bash
# Install the cqnasa systemd timers for the current user.
# Run `uv sync` and create config.json first.
set -euo pipefail

repo="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
unit_dir="${XDG_CONFIG_HOME:-$HOME/.config}/systemd/user"

if [[ ! -x "$repo/.venv/bin/cqnasa" ]]; then
    echo "error: $repo/.venv/bin/cqnasa not found, run 'uv sync' first" >&2
    exit 1
fi
if [[ ! -f "$repo/config.json" ]]; then
    echo "error: $repo/config.json not found, copy config.json.template and fill it in" >&2
    exit 1
fi

mkdir -p "$unit_dir"
for unit in "$repo"/systemd/*; do
    # Point the units at wherever this repo actually lives
    sed "s|%h/cqnasa|$repo|g" "$unit" > "$unit_dir/$(basename "$unit")"
    echo "installed $unit_dir/$(basename "$unit")"
done

systemctl --user daemon-reload
systemctl --user enable --now cqnasa-apod.timer cqnasa-sdo.timer

# Keep the timers running while logged out
if ! loginctl enable-linger "$USER"; then
    echo "warning: could not enable linger, timers will stop when you log out" >&2
fi

systemctl --user list-timers 'cqnasa-*'
