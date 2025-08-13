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

# Frontend (Vite läuft auf Port 5173)
if is_port_in_use 5173; then
  confirm_kill_port 5173
fi
echo "✅ Starte Frontend auf Port 5173..."
(cd frontend && npm run dev) &
FRONTEND_PID=$!

# Backend
if is_port_in_use 8000; then
  confirm_kill_port 8000
fi
echo "✅ Starte Backend auf Port 8000..."
(UNIFIED_SERVER_MODE=http uv run python unified_server.py) &
BACKEND_PID=$!

echo ""
echo "✅ Entwicklungsumgebung wurde erfolgreich gestartet."
echo "🔗 Frontend: http://localhost:5173"
echo "🔗 Backend:  http://localhost:8000"
echo ""
echo "📝 Drücke Ctrl+C um beide Server zu beenden..."

# Cleanup function
cleanup() {
  echo ""
  echo "🛑 Beende Server..."
  if [ -n "$FRONTEND_PID" ]; then
    kill -TERM $FRONTEND_PID 2>/dev/null
  fi
  if [ -n "$BACKEND_PID" ]; then
    kill -TERM $BACKEND_PID 2>/dev/null
  fi
  # Kill any remaining processes on these ports
  kill_process_on_port 5173 2>/dev/null
  kill_process_on_port 8000 2>/dev/null
  echo "✅ Server beendet."
  exit 0
}

# Trap Ctrl+C
trap cleanup INT

# Wait for both processes
wait

