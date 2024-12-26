from flask import Flask, jsonify, render_template, request
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from pymongo import MongoClient
import uuid
from datetime import datetime

app = Flask(__name__)

# Setup MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['twitter_data']
collection = db['trending_topics']

chromedriver_path = r"C:\Users\samit\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe"
service = Service(chromedriver_path)

PROXY = "http://samith:samith1%40@us-rotating.proxymesh.com:31280"
  # Replace with your ProxyMesh credentials

def get_trending_topics():
    options = webdriver.ChromeOptions()
    options.add_argument(f"--proxy-server={PROXY}")
    options.add_argument("--proxy-bypass-list=*")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--proxy-type=http")
    driver = webdriver.Chrome(service=service, options=options)

    try:
        driver.get('https://twitter.com/login')
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, 'text')))
        time.sleep(3)

        # Input Twitter credentials
        username = driver.find_element(By.NAME, 'text')
        username.send_keys('@ChessSamith')  # Replace with your username
        username.send_keys(Keys.RETURN)
        time.sleep(2)

        # Handle email field if prompted
        try:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, 'text')))
            email = driver.find_element(By.NAME, 'text')
            email.send_keys('samithchess4@gmail.com')  # Replace with your email
            email.send_keys(Keys.RETURN)
            time.sleep(2)
        except Exception:
            print("Email not required or already entered")

        # Enter password
        try:
            password = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, 'password')))
            password.send_keys('samithChess1@')  # Replace with your password
            password.send_keys(Keys.RETURN)
            time.sleep(5)
        except Exception:
            print("Password field did not appear within the timeout period")

        # Navigate to the trending page
        driver.get('https://x.com/explore/tabs/trending')
        time.sleep(5)

        # Find trending topics
        trending_elements = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, '[data-testid="trend"]'))
        )

        trending_topics = []
        for index, element in enumerate(trending_elements[:5]):  # Fetch top 5
            try:
                trend_name = element.text.split('\n')[3]
                if trend_name:
                    trending_topics.append(trend_name)
            except Exception as e:
                print(f"Error extracting trend {index + 1}: {e}")

        # Retrieve IP address used by the proxy
        driver.get('https://api.ipify.org')
        ip_address = driver.find_element(By.TAG_NAME, 'body').text

        unique_id = str(uuid.uuid4())
        end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        record = {
            "_id": unique_id,
            "trends": trending_topics,
            "timestamp": end_time,
            "ip_address": ip_address
        }

        collection.insert_one(record)
        return record

    finally:
        driver.quit()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/run-script', methods=['GET'])
def run_script():
    record = get_trending_topics()
    return jsonify(record)

if __name__ == "__main__":
    app.run(debug=True)
