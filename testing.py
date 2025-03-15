from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import re
import csv

# Chrome 드라이버 경로 설정
chrome_driver_path = './chromedriver_win64/chromedriver.exe'  
db_path = './DB'
db_path_keys = db_path+'/keys.txt'
db_path_cp = db_path+'/checkpoint.txt'

with open(db_path_keys, "r", encoding="utf-8") as file:
    content = file.read()

    id = content.split("\n")[0]
    pw = content.split("\n")[1]

with open(db_path_cp, "r", encoding="utf-8") as file:
    content = file.read()

    check_point = content

chrome_options = Options()

# 드라이버 서비스 생성 및 브라우저 실행
service = Service(chrome_driver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)



try:

    # 로그인
    boj_login = "https://www.acmicpc.net/login?next=%2F"
    driver.get(boj_login)

    time.sleep(2)
    
    id_input = driver.find_element(By.CSS_SELECTOR, "#login_form > div:nth-child(2) > input")
    id_input.send_keys(id)

    pw_input = driver.find_element(By.CSS_SELECTOR, "#login_form > div:nth-child(3) > input")
    pw_input.send_keys(pw)

    login_button = driver.find_element(By.CSS_SELECTOR, "#submit_button")
    login_button.click()

    time.sleep(2)

    driver.get("https://www.acmicpc.net/status?group_id=23106")

    time.sleep(2)

    catch_flag = 1
    first_elem = 0
    elem_read = 123

    table_rows = driver.find_elements(By.CSS_SELECTOR, "table.table tbody tr")

    class boj_data:
        def __init__(self,num,id,problem,tier,date):
            self.num = num
            self.id = id
            self.problem = problem
            self.tier  = tier
            self.date = date

    class boj_date:
        def __init__(self,year,month,day):
            self.year = year
            self.month = month
            self.day = day


    # 각 행의 데이터를 추출
    save_data = list()
    while True:

        for row in table_rows:

            if row.find_element(By.CLASS_NAME, 'result').text=='맞았습니다!!':

                boj_num = row.find_elements(By.TAG_NAME, 'td')[0].text
                elem_read = boj_num

                if first_elem == 0:
                    first_elem = boj_num

                if elem_read == check_point:
                    break

                boj_id = row.find_elements(By.TAG_NAME, 'td')[1].text
                boj_problem = row.find_elements(By.TAG_NAME, 'td')[2].text[1:]
                boj_tier_elem = row.find_element(By.CSS_SELECTOR, "td:nth-child(3) > img")
                boj_tier = boj_tier_elem.get_attribute("src").split("/")[-1].replace(".svg", "")
                elem = row.find_element(By.CSS_SELECTOR, "a.real-time-update.show-date")
                data_title = elem.get_attribute("data-original-title")

                # regex로 년 월 일 추출
                match = re.search(r'(\d{4})년\s*(\d{1,2})월\s*(\d{1,2})일', data_title)
                if match:
                    year, month, day = match.groups()

                save_data.append(boj_data(boj_num, boj_id,boj_problem, boj_tier,boj_date(year,month,day)))

        if elem_read != check_point:
            next_button =driver.find_element(By.CSS_SELECTOR, "#next_page")
            next_button.click()

            time.sleep(2)

            table_rows = driver.find_elements(By.CSS_SELECTOR, "table.table tbody tr")
        else:
            break
    
    with open(db_path_cp, "w", encoding="utf-8") as file:
        file.write(first_elem)

    csv_file_path = db_path+'/data.csv'
    with open(csv_file_path, mode='w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)

        writer.writerow(['boj_id', 'boj_problem', 'boj_tier', 'year', 'month', 'day'])
        
        for data in save_data:
            writer.writerow([
                data.id,
                data.problem,
                data.tier,
                data.date.year,
                data.date.month,
                data.date.day
            ])

finally:
    driver.quit()
