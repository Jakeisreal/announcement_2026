import sys
import io
import db

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

db.init_db(force_reseed=True)
candidates = db.get_all_candidates()

print(f"=== 2026년 화신그룹 공채 최종 합격자 11명 초기화 완료 ===")
print("-" * 80)
for c in candidates:
    dorm_str = f"대상 ({c['default_dormitory']})" if c['dormitory_eligible'] else "비대상"
    print(f"No.{c['id']:2d} | {c['name']:<4} | {c['division']:<10} | {c['department']:<10} | 기숙사: {dorm_str:<12} | URL: http://localhost:8000/confirm/{c['token']}")
print("-" * 80)
print("관리자 대시보드: http://localhost:8000/admin")
