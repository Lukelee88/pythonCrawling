import csv
import pandas as pd
from sqlalchemy import create_engine, text
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from sqlalchemy.exc import SQLAlchemyError
import os
import re
import time
from datetime import datetime, timedelta
from selenium.webdriver.common.by import By

disaster_map = {
    "침수": 1, "태풍": 2, "호우": 3, "낙뢰": 4, "강풍": 5,
    "풍랑": 6, "대설": 7, "한파": 8, "폭염": 9, "황사": 10,
    "지진": 11, "해일": 12, "지진해일": 13, "화산폭발": 14, "가뭄": 15,
    "홍수": 16, "조수": 17, "산사태": 18, "자연우주물체추락": 19, 
    "우주전파재난": 20, "조류대발생": 21, "적조": 22,
    "화재": 23, "산불": 24, "건축물붕괴": 25, "폭발": 26, 
    "교통사고": 27, "전기가스사고": 28, "철도사고": 29, 
    "유도선사고": 30, "해양선박사고": 31, "식용수": 32, 
    "원전사고": 33, "공동구재난": 34,
    "대규모수질오염": 35, "가축질병": 36, "댐붕괴": 37, 
    "정전 및 전력부족": 38, "감염병예방": 39, "해양오염사고": 40, 
    "화학물질사고": 41, "항공기사고": 42, "인공우주물체추락": 43, 
    "미세먼지": 44, "정보통신사고": 45, "gps전파혼신재난": 46, 
    "보건의료재난": 47, "사업장대규모인적사고": 48, 
    "공연장안전": 49, "도로터널사고": 50, "경기장안전": 51, 
    "원유수급위기": 52,
    "여름철물놀이": 53, "산행안전사고": 54, "응급처치": 55, 
    "해파리피해": 56, "심폐소생술": 57, "붉은불개미": 58, 
    "승강기안전사고": 59, "어린이놀이시설": 60, "식중독": 61, 
    "실종유괴예방": 62, "학교폭력예방": 63, "가정폭력예방": 64, 
    "석유제품사고": 65,
    "테러": 66, "비상사태": 67, 
    "민방공경보": 68, "비상대비물자준비": 69, "기타": 70, "전염병": 39, "정전": 38,
    "민방공": 68, "붕괴": 37, "수도": 70, "교통통제": 70, "환경오염사고": 35, "교통": 70,
    "통신": 45, "건조": 24, "에너지": 38
}

# 추가 매핑 생성
safety_map = {
    "안전안내": 10,
    "긴급재난": 20,
    "위급재난": 30
}

# Oracle DB 연결 정보
db_user = 'c##numberone'
db_password = ''
db_host = ''
db_port = ''
db_service_name = 'xe'

# Oracle DB 연결
db_url = 'oracle+oracledb://{}:{}@{}:{}/{}'.format(db_user, db_password, db_host, db_port, db_service_name)
engine = create_engine(db_url)

b_csv_path = 'output_test.csv'  # 참조할 CSV 파일
b_df = pd.read_csv(b_csv_path)

