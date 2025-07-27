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

# --- সিস্টেম প্যাকেজ ইনস্টল এবং আপডেট করা ---
echo -e "${YELLOW}[*] Updating package lists and upgrading...${NC}"
pkg update -y && pkg upgrade -y
echo ""
echo -e "${YELLOW}[*] Installing required packages (python, git, nano, cloudflared)...${NC}"
pkg install python git nano cloudflared -y
echo -e "${GREEN}[✔] System packages installed successfully.${NC}"
echo ""

# --- Python লাইব্রেরি ইনস্টল করা ---
echo -e "${YELLOW}[*] Installing required Python libraries...${NC}"
pip uninstall -y telegram
pip install --no-cache-dir Flask python-telegram-bot requests
echo -e "${GREEN}[✔] Python libraries installed successfully.${NC}"
echo ""

# --- ব্যবহারকারীর কাছ থেকে ইনপুট নেওয়া ---
echo -e "${YELLOW}[*] Please provide your bot credentials.${NC}"
read -p "Enter your Telegram BOT_TOKEN: " BOT_TOKEN
read -p "Enter your BOSS_ADMIN_ID (your numeric Telegram ID): " BOSS_ADMIN_ID
echo ""

# --- app.py ফাইল কনফিগার করা ---
echo -e "${YELLOW}[*] Configuring app.py with your credentials...${NC}"
sed -i "s/BOT_TOKEN = \"YOUR_TELEGRAM_BOT_TOKEN\"/BOT_TOKEN = \"$BOT_TOKEN\"/" app.py
sed -i "s/BOSS_ADMIN_ID = 123456789/BOSS_ADMIN_ID = $BOSS_ADMIN_ID/" app.py
echo -e "${GREEN}[✔] app.py configured successfully.${NC}"
echo ""

# --- watchdog.sh কে এক্সিকিউটেবল বানানো ---
echo -e "${YELLOW}[*] Making watchdog.sh executable...${NC}"
chmod +x watchdog.sh
echo -e "${GREEN}[✔] watchdog.sh is now executable.${NC}"
echo ""

# --- Termux অটো-স্টার্ট সেটআপ করা (.bashrc) ---
echo -e "${YELLOW}[*] Setting up auto-start script in .bashrc...${NC}"
BASHRC_CODE="
# Ffvip Project Auto-start
if ! pgrep -f \"watchdog.sh\" > /dev/null
then
    echo \"Starting Ffvip watchdog script in background...\"
    (cd ~/Ffvip && sh watchdog.sh > watchdog.log 2>&1 &)
fi
"
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
echo -e "To start the server, ${YELLOW}fully close and reopen Termux.${NC}"
echo "The server will start automatically in the background."
echo "You can manage everything from your Telegram bot."
echo ""
