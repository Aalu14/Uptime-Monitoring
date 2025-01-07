from flask import Flask, render_template, request, redirect, url_for
import requests
import pymongo
from datetime import datetime
from urllib.parse import unquote
import ssl
import socket

app = Flask(__name__)

HOMEPAGE = "dashboard.html"

# MongoDB connection
client = pymongo.MongoClient("mongodb+srv://aleenaarif14:123@cluster0.9vkt7.mongodb.net/dev?retryWrites=true&w=majority&appName=Cluster0")
db = client["uptime_monitoring"]
urls_collection = db["urls"]


def check_url_status():
    """Check the status of URLs and update them in the database."""
    status = {}
    urls = urls_collection.find()
    for url_doc in urls:
        url = url_doc['url']
        try:
            response = requests.get(url, timeout=5)
            status[url] = "UP" if response.status_code == 200 else "DOWN"
        except:
            status[url] = "DOWN"
        urls_collection.update_one({"url": url}, {"$set": {"status": status[url], "last_checked": datetime.now()}})
    return status


@app.route("/")
def index():
    """Front page for navigation."""
    return render_template("index.html")


@app.route("/website-monitoring", methods=["GET", "POST"])
def website_monitoring():
    """Website Monitoring dashboard."""
    if request.method == "POST":
        url = request.form["url"]
        description = request.form["description"]
        if url and description:
            urls_collection.insert_one({"url": url, "description": description, "status": "Unknown", "last_checked": None})
        return redirect(url_for("dashboard"))
    
    urls = urls_collection.find()
    status = check_url_status()
    return render_template(HOMEPAGE, status=status, urls=urls)


@app.route("/delete/<path:url>")
def delete_url(url):
    """Delete a URL from the monitoring list."""
    decoded_url = unquote(url)
    result = urls_collection.delete_one({"url": decoded_url})
    return redirect(url_for("dashboard"))


@app.route("/ssl-monitoring", methods=["GET", "POST"])
def ssl_monitoring():
    """Page for SSL Monitoring."""
    if request.method == "POST":
        domain = request.form["domain"]
        ssl_expiration, error_message = check_ssl_expiry(domain)
        return render_template("ssl_result.html", domain=domain, ssl_expiration=ssl_expiration, error_message=error_message)
    return render_template("ssl_monitoring.html")


def check_ssl_expiry(domain):
    """Check SSL expiration date for a given domain."""
    try:
        context = ssl.create_default_context()
        with socket.create_connection((domain, 443), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                ssl_info = ssock.getpeercert()
                expiration_date = datetime.strptime(ssl_info["notAfter"], "%b %d %H:%M:%S %Y GMT")
                return expiration_date, None
    except Exception as e:
        return None, str(e)


if __name__ == "__main__":
    app.run(debug=True)
