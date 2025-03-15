import csv
import json
import requests

with open('./DB/notionAPIkey.txt', "r", encoding="utf-8") as file:
    NOTION_TOKEN =  file.read()

print(NOTION_TOKEN)

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

with open("./DB/db_mapping.json", "r", encoding="utf-8") as f:
    db_mapping = json.load(f)

# CSV 파일 경로
csv_file_path = "./DB/data.csv"

# CSV 읽어서 Notion DB에 기록
with open(csv_file_path, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        user_id = row["boj_id"]
        problem = row["boj_problem"]
        score = row["boj_tier"]
        year = row["year"]
        month = row["month"]
        day = row["day"]
        
        if len(day) == 1:
            day = '0'+day
        
        if len(month) == 1:
            month = '0'+month

        date = year + '-' + month + '-' + day
        
        database_id = db_mapping[user_id]

        # Notion 페이지 생성 API
        create_url = "https://api.notion.com/v1/pages"
        new_page_data = {
            "parent": {
                "database_id": database_id
            },
            "properties": {
                "문제": {
                    "title": [
                        {
                            "type": "text",
                            "text": {
                                "content": problem
                            }
                        }
                    ]
                },
                "점수": {
                    "number": int(score) if score.isdigit() else 0
                },
                "날짜": {
                    "date": {
                        "start": date 
                    }
                }
            }
        }

        # POST 요청으로 페이지 생성
        response = requests.post(create_url, headers=headers, json=new_page_data)
        
        if response.status_code == 200:
            print(f"[{user_id}] {problem} 기록 완료!")
        else:
            print(f"오류 발생: {response.status_code}")
            print(response.text)