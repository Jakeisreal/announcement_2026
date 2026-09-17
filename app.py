import os
import datetime
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional
import pandas as pd
import uvicorn

import db
import ninehire_sync

# Initialize DB
db.init_db(force_reseed=False)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

app = FastAPI(title="Hwashin Recruit Final Confirmation Portal")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

# Deadline: 2026-09-18 11:59:00 KST
DEADLINE = datetime.datetime(2026, 9, 18, 11, 59, 0)

def is_deadline_passed():
    # In live system, compares current local time with DEADLINE
    return datetime.datetime.now() > DEADLINE

class LoginRequest(BaseModel):
    name: str
    phone: str

class SubmitRequest(BaseModel):
    status: str
    response_english_name: Optional[str] = ""
    response_uniform_size: Optional[str] = ""
    response_dormitory: Optional[str] = ""
    decline_reason: Optional[str] = ""
    decline_detail: Optional[str] = ""

class ToggleDormRequest(BaseModel):
    eligible: bool

@app.get("/", response_class=HTMLResponse)
async def index_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/login")
async def login_api(req: LoginRequest):
    candidates = db.get_all_candidates()
    input_name = req.name.strip()
    input_phone_digits = "".join(filter(str.isdigit, req.phone))

    for c in candidates:
        if c["name"] == input_name:
            c_phone_digits = "".join(filter(str.isdigit, c["phone"]))
            if input_phone_digits in c_phone_digits or c_phone_digits.endswith(input_phone_digits):
                return {"success": True, "token": c["token"]}

    return {"success": False, "message": "성명과 연락처가 일치하는 대상자를 찾을 수 없습니다."}

@app.get("/confirm/{token}", response_class=HTMLResponse)
async def confirm_page(request: Request, token: str):
    candidate = db.get_candidate_for_candidate_view(token)
    if not candidate:
        raise HTTPException(status_code=404, detail="유효하지 않은 링크입니다.")
    
    if is_deadline_passed():
        return templates.TemplateResponse("closed.html", {"request": request, "candidate": candidate})

    return templates.TemplateResponse("candidate_form.html", {
        "request": request,
        "candidate": candidate
    })

@app.post("/api/submit/{token}")
async def submit_api(request: Request, token: str, req: SubmitRequest):
    candidate = db.get_candidate_by_token(token)
    if not candidate:
        return {"success": False, "message": "유효하지 않은 요청입니다."}

    if is_deadline_passed():
        return {"success": False, "message": "응답 제출 기한(9월 18일 11:59)이 마감되었습니다."}

    client_ip = request.client.host if request.client else ""
    submit_data = req.model_dump() if hasattr(req, "model_dump") else req.dict()
    db.submit_candidate_response(token, submit_data, ip=client_ip)

    return {"success": True, "message": "정상적으로 제출되었습니다."}

@app.get("/complete/{token}", response_class=HTMLResponse)
async def complete_page(request: Request, token: str):
    candidate = db.get_candidate_for_candidate_view(token)
    if not candidate:
        raise HTTPException(status_code=404, detail="유효하지 않은 접근입니다.")

    return templates.TemplateResponse("complete.html", {
        "request": request,
        "candidate": candidate
    })

@app.get("/closed/{token}", response_class=HTMLResponse)
async def closed_page(request: Request, token: str):
    candidate = db.get_candidate_for_candidate_view(token)
    return templates.TemplateResponse("closed.html", {
        "request": request,
        "candidate": candidate
    })

# --- Admin APIs ---

@app.get("/admin", response_class=HTMLResponse)
async def admin_page(request: Request):
    return templates.TemplateResponse("admin_dashboard.html", {"request": request})

@app.get("/api/admin/candidates")
async def get_admin_candidates():
    candidates = db.get_all_candidates()
    total = len(candidates)
    responded = sum(1 for c in candidates if c["status"] in ["accepted", "declined"])
    accepted = sum(1 for c in candidates if c["status"] == "accepted")
    declined = sum(1 for c in candidates if c["status"] == "declined")
    pending = total - responded

    summary = {
        "total": total,
        "responded": responded,
        "pending": pending,
        "accepted": accepted,
        "declined": declined
    }

    return {"summary": summary, "candidates": candidates}

@app.post("/api/admin/toggle_dormitory/{candidate_id}")
async def toggle_dormitory(candidate_id: int, req: ToggleDormRequest):
    db.toggle_dormitory_eligibility(candidate_id, req.eligible)
    return {"success": True}

@app.post("/api/admin/reset")
async def reset_admin_data():
    db.reset_all_responses()
    return {"success": True, "message": "모든 응답 데이터가 초기화되었습니다."}

@app.post("/api/admin/sync_ninehire")
async def sync_ninehire_api():
    res = ninehire_sync.sync_candidate_tags_to_ninehire()
    return res

@app.get("/api/admin/export_excel")
async def export_excel():
    candidates = db.get_all_candidates()
    export_rows = []
    
    for c in candidates:
        status_label = "미응답"
        if c["status"] == "accepted":
            status_label = "입사 희망 (수락)"
        elif c["status"] == "declined":
            status_label = "입사 포기"

        export_rows.append({
            "No": c["id"],
            "성명": c["name"],
            "영문명(기존)": c["english_name"],
            "영문명(최종제출)": c["response_english_name"] or c["english_name"],
            "본부": c["division"],
            "부서": c["department"],
            "생년월일": c["birthdate"],
            "연락처": c["phone"],
            "주소": c["address"],
            "기존근무복": c["uniform_size"],
            "최종근무복": c["response_uniform_size"] or c["uniform_size"],
            "기숙사신청대상여부": "대상" if c["dormitory_eligible"] else "비대상",
            "기숙사신청결과": c["response_dormitory"] or (c["default_dormitory"] if c["dormitory_eligible"] else ""),
            "최종입사여부": status_label,
            "포기사유": c["decline_reason"],
            "포기상세사유": c["decline_detail"],
            "응답제출일시": c["responded_at"],
            "나인하이어동기화": "완료" if c["ninehire_synced"] else "미완료"
        })

    df = pd.DataFrame(export_rows)
    
    now_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"2026년_공채_입사자_정보_최종확인결과_{now_str}.xlsx"
    filepath = os.path.join(BASE_DIR, filename)
    
    # Save to Excel
    with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name="최종입사확인결과", index=False)
        
    return FileResponse(filepath, filename=filename, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
