#!/bin/bash
# Auto-sync Cloudflare Tunnel URL to GitHub Pages

set -e

REPO_DIR="/home/didar-lahiry/Antigravity/Kishan"
LOG_FILE="/home/didar-lahiry/.config/kishan_tunnel.log"

# Wait for tunnel to acquire URL
sleep 6

URL=$(grep -a -o 'https://[a-zA-Z0-9.-]*\.trycloudflare\.com' "$LOG_FILE" | tail -n 1 || true)

if [ -n "$URL" ]; then
    CURRENT=$(grep -a -o 'https://[a-zA-Z0-9.-]*\.trycloudflare\.com' "$REPO_DIR/docs/app.js" | head -n 1 || true)
    if [ "$URL" != "$CURRENT" ]; then
        echo "[AutoSync] Updating API URL from '$CURRENT' to '$URL'..."
        cd "$REPO_DIR"
        sed -i "s|https://[a-zA-Z0-9.-]*\.trycloudflare\.com|$URL|g" docs/app.js backend/app/static/app.js
        git add docs/app.js backend/app/static/app.js
        git commit -m "chore(auto-sync): update active backend tunnel URL to $URL"
        git push origin main
        echo "[AutoSync] GitHub Pages successfully synced with active URL: $URL"
    else
        echo "[AutoSync] URL is already up-to-date ($URL)."
    fi
fi
