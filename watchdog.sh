#!/data/data/com.termux/files/usr/bin/sh

# এই ফাইলটিতে Python অ্যাপের প্রসেস আইডি (PID) সেভ করা হবে
PID_FILE="app.pid"

# অ্যাপটি শুরু করার ফাংশন
start_app() {
    echo "Starting python app..."
    # অ্যাপটিকে ব্যাকগ্রাউন্ডে চালান এবং এর PID সেভ করুন
    nohup python app.py > /dev/null 2>&1 &
    echo $! > $PID_FILE
    echo "App started with PID $(cat $PID_FILE)"
}

# অ্যাপটি বন্ধ করার ফাংশন
stop_app() {
    if [ -f $PID_FILE ]; then
        PID=$(cat $PID_FILE)
        echo "Stopping app with PID $PID..."
        # প্রসেসটি আছে কিনা তা পরীক্ষা করুন এবং থাকলে বন্ধ করুন
        if ps -p $PID > /dev/null; then
            kill -9 $PID
        fi
        rm $PID_FILE
    fi
}

# অনন্ত লুপ, যা সবসময় চলতে থাকবে
while true; do
    # ইন্টারনেট সংযোগ পরীক্ষা করার জন্য গুগলকে পিং করুন
    if ping -c 1 8.8.8.8 > /dev/null; then
        # ইন্টারনেট সংযোগ আছে
        
        # অ্যাপটি চলছে কিনা তা পরীক্ষা করুন
        if [ -f $PID_FILE ] && ps -p $(cat $PID_FILE) > /dev/null; then
            # সবকিছু ঠিক আছে, অ্যাপ চলছে
            echo "[$(date)] Internet OK, App is running. No action needed."
        else
            # অ্যাপ চলছে না, এটিকে চালু করতে হবে
            echo "[$(date)] Internet OK, but App is not running. Restarting..."
            stop_app # যদি কোনো পুরনো PID থাকে, তবে প্রসেসটি বন্ধ করুন
            start_app
        fi
    else
        # ইন্টারনেট সংযোগ নেই
        echo "[$(date)] Internet connection is down. Stopping app if running."
        stop_app
    fi
    
    # প্রতি ৬০ সেকেন্ড পর পর পরীক্ষা করুন
    sleep 60
done
