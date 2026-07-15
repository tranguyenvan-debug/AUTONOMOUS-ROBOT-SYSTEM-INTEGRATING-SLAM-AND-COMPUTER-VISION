#!/bin/bash
sleep 15
IP=$(hostname -I | awk '{print $1}')
TOKEN="YOUR_TELEGRAM_BOT_TOKEN_HERE"
CHAT_ID="7056257229"
curl -s -X POST "https://api.telegram.org/bot${TOKEN}/sendMessage" \
  -d chat_id="${CHAT_ID}" \
  -d text="🤖 Robot đã khởi động!
🌐 Web: http://${IP}:8080
📡 IP: ${IP}"
