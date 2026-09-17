import sqlite3
import os
import uuid
import secrets
import pandas as pd
import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "confirmation.db")

# Ninehire Applicant ID Map (Matched from Ninehire API)
NINEHIRE_MAP = {
    "김병희": {"recruitmentId": "d71b1860-a506-11f1-9f66-5ff0ab8e46c7", "applicantId": "cb4860d0-a901-11f1-a1b4-7b8c2cfbbf67", "email": "rlaqudgml44@naver.com", "phone": "010-2304-8259"},
    "권석율": {"recruitmentId": "d71b1860-a506-11f1-9f66-5ff0ab8e46c7", "applicantId": "9bfa5f60-a901-11f1-bfa6-b184b9015c61", "email": "ksy23160@naver.com", "phone": "010-2785-8810"},
    "김윤관": {"recruitmentId": "fe5cd6c0-a506-11f1-9f66-5ff0ab8e46c7", "applicantId": "858f9640-a900-11f1-aae5-ebc78fa76fe5", "email": "dbsrhks1173@naver.com", "phone": "010-7457-1173"},
    "임성수": {"recruitmentId": "b21f0440-a506-11f1-9f66-5ff0ab8e46c7", "applicantId": "a0a94251-a8ff-11f1-8e1f-036115bda1ac", "email": "seongsuim498@gmail.com", "phone": "010-9154-8619"},
    "김정동": {"recruitmentId": "2f169800-a507-11f1-9f66-5ff0ab8e46c7", "applicantId": "98144701-a900-11f1-933e-e17929d04fc4", "email": "wsx7707@naver.com", "phone": "010-6221-7293"},
    "박기혁": {"recruitmentId": "2f169800-a507-11f1-9f66-5ff0ab8e46c7", "applicantId": "f7ab2c10-a8ff-11f1-be17-f5dafa216c52", "email": "qkrrlgur23@gmail.com", "phone": "010-8647-2915"},
    "조무승": {"recruitmentId": "2f169800-a507-11f1-9f66-5ff0ab8e46c7", "applicantId": "bb269200-a8ff-11f1-893f-5b65ff7ca71b", "email": "jhk4640@naver.com", "phone": "010-5069-3756"},
    "전세민": {"recruitmentId": "2f169800-a507-11f1-9f66-5ff0ab8e46c7", "applicantId": "c4d7ec50-a8ff-11f1-9258-79bf081e478c", "email": "jeonsm2534@gmail.com", "phone": "010-8914-8516"},
    "김수철": {"recruitmentId": "41cd8c60-a507-11f1-9f66-5ff0ab8e46c7", "applicantId": "2cf331b0-a8ff-11f1-a4fa-33cf62bf5e02", "email": "harvey30@naver.com", "phone": "010-4538-8281"},
    "강동진": {"recruitmentId": "44759120-8b0c-11f1-a759-f7bc99114654", "applicantId": "73ba93f0-8be2-11f1-bfa6-b184b9015c61", "email": "jinny8422@gmail.com", "phone": "010-6583-8422"},
    "강선우": {"recruitmentId": "44759120-8b0c-11f1-a759-f7bc99114654", "applicantId": "7df41f20-8be2-11f1-be17-f5dafa216c52", "email": "queen030720@naver.com", "phone": "010-3392-2125"},
}

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db(force_reseed=False):
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS candidates (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        english_name TEXT,
        phone TEXT NOT NULL,
        email TEXT,
        birthdate TEXT,
        address TEXT,
        division TEXT,
        department TEXT,
        uniform_size TEXT,
        dormitory_eligible INTEGER DEFAULT 0,
        default_dormitory TEXT,
        token TEXT UNIQUE NOT NULL,
        status TEXT DEFAULT 'pending',
        response_english_name TEXT,
        response_uniform_size TEXT,
        response_dormitory TEXT,
        decline_reason TEXT,
        decline_detail TEXT,
        responded_at TEXT,
        ip_address TEXT,
        ninehire_applicant_id TEXT,
        ninehire_recruitment_id TEXT,
        ninehire_synced INTEGER DEFAULT 0
    )
    """)
    conn.commit()

    cursor.execute("SELECT COUNT(*) FROM candidates")
    count = cursor.fetchone()[0]

    if count == 0 or force_reseed:
        if force_reseed:
            cursor.execute("DELETE FROM candidates")
            conn.commit()
            
        excel_info = os.path.join(os.path.dirname(os.path.abspath(__file__)), "2026년 공채 입사자 정보.xlsx")
        excel_card = os.path.join(os.path.dirname(os.path.abspath(__file__)), "2026년 공채 입사자 정보_사원증,명함 제작 등.xlsx")
        
        df_info = pd.read_excel(excel_info)
        df_card = pd.read_excel(excel_card) if os.path.exists(excel_card) else pd.DataFrame()

        for idx, row in df_info.iterrows():
            cid = int(row['No'])
            name = str(row['성명']).strip()
            
            # English name from card excel
            eng_name = ""
            if not df_card.empty and '성명' in df_card.columns and '영문이름' in df_card.columns:
                match = df_card[df_card['성명'] == name]
                if not match.empty and pd.notna(match['영문이름'].values[0]):
                    eng_name = str(match['영문이름'].values[0]).strip()
            
            phone = str(row['연락처']).strip() if pd.notna(row['연락처']) else ""
            birthdate = str(row['생년월일']).split(" ")[0] if pd.notna(row['생년월일']) else ""
            address = str(row['주소']).strip() if pd.notna(row['주소']) else ""
            division = str(row['본부']).strip() if pd.notna(row['본부']) else ""
            dept = str(row['부서']).strip() if pd.notna(row['부서']) else ""
            uniform = str(row['근무복']).strip() if pd.notna(row['근무복']) else ""
            dorm = str(row['기숙사']).strip() if pd.notna(row['기숙사']) else ""
            
            # Eligible if dorm is present in initial excel (박기혁, 전세민, 김수철, 강동진)
            dorm_eligible = 1 if dorm in ['영천', '예산'] else 0
            
            # Match Ninehire
            nh = NINEHIRE_MAP.get(name, {})
            nh_applicant_id = nh.get("applicantId", "")
            nh_recruitment_id = nh.get("recruitmentId", "")
            email = nh.get("email", "")
            
            # Generate deterministic or random secure token
            token = secrets.token_hex(8)

            cursor.execute("""
            INSERT INTO candidates (
                id, name, english_name, phone, email, birthdate, address,
                division, department, uniform_size, dormitory_eligible,
                default_dormitory, token, status, ninehire_applicant_id,
                ninehire_recruitment_id, ninehire_synced
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending', ?, ?, 0)
            """, (
                cid, name, eng_name, phone, email, birthdate, address,
                division, dept, uniform, dorm_eligible, dorm, token,
                nh_applicant_id, nh_recruitment_id
            ))
            
        conn.commit()
        print(f"Database seeded with {len(df_info)} candidates.")
        
    conn.close()

def get_all_candidates():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM candidates ORDER BY id ASC")
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

def get_candidate_by_token(token: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM candidates WHERE token = ?", (token,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None

def get_candidate_for_candidate_view(token: str):
    """
    CRITICAL REQUIREMENT:
    Return candidate data for applicant view WITHOUT division and department (hidden completely).
    """
    c = get_candidate_by_token(token)
    if not c:
        return None
    
    # Sanitize and strip sensitive information
    return {
        "id": c["id"],
        "name": c["name"],
        "english_name": c["english_name"] or "",
        "phone": c["phone"],
        "email": c["email"],
        "birthdate": c["birthdate"],
        "address": c["address"],
        "uniform_size": c["uniform_size"] or "L(100)",
        "dormitory_eligible": bool(c["dormitory_eligible"]),
        "default_dormitory": c["default_dormitory"] or "",
        "status": c["status"],
        "token": c["token"],
        "response_english_name": c["response_english_name"],
        "response_uniform_size": c["response_uniform_size"],
        "response_dormitory": c["response_dormitory"],
        "decline_reason": c["decline_reason"],
        "decline_detail": c["decline_detail"],
        "responded_at": c["responded_at"]
        # division & department are intentionally OMITTED!
    }

def toggle_dormitory_eligibility(candidate_id: int, eligible: bool):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE candidates SET dormitory_eligible = ? WHERE id = ?", (1 if eligible else 0, candidate_id))
    conn.commit()
    conn.close()
    return True

def submit_candidate_response(token: str, data: dict, ip: str = ""):
    conn = get_connection()
    cursor = conn.cursor()
    
    responded_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    status = data.get("status") # 'accepted' or 'declined'
    
    cursor.execute("""
    UPDATE candidates SET
        status = ?,
        response_english_name = ?,
        response_uniform_size = ?,
        response_dormitory = ?,
        decline_reason = ?,
        decline_detail = ?,
        responded_at = ?,
        ip_address = ?,
        ninehire_synced = 0
    WHERE token = ?
    """, (
        status,
        data.get("response_english_name", ""),
        data.get("response_uniform_size", ""),
        data.get("response_dormitory", ""),
        data.get("decline_reason", ""),
        data.get("decline_detail", ""),
        responded_at,
        ip,
        token
    ))
    conn.commit()
    conn.close()
    return True

def mark_ninehire_synced(candidate_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE candidates SET ninehire_synced = 1 WHERE id = ?", (candidate_id,))
    conn.commit()
    conn.close()
