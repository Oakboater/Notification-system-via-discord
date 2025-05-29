import requests
import time
import csv
import re
from datetime import datetime
import os

REMINDER_FILE = 'reminders.csv'
WEBHOOK_FILE = 'webhook.txt'

def get_webhook_url():
    # Load webhook from file or prompt user to enter one
    if os.path.exists(WEBHOOK_FILE):
        with open(WEBHOOK_FILE, 'r', encoding='utf-8') as f:
            url = f.read().strip()
            if url:
                return url
    return set_webhook_url()

def set_webhook_url():
    # Prompt user to enter a webhook and save it
    url = input("Enter your Discord webhook URL: ").strip()
    with open(WEBHOOK_FILE, 'w', encoding='utf-8') as f:
        f.write(url)
    print("Webhook URL saved.")
    return url

def add_reminder():
    task = input("Task to remind: ")
    while True:
        time_str = input("Time (HH:MM): ")
        if not re.match(r'^\d{2}:\d{2}$', time_str):
            print("Invalid format! Use HH:MM like 14:30")
            continue
        try:
            hour, minute = map(int, time_str.split(":"))
            if not (0 <= hour <= 23 and 0 <= minute <= 59):
                print("Invalid time! Hour must be 00-23 and minute 00-59.")
                continue
            break
        except ValueError:
            print("Invalid time! Use a valid 24-hour format.")
            continue

    with open(REMINDER_FILE, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([task, time_str])
    return task, time_str

def list_reminders():
    try:
        with open(REMINDER_FILE, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                print(row)
    except FileNotFoundError:
        print("No reminders found.")

def send_reminder(task, webhook_url):
    payload = {"content": f"🔔 REMINDER: {task}"}
    requests.post(webhook_url, json=payload)

def check_schedule(webhook_url):
    now = datetime.now().strftime("%H:%M")
    reminders = []
    triggered = []
    try:
        with open(REMINDER_FILE, 'r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                if row[1] == now:
                    send_reminder(row[0], webhook_url)
                    triggered.append(row)
                else:
                    reminders.append(row)
        if triggered:
            with open(REMINDER_FILE, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerows(reminders)
    except FileNotFoundError:
        pass

def add_reminders_loop():
    while True:
        add_reminder()
        answer = input("Would you like to add another task? y/n? ").strip().lower()
        if answer != "y":
            break

def webhook_menu():
    webhook_url = get_webhook_url()
    while True:
        print(f"\nCurrent webhook: {webhook_url}")
        print("1. Change webhook URL")
        print("2. Continue")
        choice = input("Choose an option: ").strip()
        if choice == "1":
            webhook_url = set_webhook_url()
        elif choice == "2":
            break
        else:
            print("Invalid choice.")
    return webhook_url

if __name__ == "__main__":
    print("Welcome to the Timed Task Notification System!")
    webhook_url = webhook_menu()
    add_reminders_loop()
    print("\nCurrent reminders:")
    list_reminders()
    print("\nStarting reminder schedule.. (checks every 60 seconds)")
    while True:
        check_schedule(webhook_url)
        time.sleep(60)
