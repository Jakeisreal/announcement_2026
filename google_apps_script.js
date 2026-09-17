// ========================================================
// 2026년 화신그룹 공채 최종 입사확인 - Google Sheets 실시간 연동 스크립트
// [구글 시트] -> [확장 프로그램] -> [Apps Script]에 붙여넣기
// ========================================================

var HEADERS = [
  "token", "name", "status", "response_english_name", 
  "response_uniform_size", "response_dormitory", 
  "decline_reason", "decline_detail", "responded_at"
];

function doGet(e) {
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  var data = sheet.getDataRange().getValues();
  if (data.length === 0) {
    return ContentService.createTextOutput(JSON.stringify({ status: "success", data: [] }))
      .setMimeType(ContentService.MimeType.JSON);
  }
  
  var startIdx = 0;
  if (data[0][0] === "token") {
    startIdx = 1;
  }
  
  var rows = [];
  for (var i = startIdx; i < data.length; i++) {
    if (!data[i][0]) continue;
    var rowObj = {
      token: String(data[i][0] || ""),
      name: String(data[i][1] || ""),
      status: String(data[i][2] || ""),
      response_english_name: String(data[i][3] || ""),
      response_uniform_size: String(data[i][4] || ""),
      response_dormitory: String(data[i][5] || ""),
      decline_reason: String(data[i][6] || ""),
      decline_detail: String(data[i][7] || ""),
      responded_at: String(data[i][8] || "")
    };
    rows.push(rowObj);
  }
  
  return ContentService.createTextOutput(JSON.stringify({ status: "success", data: rows }))
    .setMimeType(ContentService.MimeType.JSON);
}

function doPost(e) {
  try {
    var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
    var data = sheet.getDataRange().getValues();
    
    // 헤더가 없거나 첫 행이 token이 아니면 헤더 보정
    if (data.length === 0 || data[0][0] !== "token") {
      sheet.insertRowsBefore(1, 1);
      sheet.getRange(1, 1, 1, HEADERS.length).setValues([HEADERS]);
      data = sheet.getDataRange().getValues();
    }
    
    var body = JSON.parse(e.postData.contents);
    var token = String(body.token || "");
    if (!token) {
      return ContentService.createTextOutput(JSON.stringify({ status: "error", message: "Token missing" }))
        .setMimeType(ContentService.MimeType.JSON);
    }
    
    var rowIndex = -1;
    for (var i = 1; i < data.length; i++) {
      if (String(data[i][0]) === token) {
        rowIndex = i + 1;
        break;
      }
    }
    
    var newRow = [
      token,
      body.name || "",
      body.status || "",
      body.response_english_name || "",
      body.response_uniform_size || "",
      body.response_dormitory || "",
      body.decline_reason || "",
      body.decline_detail || "",
      new Date().toLocaleString("ko-KR", { timeZone: "Asia/Seoul" })
    ];
    
    if (rowIndex > 0) {
      sheet.getRange(rowIndex, 1, 1, newRow.length).setValues([newRow]);
    } else {
      sheet.appendRow(newRow);
    }
    
    return ContentService.createTextOutput(JSON.stringify({ status: "success", message: "저장 완료" }))
      .setMimeType(ContentService.MimeType.JSON);
      
  } catch (err) {
    return ContentService.createTextOutput(JSON.stringify({ status: "error", message: err.toString() }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}
