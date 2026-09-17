import smtplib
import os
import sys
import io
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import db

NOTION_URL = "https://dull-chip-592.notion.site/3db81225d75380f0bce9c116ca22486f?source=copy_link"
BASE_URL = "https://jakeisreal.github.io/announcement_2026/"

def get_email_content(candidate):
    name = candidate["name"]
    token = candidate["token"]
    link = f"{BASE_URL}?t={token}"

    subject = f"[화신] 2026년 정규직 전환 채용 최종 면접 결과 및 입사여부 확인 안내"
    
    body_text = f"""안녕하세요, 화신그룹 채용담당자입니다.

우선 그 동안 화신에서의 인턴 근무, 그리고 정규직 전환을 위한 면접 참석에 성실히 임해주신 부분에 대해 담당자로서 깊은 감사의 말씀을 전해드립니다.

금번 채용 면접 결과, {name} 님께서 최종 합격하셨음을 기쁜 마음으로 알려드립니다.

정규직 신입사원 입사 준비(사원증 및 명함 제작, 근무복 지급 등)를 위해 아래 전용 확인 페이지를 통해 9월 18일(금) 오전 11:59까지 최종 입사 여부 회신을 부탁드립니다.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
■ 대상자: {name} 님
■ 회신 기한: 2026년 9월 18일 (금) 오전 11:59 까지
■ 최종 입사확인 전용 페이지: {link}
■ 정규직 전환 상세 안내 가이드(Notion): {NOTION_URL}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

※ 위 전용 페이지는 {name} 님만을 위한 1:1 확인 링크이오니 타인에게 공유되지 않도록 유의해 주시기 바랍니다.

감사합니다.
화신 채용담당자 드림
"""
    return subject, body_text

def preview_all_emails():
    candidates = db.get_all_candidates()
    print(f"=== 총 {len(candidates)}명 합격자 이메일 발송 내용 미리보기 ===")
    for c in candidates:
        subj, body = get_email_content(c)
        print(f"\n[받는사람: {c['name']} <{c['email']}>]")
        print(f"제목: {subj}")
        print("-" * 50)
        print(body)
        print("=" * 60)

def send_via_smtp(smtp_server, smtp_port, sender_email, sender_password):
    """
    사내 SMTP 또는 Gmail/Naver SMTP를 통한 일괄 발송 함수
    """
    candidates = db.get_all_candidates()
    
    server = smtplib.SMTP_SSL(smtp_server, smtp_port)
    server.login(sender_email, sender_password)
    
    for c in candidates:
        subj, body = get_email_content(c)
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = c['email']
        msg['Subject'] = subj
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        server.send_message(msg)
        print(f"✅ 발송 완료: {c['name']} ({c['email']})")
        
    server.quit()
    print("\n🎉 11명 전원 이메일 발송이 완료되었습니다.")

if __name__ == "__main__":
    preview_all_emails()
