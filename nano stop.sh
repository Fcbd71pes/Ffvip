#!/data/data/com.termux/files/usr/bin/sh

# রঙ এবং স্টাইলের জন্য ভেরিয়েবল
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}Stopping all Ffvip related processes...${NC}"

# --- ধাপ ১: ওয়াচডগ স্ক্রিপ্টটি বন্ধ করা ---
# pkill কমান্ড -f ফ্ল্যাগ দিয়ে নামের অংশবিশেষ খুঁজে প্রসেস বন্ধ করে
echo "[*] Attempting to stop the watchdog script..."
pkill -f "watchdog.sh"
# pgrep দিয়ে নিশ্চিত হওয়া যে প্রসেসটি বন্ধ হয়েছে
if ! pgrep -f "watchdog.sh" > /dev/null; then
    echo -e "${GREEN}[✔] Watchdog script stopped successfully.${NC}"
else
    echo -e "${RED}[!] Failed to stop the watchdog script.${NC}"
fi

# --- ধাপ ২: Python অ্যাপটি (app.py) বন্ধ করা ---
echo "[*] Attempting to stop the Python app (app.py)..."
pkill -f "app.py"
if ! pgrep -f "app.py" > /dev/null; then
    echo -e "${GREEN}[✔] Python app stopped successfully.${NC}"
else
    echo -e "${RED}[!] Failed to stop the Python app.${NC}"
fi

# --- ধাপ ৩: Cloudflare Tunnel বন্ধ করা ---
echo "[*] Attempting to stop the Cloudflare Tunnel (cloudflared)..."
pkill -f "cloudflared"
if ! pgrep -f "cloudflared" > /dev/null; then
    echo -e "${GREEN}[✔] Cloudflare Tunnel stopped successfully.${NC}"
else
    echo -e "${RED}[!] Failed to stop the Cloudflare Tunnel.${NC}"
fi

# --- ধাপ ৪: PID ফাইল মুছে ফেলা (যদি থাকে) ---
if [ -f "app.pid" ]; then
    rm app.pid
    echo "[*] PID file removed."
fi

echo -e "\n${GREEN}All services have been stopped. The project will not restart automatically until you reopen Termux.${NC}"
