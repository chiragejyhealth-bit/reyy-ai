#!/usr/bin/env bash
set -e

# Start a virtual display so Chrome can open a GUI
Xvfb :99 -screen 0 "${XVFB_WHD:-1920x1080x24}" &
export DISPLAY=:99

# Hand over to whatever CMD the image received
exec "$@"