def update_broadcast_region(row):
    locations = row['broadcastArea'].split(', ')  # ','로 분리
    new_locations = []

    for loc in locations:
        tokens = loc.split()  # 띄어쓰기로 분리
        if len(tokens) == 1:  # 1개인 경우
            sido = tokens[0]
            matched_row = b_df[b_df['sido'] == sido]
            if not matched_row.empty:
                loc_code = str(matched_row['loc_code'].values[0])  # loc_code를 문자열로 변환
                new_locations.append(loc_code)
            else:
                print("loc:",loc)
                new_locations.append(loc)  # 일치하지 않으면 원래 값 유지
        elif len(tokens) == 2:  # 2개인 경우
            sido, sigungu = tokens
            if sido == "세종특별자치시":
                matched_row = b_df[b_df['sido'] == sido]
                if not matched_row.empty:
                    loc_code = str(matched_row['loc_code'].values[0])  # loc_code를 문자열로 변환
                    new_locations.append(loc_code)
                else:
                    print("loc:",loc)
                    new_locations.append(loc)  # 일치하지 않으면 원래 값 유지
            else:
                combined = f"{sido} {sigungu}"
                matched_row = b_df[b_df['sido'] + ' ' + b_df['sigungu'] == combined]
                if not matched_row.empty:
                    loc_code = str(matched_row['loc_code'].values[0])  # loc_code를 문자열로 변환
                    new_locations.append(loc_code)
                else:
                    print("loc:",loc)
                    new_locations.append(loc)  # 일치하지 않으면 원래 값 유지
        elif len(tokens) == 3:  # 3개인 경우
            sido, sigungu, eupmyeondong = tokens
            matched_row = b_df[
                (b_df['sido'] == sido) &
                (b_df['sigungu'] == sigungu) &
                (b_df['eupmyeondong'] == eupmyeondong)
            ]
            if not matched_row.empty:
                loc_code = str(matched_row['loc_code'].values[0])  # loc_code를 문자열로 변환
                new_locations.append(loc_code)
            else:
                matched_row = b_df[
                    (b_df['sido'] == sido) &
                    (b_df['sigungu'] == sigungu + " " + eupmyeondong)
                ]
                if not matched_row.empty:
                    loc_code = str(matched_row['loc_code'].values[0])  # loc_code를 문자열로 변환
                    new_locations.append(loc_code)
                else:
                    if sido == "세종특별자치시":
                        matched_row = b_df[
                            (b_df['sido'] == sido) &
                            (b_df['sigungu'] == eupmyeondong)
                        ]
                        if not matched_row.empty:
                            loc_code = str(matched_row['loc_code'].values[0])  # loc_code를 문자열로 변환
                            new_locations.append(loc_code)
                        else:
                            print("loc:",loc)
                            new_locations.append(loc)  # 일치하지 않으면 원래 값 유지
                    else:
                        print("loc:",loc)
                        new_locations.append(loc)  # 일치하지 않으면 원래 값 유지
        elif len(tokens) == 4:  # 4개인 경우
            sido = tokens[0]
            sigungu = " ".join(tokens[1:3])  # 2, 3번째 토큰을 띄어쓰기로 연결
            eupmyeondong = tokens[3]  # 4번째 토큰
            
            matched_row = b_df[
                (b_df['sido'] == sido) &
                (b_df['sigungu'] == sigungu) &
                (b_df['eupmyeondong'] == eupmyeondong)
            ]
            if not matched_row.empty:
                loc_code = str(matched_row['loc_code'].values[0])  # loc_code를 문자열로 변환
                new_locations.append(loc_code)
            else:
                print("loc:",loc)
                new_locations.append(loc)  # 일치하지 않으면 원래 값 유지
                
    # 새로운 송출 지역으로 업데이트
    return ', '.join(new_locations)


