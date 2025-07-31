#!/bin/bash

# Funktionen
is_port_in_use() {
  lsof -i tcp:$1 >/dev/null
}

kill_process_on_port() {
  PID=$(lsof -ti tcp:$1)
  if [ -n "$PID" ]; then
    echo "Beende Prozess auf Port $1 (PID: $PID)..."
    kill -9 "$PID"
  fi
}

confirm_kill_port() {
  local PORT=$1
  echo "⚠️  Port $PORT ist bereits belegt."
  read -p "Möchtest du den Prozess auf Port $PORT beenden? (y/n): " yn
  case $yn in
    [Yy]* ) kill_process_on_port $PORT ;;
    * ) echo "Start abgebrochen."; exit 1 ;;
  esac
}

# Frontend
if is_port_in_use 5137; then
  confirm_kill_port 5137
fi
echo "✅ Starte Frontend auf Port 5137..."
(cd frontend && npm run dev) &

# Backend
if is_port_in_use 8000; then
  confirm_kill_port 8000
fi
echo "✅ Starte Backend auf Port 8000..."
(python3 http_server.py) &

echo "✅ Entwicklungsumgebung wurde erfolgreich gestartet."
echo "🔗 Frontend: http://localhost:5137"
echo "🔗 Backend:  http://localhost:8000"

