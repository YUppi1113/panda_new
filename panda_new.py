import requests
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import datetime
import emoji

TOKEN = "fhiWSDz78NGUGOT9jJFgPfEuJva0A6jGXQyWAAZItjlO3eI+z+B2pgiVJlAu+1MVPbTfske4Pfzf8ljeHO3Knh+7DeB+0jW4iXQ/sfb8IFzD2vqV4q4YJxnmXcN1v+OYN3MnBBt/AZTn+UnevKdYSAdB04t89/1O/w1cDnyilFU="
USERNAME="a0223555"
PASSWORD="Yuto1113154649"

url = "https://api.line.me/v2/bot/message/broadcast"
headers = {"Authorization": "Bearer " + TOKEN, "Content-Type": "application/json"}

panda_url = "https://panda.ecs.kyoto-u.ac.jp/portal"

options = Options()
options.add_argument(
    'window-size=1400,2000')

options.add_argument('start-maximized')
options.add_argument('--headless')

driver = webdriver.Chrome(options=options)
driver.implicitly_wait(10)
driver.get(panda_url)
contents_list = []
# ログイン
driver.find_element(By.CSS_SELECTOR, "#loginLink1").click()
driver.find_element(By.CSS_SELECTOR, "#username").send_keys(USERNAME)
driver.find_element(By.CSS_SELECTOR, "#password").send_keys(PASSWORD)
driver.find_element(
    By.CSS_SELECTOR, "#fm1 > div.row.btn-row > input.btn-submit"
).click()

driver.implicitly_wait(2)

# 授業数取得
driver.find_element(By.CSS_SELECTOR, "#viewAllSites").click()
cources_tag = driver.find_elements(
    By.CSS_SELECTOR,
    "#otherSitesCategorWrap > div.moresites-left-col > div:nth-child(1) > ul > li > div > a", )
driver.find_element(By.CSS_SELECTOR, "#viewAllSites").click()


# 各授業の課題ページに飛ぶ
def to_kadai(i):
    driver.find_element(By.CSS_SELECTOR, "#viewAllSites").click()
    cource_click = driver.find_element(By.CSS_SELECTOR,
                                       f"#otherSitesCategorWrap > div.moresites-left-col > div:nth-child(1) > ul > li:nth-child({i + 1}) > div > a")
    driver.execute_script("arguments[0].click();", cource_click)

    # 課題ページへ
    driver.find_element(By.CSS_SELECTOR,
                        "#toolMenu > ul > li > a > div.icon-sakai--sakai-assignment-grades").click()
    content(i)


# 各授業ページ内の課題情報を取得する
def content(i):
    kadai_num = len(driver.find_elements(By.CSS_SELECTOR,
                                         "#col1 > div > div.portletBody.container-fluid > form > div > table > tbody > tr")) - 1
    if kadai_num > 0:
        for _ in range(kadai_num):
            course(_ + 1)
    # if i<=len(cources_tag)-2:
    #     to_kadai(i + 1)


# 各課題の各項目を取得
def course(i):
    course_name = driver.find_element(By.CSS_SELECTOR,
                                      "#topnav > li.Mrphs-sitesNav__menuitem.is-selected > a.link-container").text
    try:
        kadai_title = driver.find_element(By.CSS_SELECTOR,
                                          f"#col1 > div > div.portletBody.container-fluid > form > div > table > tbody > tr:nth-child({i + 1}) > td:nth-child(1) > strong > a").text
    except:
        kadai_title = driver.find_element(By.CSS_SELECTOR,
                                          f"#col1 > div > div.portletBody.container-fluid > form > div > table > tbody > tr:nth-child({i + 1}) > td:nth-child(1)  > a").text
    kadai_status = driver.find_element(By.CSS_SELECTOR,
                                       f"#col1 > div > div.portletBody.container-fluid > form > div > table > tbody > tr:nth-child({i + 1}) > td:nth-child(2)").text
    kadai_date = driver.find_element(By.CSS_SELECTOR,
                                     f"#col1 > div > div.portletBody.container-fluid > form > div > table > tbody > tr:nth-child({i + 1}) > td:nth-child(4)").text
    dt_kadai = datetime.datetime(year=int(kadai_date[0:4]), month=int(kadai_date[5:7]),
                                 day=int(kadai_date[8:10]),
                                 hour=int(kadai_date[11:kadai_date.find(":")]))
    now = datetime.datetime.now()
    dt_now = datetime.datetime(year=now.year, month=now.month, day=now.day, hour=now.hour,
                               minute=now.minute)
    kadai_limit = dt_kadai - dt_now
    if kadai_status == "未開始" and 0 <= kadai_limit.days <= 7:
        contents_list.append([course_name, kadai_title, kadai_date, kadai_limit])


# メインプログラム
for i in range(len(cources_tag)):
    to_kadai(i)
dict = {i: contents_list[i][3] for i in range(len(contents_list))}
sorted_dict = sorted(dict.items(), key=lambda x: x[1])
index_list = [sorted_dict[i][0] for i in range(len(sorted_dict))]
sorted_list = [contents_list[i] for i in index_list]

# ラインに出力する本文
text = "期限７日以内の未開始の課題一覧"
for i in range(len(sorted_list)):
    limit_date=sorted_list[i][3].days
    if limit_date>2:
        text_mini = (f"\n\n{sorted_list[i][0]}\n"
                     f"{sorted_list[i][1]}\n"
                     f"期限:{sorted_list[i][2]}\n"
                     f"あと{sorted_list[i][3].days}日{sorted_list[i][3].seconds // 3600}時間{sorted_list[i][3].seconds % 3600 // 60}分")
    else:
        text_mini = (f"\n\n{emoji.emojize(':warning:')}{sorted_list[i][0]}\n"
                     f"{sorted_list[i][1]}\n"
                     f"期限:{sorted_list[i][2]}\n"
                     f"あと{sorted_list[i][3].days}日{sorted_list[i][3].seconds // 3600}時間{sorted_list[i][3].seconds % 3600 // 60}分")

    text += text_mini

# json形式でメッセージを定義
message_list = {
    'messages': [
        {
            'type': 'text',
            'text': text
        }
    ]
}

# jsonにエンコードしてラインにtext送信
data = json.dumps(message_list)
response = requests.post(url, headers=headers, data=data)

