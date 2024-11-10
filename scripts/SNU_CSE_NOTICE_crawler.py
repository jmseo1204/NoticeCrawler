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


def SNU_CSE_NOTICE_crawl(driver, bot, conf):

    MAX_SEARCH_NUM = 15
    searching_keywords = []
    page_link = r"https://cse.snu.ac.kr/community/notice?tag=%EC%99%B8%EB%B6%80%ED%96%89%EC%82%AC%2F%ED%94%84%EB%A1%9C%EA%B7%B8%EB%9E%A8&tag=%EB%82%B4%EB%B6%80%ED%96%89%EC%82%AC%2F%ED%94%84%EB%A1%9C%EA%B7%B8%EB%9E%A8&tag=%EA%B5%90%ED%99%98%ED%95%99%EC%83%9D%2F%EC%9C%A0%ED%95%99&pageNum=1"

    feed_template = (
        "[SNU CSE 공지사항] \n\n"
        + (f"키워드 {searching_keywords}에 해당하는 " if searching_keywords != [] else "")
        + "업데이트 게시글은 다음과 같습니다. \n\n"
    )
    sent_titles_file_loc = os.path.join(os.path.dirname(__file__), "src/SNU_CSE_NOTICE_sent_titles.pkl")
    with open(sent_titles_file_loc, mode="rb") as f:
        sent_titles = pickle.load(f)

    page = driver.get(page_link)
    BASE_LOC = "/html/body/main/div/div[2]/div[2]/ul"
    not_found = True

    i = 1
    block_ptr = 1
    while i < MAX_SEARCH_NUM + 1:
        try:
            title_loc = BASE_LOC + f"/li[{block_ptr}]/span[2]/a/span"
            title = driver.find_element(By.XPATH, title_loc).text

            href_loc = BASE_LOC + f"/li[{block_ptr}]/span[2]/a"
            href = driver.find_element(By.XPATH, href_loc).get_attribute("href")

            date_loc = BASE_LOC + f"/li[{block_ptr}]/span[3]"
            date = driver.find_element(By.XPATH, date_loc).text

            # print(f"{title} : {href}")
            if searching_keywords != []:
                for keyword in searching_keywords:
                    if keyword in title:
                        if title in sent_titles:
                            i = 1e10
                            break
                        feed_template += f"[{keyword}] {date} - {title} : {href}\n"
                        sent_titles.add(title)
                        not_found = False
                        break
            else:
                if title in sent_titles:
                    i = MAX_SEARCH_NUM + 1
                else:
                    feed_template += f"{date} - {title} : {href}\n"
                    sent_titles.add(title)
                    not_found = False

        except Exception as e:
            eq_loc = page_link[::-1].find("=")
            page_link = page_link[:-eq_loc] + str(int(page_link[-eq_loc:]) + 1)
            page = driver.get(page_link)
            block_ptr = 1
            continue
        block_ptr += 1
        i += 1

    if not not_found:
        print("[SENDING MESSAGE]...")
        print(feed_template)
        asyncio.run(bot.send_message(text=feed_template, chat_id=conf.CHAT_ID))
    else:
        print("No one has been updated.")

    with open(sent_titles_file_loc, mode="wb") as f:
        pickle.dump(sent_titles, f)

    return feed_template
