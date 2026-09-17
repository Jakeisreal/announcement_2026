import requests
import json
import logging
from db import get_connection, mark_ninehire_synced, get_all_candidates

TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjb21wYW55SWQiOiI5NWM5ZWMyMC1mYTg4LTExZjAtYjhiNi0zMWZjNTlmMGEyZmMiLCJqdGkiOiI5ZjkzZDY2Yy1jM2E1LTRhNjktODcyMC1mMTUyMjE1NTUwMGMiLCJpYXQiOjE3ODE3NjA2Mjd9.XK6g1jvlCXou5oV562fgKpNLkuTDM3pOxYnpzQUhAFE"
MCP_URL = "https://api.ninehire.com/developer/mcp"

logger = logging.getLogger(__name__)

def call_ninehire_mcp(tool_name: str, arguments: dict):
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream"
    }
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": arguments
        }
    }
    try:
        resp = requests.post(MCP_URL, headers=headers, json=payload, timeout=15)
        if resp.status_code != 200:
            return {"success": False, "error": f"HTTP {resp.status_code}: {resp.text}"}
        
        result = resp.json().get("result", {})
        content = result.get("content", [])
        if content and content[0].get("type") == "text":
            return {"success": True, "data": json.loads(content[0].get("text", "{}"))}
        return {"success": True, "data": result}
    except Exception as e:
        return {"success": False, "error": str(e)}

def sync_candidate_tags_to_ninehire():
    """
    Find all candidates with status 'accepted' or 'declined' and sync to Ninehire.
    Applies tag '입사확정' (accepted) or '입사포기' (declined).
    """
    candidates = get_all_candidates()
    
    # Group operations by recruitmentId
    recruitment_ops = {}
    synced_candidates = []
    
    for c in candidates:
        if c["status"] not in ["accepted", "declined"]:
            continue
        
        rec_id = c["ninehire_recruitment_id"]
        app_id = c["ninehire_applicant_id"]
        if not rec_id or not app_id:
            continue
            
        tag_name = "입사확정" if c["status"] == "accepted" else "입사포기"
        
        if rec_id not in recruitment_ops:
            recruitment_ops[rec_id] = []
            
        recruitment_ops[rec_id].append({
            "type": "add",
            "tagContent": tag_name,
            "applicantProgressIds": [app_id]
        })
        synced_candidates.append(c["id"])

    results = []
    for rec_id, ops in recruitment_ops.items():
        res = call_ninehire_mcp("commit_apply_applicant_tags", {
            "recruitmentId": rec_id,
            "operations": ops
        })
        results.append({
            "recruitmentId": rec_id,
            "result": res
        })

    # Mark candidates as synced
    for cid in synced_candidates:
        mark_ninehire_synced(cid)
        
    return {
        "success": True,
        "synced_count": len(synced_candidates),
        "details": results
    }

if __name__ == "__main__":
    print("Ninehire Sync Module Loaded.")
