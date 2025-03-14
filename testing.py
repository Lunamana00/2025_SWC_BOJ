from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time

# Chrome 드라이버 경로 설정 (chromedriver가 PATH에 있다면 생략 가능)
chrome_driver_path = './chromedriver_win64/chromedriver.exe'  
# 혹은 chromedriver의 절대경로

# Chrome 옵션 설정 (헤드리스 모드 사용 예)
chrome_options = Options()
chrome_options.add_argument("--headless")  # 브라우저 창을 띄우지 않음

# 드라이버 서비스 생성 및 브라우저 실행
service = Service(chrome_driver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)

try:
    # 목표 URL로 이동
    url = "https://www.acmicpc.net/status?group_id=23106"
    driver.get(url)

    # 페이지가 완전히 로드될 때까지 잠시 대기
    time.sleep(3)
    print(11)
    """
    # 채점 현황 테이블 찾기 (페이지 구조에 따라 selector 수정 필요)
    # 일반적으로 테이블은 <table> 태그 내에 있으며, tbody > tr 형태로 각 행이 있음
    table_rows = driver.find_elements(By.CSS_SELECTOR, "table.table tbody tr")

    # 각 행의 데이터를 추출
    for row in table_rows:
        cells = row.find_elements(By.TAG_NAME, "td")
        # 각 셀의 텍스트를 리스트로 저장
        data = [cell.text for cell in cells]
        print(data)
    """
finally:
    driver.quit()
