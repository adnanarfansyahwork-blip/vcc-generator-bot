#!/usr/bin/env bash
# Script Deploy VCC Generator Bot ke VPS
set -euo pipefail

VPS="${VPS:-ubuntu@43.157.204.9}"
SSH_KEY="${SSH_KEY:-$HOME/.ssh/sumopod_vps}"
APP_DIR=/home/ubuntu/vcc-generator-bot

echo "==> Mengirim file terbaru ke VPS ($VPS)..."
scp -i "$SSH_KEY" -o StrictHostKeyChecking=no bot.py fsub.py generator.py requirements.txt README.md "$VPS:$APP_DIR/"

echo "==> Restarting vcc-bot di PM2..."
ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$VPS" "pm2 restart vcc-bot && sleep 2 && pm2 logs vcc-bot --lines 8 --nostream"
