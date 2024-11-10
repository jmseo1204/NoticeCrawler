# selenium 4
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


def KAIST_AI_crawl(driver, bot, conf):

    MAX_BLOCKS = 3
    searching_keywords = ["2024"]
    search_query = ""
    page_num = 1
    page_link = f"https://gsai.kaist.ac.kr/?s=KAIRI"
    feed_template = (
        f"[KAIST AI 공지사항] \n\n키워드 {searching_keywords}에 해당하는 업데이트 게시글은 다음과 같습니다. \n\n"
    )
    sent_titles_file_loc = os.path.join(os.path.dirname(__file__), "src/KAIST_sent_titles.pkl")
    with open(sent_titles_file_loc, mode="rb") as f:
        sent_titles = pickle.load(f)

    page = driver.get(page_link)
    BASE_LOC = "/html/body/div[1]/div[2]/div/div[2]/div/div/div/div[1]"

    not_found = True

    for i in range(1, MAX_BLOCKS + 1):
        title_loc = BASE_LOC + f"/article[{i}]/div[2]/div[2]/div/a/span"
        block = driver.find_element(By.XPATH, title_loc)
        title = block.text
        href_loc = BASE_LOC + f"/article[{i}]/div[2]/div[2]/div/a"
        block = driver.find_element(By.XPATH, href_loc)
        href = block.get_attribute("href")

        # date_loc = BASE_LOC + f"/tr[{i}]/td[2]"
        # date = driver.find_element(By.XPATH, date_loc).text

        # print(f"{title} : {href}")
        for keyword in searching_keywords:
            if keyword in title and title not in sent_titles:
                feed_template += f"[{keyword}] {title} : {href}\n"
                sent_titles.add(title)
                not_found = False
                break

    if not not_found:
        print("[SENDING MESSAGE]...")
        print(feed_template)
        asyncio.run(bot.send_message(text=feed_template, chat_id=conf.CHAT_ID))
    else:
        print("No one has been updated.")

    with open(sent_titles_file_loc, mode="wb") as f:
        pickle.dump(sent_titles, f)
