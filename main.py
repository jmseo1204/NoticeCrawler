from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import telegram
import yaml
from box import Box
import asyncio
import pickle
import os
import sys
from scripts import *

if __name__ == "__main__":

    with open("config.yaml") as f:
        conf = Box(yaml.load(f, Loader=yaml.FullLoader))

    TOKEN = conf.API_KEY
    CHAT_ID = conf.CHAT_ID
    bot = telegram.Bot(token=TOKEN)

    options = webdriver.ChromeOptions()
    options.add_argument("headless")
    options.add_argument("window-size=1920x1080")
    options.add_argument("disable-gpu")
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

    crawlers = [x[:-5] for x in os.listdir("scripts") if x[-3:] == ".py" and x not in ["main.py", "__init__.py"]]
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "scripts"))
    for crawler in crawlers:
        f = eval(crawler)
        text = f(driver, bot, conf)
