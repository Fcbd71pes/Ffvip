#!/data/data/com.termux/files/usr/bin/sh

# --- রঙ এবং স্টাইলের জন্য ভেরিয়েবল ---
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# --- স্বাগতম বার্তা ---
echo -e "${BLUE}=====================================================${NC}"
echo -e "${YELLOW} Welcome to the Ffvip Project Auto-Setup Script! ${NC}"
echo -e "${BLUE}=====================================================${NC}"
echo "This script will automatically set up the entire project for you."
echo ""

# --- ধাপ ১: সিস্টেম প্যাকেজ ইনস্টল এবং আপডেট করা ---
echo -e "${YELLOW}[*] Updating package lists and upgrading...${NC}"
pkg update -y && pkg upgrade -y
echo ""
# --- *** গুরুত্বপূর্ণ পরিবর্তন এখানে *** ---
echo -e "${YELLOW}[*] Installing required packages (python, git, nano, cloudflared)...${NC}"
pkg install python git nano cloudflared -y
echo -e "${GREEN}[✔] System packages installed successfully.${NC}"
echo ""

# --- ধাপ ২: Python লাইব্রেরি ইনস্টল করা ---
echo -e "${YELLOW}[*] Installing required Python libraries (Flask, python-telegram-bot, requests)...${NC}"
pip install --no-cache-dir Flask python-telegram-bot requests
echo -e "${GREEN}[✔] Python libraries installed successfully.${NC}"
echo ""

# --- ধাপ ৩: ব্যবহারকারীর কাছ থেকে ইনপুট নেওয়া ---
echo -e "${YELLOW}[*] Please provide your bot credentials.${NC}"
read -p "Enter your Telegram BOT_TOKEN: " BOT_TOKEN
read -p "Enter your BOSS_ADMIN_ID (your numeric Telegram ID): " BOSS_ADMIN_ID
echo ""

# --- ধাপ ৪: app.py ফাইল কনফিগার করা ---
echo -e "${YELLOW}[*] Configuring app.py with your credentials...${NC}"
# sed কমান্ড ব্যবহার করে placeholder টেক্সটগুলো আসল টোকেন ও আইডি দিয়ে প্রতিস্থাপন করা
sed -i "s/BOT_TOKEN = \"YOUR_TELEGRAM_BOT_TOKEN\"/BOT_TOKEN = \"$BOT_TOKEN\"/" app.py
sed -i "s/BOSS_ADMIN_ID = 123456789/BOSS_ADMIN_ID = $BOSS_ADMIN_ID/" app.py
echo -e "${GREEN}[✔] app.py configured successfully.${NC}"
echo ""

# --- ধাপ ৫: watchdog.sh কে এক্সিকিউটেবল বানানো ---
echo -e "${YELLOW}[*] Making watchdog.sh executable...${NC}"
chmod +x watchdog.sh
echo -e "${GREEN}[✔] watchdog.sh is now executable.${NC}"
echo ""

# --- ধাপ ৬: Termux অটো-স্টার্ট সেটআপ করা (.bashrc) ---
echo -e "${YELLOW}[*] Setting up auto-start script in .bashrc...${NC}"

# .bashrc ফাইলে যোগ করার জন্য কোড ব্লক
BASHRC_CODE="
# Ffvip Project Auto-start
# Check if the watchdog script is already running
if ! pgrep -f \"watchdog.sh\" > /dev/null
then
    echo \"Starting Ffvip watchdog script in background...\"
    # Go to the project directory and run watchdog.sh in the background
    (cd ~/Ffvip && sh watchdog.sh > watchdog.log 2>&1 &)
fi
"
# পরীক্ষা করুন যে এই কোডটি আগে থেকেই .bashrc ফাইলে আছে কিনা
if ! grep -q "# Ffvip Project Auto-start" ~/.bashrc; then
    echo "$BASHRC_CODE" >> ~/.bashrc
    echo -e "${GREEN}[✔] Auto-start script added to .bashrc successfully.${NC}"
else
    echo -e "${YELLOW}[!] Auto-start script already exists in .bashrc. Skipping.${NC}"
fi
echo ""

# --- চূড়ান্ত বার্তা ---
echo -e "${BLUE}=====================================================${NC}"
echo -e "${GREEN}Congratulations! Setup is complete! 🎉${NC}"
echo -e "${BLUE}=====================================================${NC}"
echo ""
echo -e "To start the server, you can either:"
echo -e "1. ${YELLOW}Close and reopen Termux.${NC} The server will start automatically."
echo -e "2. ${YELLOW}Run the watchdog script manually now:${NC} (cd ~/Ffvip && sh watchdog.sh &)"
echo ""
echo "Your server will now run in the background and restart automatically."
echo "You can manage everything from your Telegram bot."
echo ""
