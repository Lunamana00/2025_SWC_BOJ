import csv
import json
import requests
import os
from datetime import datetime, timedelta

def map_tier(numeric_tier):
    if numeric_tier == 1:
        return "Bronze V"
    elif numeric_tier == 2:
        return "Bronze IV"
    elif numeric_tier == 3:
        return "Bronze III"
    elif numeric_tier == 4:
        return "Bronze II"
    elif numeric_tier == 5:
        return "Bronze I"
    elif numeric_tier == 6:
        return "Silver V"
    elif numeric_tier == 7:
        return "Silver IV"
    elif numeric_tier == 8:
        return "Silver III"
    elif numeric_tier == 9:
        return "Silver II"
    elif numeric_tier == 10:
        return "Silver I"
    elif numeric_tier == 11:
        return "Gold V"
    elif numeric_tier == 12:
        return "Gold IV"
    elif numeric_tier == 13:
        return "Gold III"
    elif numeric_tier == 14:
        return "Gold II"
    elif numeric_tier == 15:
        return "Gold I"
    elif numeric_tier == 16:
        return "Platinum V"
    elif numeric_tier == 17:
        return "Platinum IV"
    elif numeric_tier == 18:
        return "Platinum III"
    elif numeric_tier == 19:
        return "Platinum II"
    elif numeric_tier == 20:
        return "Platinum I"
    elif numeric_tier == 21:
        return "Diamond V"
    elif numeric_tier == 22:
        return "Diamond IV"
    elif numeric_tier == 23:
        return "Diamond III"
    elif numeric_tier == 24:
        return "Diamond II"
    elif numeric_tier == 25:
        return "Diamond I"
    elif numeric_tier == 26:
        return "Ruby V"
    elif numeric_tier == 27:
        return "Ruby IV"
    elif numeric_tier == 28:
        return "Ruby III"
    elif numeric_tier == 29:
        return "Ruby II"
    elif numeric_tier == 30:
        return "Ruby I"
    else:
        return "MASTER"

# 1. 기본 설정 및 파일 읽기
with open('./DB/notionAPIkey.txt', "r", encoding="utf-8") as file:
    NOTION_TOKEN = file.read().strip()

notion_headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

with open("./DB/db_mapping.json", "r", encoding="utf-8") as f:
    db_mapping = json.load(f)

csv_file_path = "./DB/data.csv"
update_id = {} 

# 2. CSV 읽어서 유저별 문제 데이터 저장
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
            day = '0' + day
        if len(month) == 1:
            month = '0' + month
        date = f"{year}-{month}-{day}"

        entry = {"date": date, "problem": problem, "score": score}
        update_id.setdefault(user_id, []).append(entry)

# 3. 각 유저별 JSON 업데이트 (로컬 데이터 갱신)
json_dir = "./DB/userdata/"
overall_db_id = db_mapping["db_id"]# 전체 리더보드 DB ID

print("업데이트할 유저:", update_id.keys())