while True:
        try:

            # 데이터베이스 연결
            conn = engine.connect()
            trans = conn.begin() 
            result = conn.execute(text("SELECT MAX(message_seq) FROM disasterMsg"))
            max_message_seq = result.scalar()

            options = webdriver.ChromeOptions()
            options.add_argument('headless')
            options.add_argument("no-sandbox")
            options.add_argument('window-size=1920x1080')
            options.add_argument("disable-gpu")
            options.add_argument("lang=ko_KR")
            options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36')

            driver = webdriver.Chrome(options=options)

            driver.get('https://www.safekorea.go.kr/idsiSFK/neo/sfk/cs/sfc/dis/disasterMsgList.jsp?emgPage=Y&menuSeq=679')
            driver.implicitly_wait(3)

            wait = WebDriverWait(driver, 10)
            today_date = datetime.now().strftime('%Y-%m-%d')
            yesterday_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
            driver.execute_script("disasterSms_searchinfo.set('searchBgnDe', arguments[0])", yesterday_date)
            driver.execute_script("disasterSms_searchinfo.set('searchEndDe', arguments[0])", today_date)
            driver.execute_script("getDisasterSmsList_submission.exec()")
            time.sleep(0.3)

            totalpages = int(driver.find_element("id", "tbpagetotal").text.replace("/", ""))
            current_page = 1
            pattern = r"(\d+)\s(\w+)\s(\w+)\n(\d{4}/\d{2}/\d{2}\s\d{2}:\d{2}:\d{2}\s\[[\w\s]+\])\n(\d{4}-\d{2}-\d{2})"

            # 새 메시지를 저장할 데이터프레임 (중복 없이)
            new_messages = []

            while current_page <= totalpages:
                wait.until(EC.visibility_of_element_located(("id", "iptpageinput")))
                page_input = driver.find_element("id", "iptpageinput")
                page_input.clear()
                page_input.send_keys(str(current_page))
                driver.find_element("id", "apagego").click()
                time.sleep(0.3)
                
                
                rows = driver.find_elements("id", "disasterSms_tr")

                for row in rows:
                    cells = row.text

                    for match in re.finditer(pattern, cells):
                        no, disasterDiv, emergencyLevel, message, regDate = match.groups()

                        if int(no) > max_message_seq :
                            message_parts = message.split(' ', 2)
                            if len(message_parts) >= 3:
                                sender = message_parts[2].strip('[]')
                                remaining_message = ' '.join(message_parts[:2])
                                regDate =remaining_message
                                message = ""  # message는 빈 문자열로 남김
                            else:
                                sender = ''
                                message = message

                            new_message = {
                                "no": no,
                                "disasterDiv": disasterDiv,
                                "emergencyLevel": emergencyLevel,
                                "message": message,
                                "regDate": regDate,
                                "sender": sender,
                                "broadcastArea": ""
                            }
                            new_messages.append(new_message)

                current_page += 1 

            # URL 접근 및 크롤링
            for new_message in new_messages:
                no = new_message["no"]
                url = f"https://www.safekorea.go.kr/idsiSFK/neo/sfk/cs/sfc/dis/disasterMsgView.jsp?menuSeq=679&md101_sn={no}"
                driver.get(url)
                time.sleep(0.5)  # 페이지 로딩 대기

                try:
                    detail_context = driver.find_element(By.ID, "msg_cn")
                    bbs_detail_element = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.ID, "bbsDetail"))
                    )
                    second_child = bbs_detail_element.find_elements(By.XPATH, './*')[0]
                    extracted_data = second_child.text.split("송출지역 :")[1].strip()

                    # 개행 문자가 포함된 경우 처리
                    content = detail_context.text.replace('\n', ' ').replace('\r', '')

                    # DataFrame에 추가
                    start_index = content.rfind('[')
                    if start_index != -1:
                        cleaned_text = content[:start_index].strip()  # [] 이전까지의 문자열을 잘라내고 공백 제거
                    else:
                        cleaned_text = content  # []가 없으면 원본 문자열 그대로
                        
                    new_message['message'] = cleaned_text  # '내용'을 message에 추가
                    new_message['broadcastArea'] = extracted_data  # '송출 지역'을 broadcastArea에 추가
                    new_message['disasterDiv']= disaster_map.get(new_message['disasterDiv'])
                    new_message['emergencyLevel']= safety_map.get(new_message['emergencyLevel'])
                    new_message['broadcastArea'] = update_broadcast_region(new_message)
                    no = int(new_message['no'])  # no 컬럼값
                    locations = new_message['broadcastArea'].split(', ')  # 송출 지역을 ','로 분리
                    for loc in locations:
                            # 송출 지역 문자열을 숫자로 변환 (여기서는 간단한 예시로 변환)
                        loc_code = int(loc)  # 변환 로직은 필요에 따라 수정
                            # INSERT 문 작성 (여기서 'your_table_name'을 실제 테이블 이름으로 변경)
                        insert_query = text(f"INSERT INTO message_area (message_seq, area_code) VALUES (:no, :loc_code)")
                            # 데이터베이스에 INSERT 실행
                        conn.execute(insert_query, {'no': no, 'loc_code': loc_code})
                    query = text("INSERT INTO disastermsg (message_seq, disaster_type, emergency_level, message_context, msg_reg_dt, broadcast_organization) VALUES (:no, :disasterDiv, :emergencyLevel, :context, TO_DATE(:regDate, 'YYYY-MM-DD HH24:MI:SS'), :sender)")
                    conn.execute(query, {
                        'no': no,
                        'disasterDiv': new_message['disasterDiv'],
                        'emergencyLevel': new_message['emergencyLevel'],
                        'regDate': new_message['regDate'],
                        'sender': new_message['sender'],
                        'context': new_message['message']
                    })
                    
                    print(new_message)
       
                except Exception as e:
                    print(f"Error fetching details for {no}: {e}")
                    new_message['message'] = None  # 오류 발생 시 내용 열에 None 저장
                    new_message['broadcastArea'] = None  # 오류 발생 시 송출 지역 열에 None 저장
            trans.commit()
        except SQLAlchemyError as e:
        # 오류 발생 시 롤백
            trans.rollback()
            print(f"SQLAlchemy Error occurred: {e}")
        
        except Exception as e:
            print(f"An error occurred: {e}")


                
        finally:
            # 연결 종료
            if 'conn' in locals():
                conn.close()
            if 'driver' in locals():
                driver.quit()  # 드라이버 종료
        print("5초 후에 다시 시도합니다...")
        time.sleep(5)    
