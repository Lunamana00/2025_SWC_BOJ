from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time

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

    cp = content
    print(len(cp))
    print(cp)

chrome_options = Options()
#chrome_options.add_argument("--headless")  # 브라우저 창을 띄우지 않음

# 드라이버 서비스 생성 및 브라우저 실행
service = Service(chrome_driver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)



try:
    
    # 로그인인
    boj_login = "https://www.acmicpc.net/login?next=%2F"
    driver.get(boj_login)

    time.sleep(3)
    
    id_input = driver.find_element(By.CSS_SELECTOR, "#login_form > div:nth-child(2) > input")
    id_input.send_keys(id)

    pw_input = driver.find_element(By.CSS_SELECTOR, "#login_form > div:nth-child(3) > input")
    pw_input.send_keys(pw)

    login_button = driver.find_element(By.CSS_SELECTOR, "#submit_button")
    login_button.click()

    time.sleep(3)
    
    driver.get("https://www.acmicpc.net/status?group_id=23106")

    time.sleep(2)

    catch_flag = 1
    first_elem = 0

    table_rows = driver.find_elements(By.CSS_SELECTOR, "table.table tbody tr")

    class boj_data:
        def __init__(self,num,id,problem,tier):
            self.num = num
            self.id = id
            self.problem = problem
            self.tier  = tier

    # 각 행의 데이터를 추출
    save_data = list()

    for row in table_rows:
        if first_elem == cp:
            break
        if row.find_element(By.CLASS_NAME, 'result').text=='맞았습니다!!':
            boj_num = row.find_elements(By.TAG_NAME, 'td')[0].text
            boj_id = row.find_elements(By.TAG_NAME, 'td')[1].text
            boj_problem = row.find_elements(By.TAG_NAME, 'td')[2].text[1:]
            boj_tier_elem = row.find_element(By.CSS_SELECTOR, "td:nth-child(3) > img")
            boj_tier = boj_tier_elem.get_attribute("src").split("/")[-1].replace(".svg", "")
            save_data.append(boj_data(boj_num, boj_id,boj_problem, boj_tier))
    
    print(len(save_data))
        
finally:
    driver.quit()

