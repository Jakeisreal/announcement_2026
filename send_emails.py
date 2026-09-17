import smtplib
import os
import sys
import io
import getpass
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import db

NOTION_URL = "https://dull-chip-592.notion.site/3db81225d75380f0bce9c116ca22486f?source=copy_link"
BASE_URL = "https://jakeisreal.github.io/announcement_2026/"

def get_email_content(name="홍길동", token="dd394fc093eaa147"):
    link = f"{BASE_URL}?t={token}"
    subject = f"[화신] 2026년 정규직 전환 채용 최종 면접 결과 및 입사여부 확인 안내"
    
    body_text = f"""안녕하세요, 화신그룹 채용담당자입니다.

우선 그 동안 화신에서의 인턴 근무, 그리고 정규직 전환을 위한 면접 참석에 성실히 임해주신 부분에 대해 담당자로서 깊은 감사의 말씀을 드립니다.

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

def preview_test_email():
    subj, body = get_email_content("홍길동", "dd394fc093eaa147")
    print("\n================ [홍길동 테스트 이메일 미리보기] ================")
    print(f"제목: {subj}")
    print("----------------------------------------------------------------")
    print(body)
    print("================================================================\n")

def send_email_message(smtp_conn, sender_email, to_email, subject, body_text):
    msg = MIMEMultipart()
    msg['From'] = f"화신 채용담당자 <{sender_email}>"
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body_text, 'plain', 'utf-8'))
    smtp_conn.send_message(msg)

def get_smtp_connection():
    print("\n--- [발송용 이메일(SMTP) 설정 선택] ---")
    print("1. 네이버 메일 (smtp.naver.com:465)")
    print("2. 구글 Gmail (smtp.gmail.com:465 - 앱비밀번호 필요)")
    print("3. 다음/카카오 (smtp.daum.net:465)")
    print("4. 사내 SMTP / 직접 입력")
    
    choice = input("선택 번호 (기본 1): ").strip() or "1"
    
    if choice == "1":
        smtp_host = "smtp.naver.com"
        smtp_port = 465
    elif choice == "2":
        smtp_host = "smtp.gmail.com"
        smtp_port = 465
    elif choice == "3":
        smtp_host = "smtp.daum.net"
        smtp_port = 465
    else:
        smtp_host = input("SMTP 서버 주소: ").strip()
        smtp_port = int(input("SMTP 포트 번호 (예: 465 또는 587): ").strip())

    sender_email = input("발신자 이메일 주소: ").strip()
    sender_pw = getpass.getpass("발신자 비밀번호 (또는 앱 비밀번호): ").strip()

    print("\nSMTP 서버에 연결 중...")
    if smtp_port == 465:
        server = smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=10)
    else:
        server = smtplib.SMTP(smtp_host, smtp_port, timeout=10)
        server.starttls()
        
    server.login(sender_email, sender_pw)
    print("✅ SMTP 로그인 성공!\n")
    return server, sender_email

def main():
    print("=" * 65)
    print("    2026년 화신그룹 공채 최종 합격자 이메일 발송 프로그램")
    print("=" * 65)
    print("1. [테스트 발송] 홍길동 (010-1234-5678) 1건 테스트 발송")
    print("2. [본 발송] 실제 11명 합격자 전원 일괄 발송")
    print("3. [미리보기] 메일 본문 내용 미리보기")
    print("=" * 65)
    
    mode = input("실행할 작업 번호를 입력하세요 (1, 2, 3): ").strip()
    
    if mode == "3":
        preview_test_email()
        return

    try:
        server, sender_email = get_smtp_connection()
    except Exception as e:
        print(f"❌ SMTP 연결/로그인 실패: {e}")
        print("Tip: 네이버/구글의 경우 [환경설정 > POP3/IMAP/SMTP 사용 설정]이 켜져 있어야 합니다.")
        return

    if mode == "1":
        test_email = input("테스트 메일을 수신할 이메일 주소를 입력하세요: ").strip()
        if not test_email:
            print("이메일 주소가 입력되지 않았습니다.")
            return

        name = "홍길동"
        phone = "010-1234-5678"
        subj, body = get_email_content(name=name, token="dd394fc093eaa147")
        
        print(f"\n[{name} ({phone}) -> {test_email}] 테스트 메일 발송 중...")
        try:
            send_email_message(server, sender_email, test_email, subj, body)
            print(f"🎉 테스트 이메일이 성공적으로 발송되었습니다! ({test_email} 확인 요망)")
        except Exception as e:
            print(f"❌ 발송 실패: {e}")

    elif mode == "2":
        candidates = db.get_all_candidates()
        print(f"\n총 {len(candidates)}명의 합격자에게 메일을 순차 발송합니다.")
        confirm = input("정말로 발송하시겠습니까? (Y/N): ").strip().upper()
        if confirm != "Y":
            print("발송이 취소되었습니다.")
            return

        success_count = 0
        for c in candidates:
            subj, body = get_email_content(name=c["name"], token=c["token"])
            try:
                send_email_message(server, sender_email, c["email"], subj, body)
                print(f"✅ [{c['id']}/11] 발송 완료: {c['name']} ({c['email']})")
                success_count += 1
            except Exception as e:
                print(f"❌ [{c['id']}/11] 발송 실패: {c['name']} ({c['email']}) - {e}")
        
        print(f"\n🎉 총 {success_count}/{len(candidates)}명에게 발송이 완료되었습니다!")

    try:
        server.quit()
    except:
        pass

if __name__ == "__main__":
    main()