for user_id, entries in update_id.items():
    user_file_path = os.path.join(json_dir, f"{user_id}.json")
    if os.path.exists(user_file_path):
        with open(user_file_path, "r", encoding="utf-8") as user_file:
            try:
                user_data = json.load(user_file)
            except json.JSONDecodeError:
                user_data = {
                    "start_tier": 0,
                    "curr_tier": 0,
                    "day": [],
                    "top10": [],
                    "longest_streak": 0,
                    "current_streak": 0
                }
    else:
        user_data = {
            "start_tier": 0,
            "curr_tier": 0,
            "day": [],
            "top10": [],
            "longest_streak": 0,
            "current_streak": 0
        }

    # 3-1. Solved.ac API 호출로 유저 티어 업데이트
    api_headers = {
        "Accept": "application/json",
        "x-solvedac-language": "kr"
    }
    response = requests.get(f'https://solved.ac/api/v3/user/show?handle={user_id}', headers=api_headers)
    if response.status_code == 200:
        print(f"✅ {user_id}의 티어 정보 가져오기 성공!")
        user_tier = response.json().get('tier', 0)
        print(f"{user_id}의 현재 티어: {user_tier}")
        user_data["curr_tier"] = user_tier
        if user_data["start_tier"] == 0:
            user_data["start_tier"] = user_tier
    else:
        print(f"❌ {user_id}의 티어 정보를 가져오지 못했습니다. 코드: {response.status_code}")
        continue

    # 3-2. CSV 기반 날짜별 문제 추가 & top10 업데이트 (중복되지 않도록)
    for entry in entries:
        date = entry["date"]
        problem_data = {"problem_id": entry["problem"], "difficulty": entry["score"]}
        found = False
        for day_entry in user_data["day"]:
            if day_entry.get("date") == date:
                # 이미 해당 날짜에 같은 문제가 없으면 추가
                if not any(p["problem_id"] == entry["problem"] for p in day_entry.get("problems", [])):
                    day_entry.setdefault("problems", []).append(problem_data)
                found = True
                break
        if not found:
            user_data["day"].append({"date": date, "problems": [problem_data]})
        
        exists_in_top10 = any(p["problem_id"] == entry["problem"] for p in user_data["top10"])
        if not exists_in_top10:
            try:
                new_score = int(entry["score"])
            except ValueError:
                new_score = 0
            if len(user_data["top10"]) < 10:
                user_data["top10"].append(problem_data)
            else:
                min_index = min(range(len(user_data["top10"])), key=lambda i: int(user_data["top10"][i]["difficulty"]))
                if new_score > int(user_data["top10"][min_index]["difficulty"]):
                    user_data["top10"][min_index] = problem_data

    # 3-3. 최장 & 현재 스트릭 계산
    dates = sorted(set(day_entry["date"] for day_entry in user_data["day"]))
    max_streak = 0
    current_streak = 0
    prev_date = None
    for date_str in dates:
        current_date = datetime.strptime(date_str, "%Y-%m-%d")
        if prev_date and current_date - prev_date == timedelta(days=1):
            current_streak += 1
        else:
            current_streak = 1
        max_streak = max(max_streak, current_streak)
        prev_date = current_date
    user_data["longest_streak"] = max_streak
    user_data["current_streak"] = current_streak

    with open(user_file_path, "w", encoding="utf-8") as file:
        json.dump(user_data, file, indent=4, ensure_ascii=False)
    print(f"✅ {user_id}.json 파일 저장 완료!")

    # 4-1. 전체 리더보드 업데이트
    total_days = len(user_data["day"])
    total_problems = sum(len(day_entry.get("problems", [])) for day_entry in user_data["day"])
    top10_sum = sum(int(item["difficulty"]) for item in user_data["top10"] if str(item["difficulty"]).isdigit())
    numeric_start_tier = user_data["start_tier"]
    numeric_curr_tier = user_data["curr_tier"]
    start_tier_str = map_tier(numeric_start_tier)
    curr_tier_str = map_tier(numeric_curr_tier)
    
    # 전체 리더보드 DB에서 해당 유저 페이지를 쿼리 (아이디 기준)
    query_url = f"https://api.notion.com/v1/databases/{overall_db_id}/query"
    query_payload = {
        "filter": {
            "property": "아이디",
            "rich_text": {
                "equals": user_id
            }
        }
    }
    query_resp = requests.post(query_url, headers=notion_headers, json=query_payload)
    if query_resp.status_code == 200:
        results = query_resp.json().get("results", [])
        page_payload = {
            "properties": {
                "참가 일 수": {
                    "number": total_days
                },
                "시작티어": {
                    "select": {"name": start_tier_str}
                },
                "현재티어": {
                    "select": {"name": curr_tier_str}
                },
                "문제수": {
                    "number": total_problems
                },
                "최고난도 문제 점수 합": {
                    "number": top10_sum
                },
                "최장 스트릭": {
                    "number": user_data["longest_streak"]
                },
                "현재 스트릭": {
                    "number": user_data["current_streak"]
                }
            }
        }
        if results:
            # 기존 페이지가 있으면 업데이트
            page_id = results[0]["id"]
            update_url = f"https://api.notion.com/v1/pages/{page_id}"
            up_resp = requests.patch(update_url, headers=notion_headers, json=page_payload)
            if up_resp.status_code == 200:
                print(f"[{user_id}] 전체 리더보드 페이지 업데이트 완료!")
            else:
                print(f"[{user_id}] 전체 리더보드 페이지 업데이트 실패: {up_resp.status_code}")
                print(up_resp.text)
        else:
            # 기존 페이지가 없으면 새로 생성
            new_page_data = {
                "parent": {"database_id": overall_db_id},
                "properties": {
                    "아이디": {
                        "title": [{"type": "text", "text": {"content": user_id}}]
                    },
                    **page_payload["properties"]
                }
            }
            create_url = "https://api.notion.com/v1/pages"
            cr_resp = requests.post(create_url, headers=notion_headers, json=new_page_data)
            if cr_resp.status_code == 200:
                print(f"[{user_id}] 전체 리더보드 페이지 생성 완료!")
            else:
                print(f"[{user_id}] 전체 리더보드 페이지 생성 실패: {cr_resp.status_code}")
                print(cr_resp.text)
    else:
        print(f"[{user_id}] 전체 리더보드 쿼리 실패: {query_resp.status_code}")


    # 4-2. 개인 문제 리더보드 업데이트 (CSV 기반 Upsert)
    personal_db_id = db_mapping.get(user_id)
    if not personal_db_id:
        print(f"{user_id}에 해당하는 개인 DB ID가 없습니다.")
        continue

    for day_entry in user_data["day"]:
        date_str = day_entry["date"]
        for prob in day_entry["problems"]:
            problem_id = prob["problem_id"]
            difficulty = prob["difficulty"]
            try:
                difficulty_num = int(difficulty)
            except ValueError:
                difficulty_num = 0

            # 복합 필터: 날짜와 문제(Title) 모두 일치하는지 확인
            filter_payload = {
                "filter": {
                    "and": [
                        {"property": "날짜", "date": {"equals": date_str}},
                        {"property": "문제", "title": {"equals": problem_id}}
                    ]
                }
            }
            query_url = f"https://api.notion.com/v1/databases/{personal_db_id}/query"
            query_resp = requests.post(query_url, headers=notion_headers, json=filter_payload)
            new_page_data = {
                "parent": {"database_id": personal_db_id},
                "properties": {
                    "날짜": {"date": {"start": date_str}},
                    "문제": {"title": [{"type": "text", "text": {"content": problem_id}}]},
                    "점수": {"number": difficulty_num}
                }
            }
            if query_resp.status_code == 200:
                results = query_resp.json().get("results", [])
                if results:
                    # 업데이트
                    page_id = results[0]["id"]
                    update_url = f"https://api.notion.com/v1/pages/{page_id}"
                    up_resp = requests.patch(update_url, headers=notion_headers, json=new_page_data)
                    if up_resp.status_code == 200:
                        print(f"[{user_id}] 개인 DB: {problem_id} 업데이트 완료!")
                    else:
                        print(f"[{user_id}] 개인 DB 업데이트 실패: {up_resp.status_code}")
                        print(up_resp.text)
                else:
                    # 생성
                    create_url = "https://api.notion.com/v1/pages"
                    cr_resp = requests.post(create_url, headers=notion_headers, json=new_page_data)
                    if cr_resp.status_code == 200:
                        print(f"[{user_id}] 개인 DB: {problem_id} 생성 완료!")
                    else:
                        print(f"[{user_id}] 개인 DB 생성 실패: {cr_resp.status_code}")
                        print(cr_resp.text)
            else:
                print(f"[{user_id}] 개인 DB 쿼리 실패: {query_resp.status_code}")
