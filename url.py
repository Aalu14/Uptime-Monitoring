import requests
from datetime import datetime
import pymongo
import logging
from apscheduler.schedulers.background import BackgroundScheduler
import time

client = pymongo.MongoClient("mongodb+srv://aleenaarif14:123@cluster0.9vkt7.mongodb.net/dev?retryWrites=true&w=majority&appName=Cluster0")
db = client["uptime_monitoring"]
urls_collection = db["urls"]

slack_webhook_url = "https://hooks.slack.com/services/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"

logging.basicConfig(filename='url_status_log.txt', level=logging.INFO)


def check_url(url):
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return "UP"
        else:
            return "DOWN"
    except requests.exceptions.RequestException as e:
        print(f"Error checking {url}: {e}")
        return "DOWN"

def log_status(url, status):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("url_status_log.txt", "a") as log_file:
        log_file.write(f"{timestamp} - {url} is {status}\n")
    print(f"Logged: {url} is {status}")

def send_slack_alert(url, status):
    message = {"text": f"🔔 Status Update: {url} is {status}!"}
    try:
        response = requests.post(slack_webhook_url, json=message)
        
        print(f"Slack response status: {response.status_code}")
        print(f"Slack response text: {response.text}")
        
        if response.status_code == 200:
            print(f"Slack alert sent for {url} (status: {status})!")
        else:
            print(f"Failed to send Slack alert for {url}. HTTP Status: {response.status_code}")
            print(f"Response: {response.text}")
    
    except Exception as e:
        print(f"Error sending Slack alert: {e}")

def check_and_alert():
    """Check the status of all URLs and alert if DOWN."""
    print("Checking URLs...")  
    urls = urls_collection.find()
    
    for url_doc in urls:
        url = url_doc["url"]
        print(f"Checking: {url}")  
        
        status = check_url(url)
        log_status(url, status)  
        
        send_slack_alert(url, status)
        
        urls_collection.update_one({"url": url}, {"$set": {"status": status, "last_checked": datetime.now()}})

if __name__ == "__main__":
    check_and_alert()





