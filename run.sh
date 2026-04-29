#!/bin/bash
set -e

PORT=80
APP_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV="$APP_DIR/.venv"
PID_FILE="$APP_DIR/.server.pid"
LOG_FILE="$APP_DIR/server.log"

case "$1" in

  deploy)
    echo "Pulling latest from repo..."
    cd "$APP_DIR"
    git pull
    echo "Installing/updating dependencies..."
    "$VENV/bin/pip" install -q -r requirements.txt
    echo "Deploy complete."
    ;;

  start)
    if [ -f "$PID_FILE" ] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
      echo "Server is already running (PID $(cat "$PID_FILE"))."
      exit 1
    fi
    echo "Starting Media Arts home on port $PORT..."
    cd "$APP_DIR"
    nohup "$VENV/bin/python3" app.py >> "$LOG_FILE" 2>&1 &
    echo $! > "$PID_FILE"
    echo "Started (PID $!)."
    ;;

  stop)
    # Try PID file first
    if [ -f "$PID_FILE" ]; then
      PID=$(cat "$PID_FILE")
      if kill -0 "$PID" 2>/dev/null; then
        kill "$PID"
        rm -f "$PID_FILE"
        echo "Stopped (PID $PID)."
        exit 0
      else
        rm -f "$PID_FILE"
      fi
    fi
    # Fall back to finding whatever owns the port
    PID=$(lsof -ti tcp:"$PORT" 2>/dev/null || true)
    if [ -n "$PID" ]; then
      kill $PID
      echo "Stopped process(es) on port $PORT (PID $PID)."
    else
      echo "No process found on port $PORT."
    fi
    ;;

  *)
    echo "Usage: $0 {deploy|start|stop}"
    exit 1
    ;;

esac
