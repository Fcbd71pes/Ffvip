#!/data/data/com.termux/files/usr/bin/sh

PID_FILE="app.pid"

start_app() {
    echo "Starting python app..."
    nohup python app.py > /dev/null 2>&1 &
    echo $! > $PID_FILE
    echo "App started with PID $(cat $PID_FILE)"
}

stop_app() {
    if [ -f $PID_FILE ]; then
        PID=$(cat $PID_FILE)
        echo "Stopping app with PID $PID..."
        if ps -p $PID > /dev/null; then
            kill -9 $PID
        fi
        rm $PID_FILE
    fi
}

while true; do
    if ping -c 1 8.8.8.8 > /dev/null; then
        if [ -f $PID_FILE ] && ps -p $(cat $PID_FILE) > /dev/null; then
            echo "[$(date)] Internet OK, App is running."
        else
            echo "[$(date)] Internet OK, but App is not running. Restarting..."
            stop_app
            start_app
        fi
    else
        echo "[$(date)] Internet connection is down. Stopping app if running."
        stop_app
    fi
    sleep 60
done
