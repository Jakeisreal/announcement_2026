' ========================================================
' 2026년 화신그룹 공채 메일 발송 VBScript 실행기
' 현재 로그인된 Outlook 사내 계정으로 자동 발송됩니다.
' ========================================================

Option Explicit

Dim objExcel, objWorkbook, objSheet
Dim objOutlook, objMail, objAccount
Dim fso, curDir, excelPath
Dim lastRow, i, sendCount, testMode, myEmail

Set fso = CreateObject("Scripting.FileSystemObject")
curDir = fso.GetParentFolderName(WScript.ScriptFullName)
excelPath = curDir & "\2026년_공채_입사확인_메일발송_명단.xlsx"

If Not fso.FileExists(excelPath) Then
    MsgBox "엑셀 파일을 찾을 수 없습니다:" & vbCrLf & excelPath, vbCritical, "오류"
    WScript.Quit
End If

On Error Resume Next
Set objOutlook = GetObject(, "Outlook.Application")
If objOutlook Is Nothing Then
    Set objOutlook = CreateObject("Outlook.Application")
End If
On Error GoTo 0

If objOutlook Is Nothing Then
    MsgBox "Microsoft Outlook을 실행할 수 없습니다. Outlook이 설치되어 있는지 확인해주세요.", vbCritical, "Outlook 오류"
    WScript.Quit
End If

' 현재 로그인된 Outlook 사내 계정 이메일 자동 추출
myEmail = ""
On Error Resume Next
If objOutlook.Session.Accounts.Count > 0 Then
    myEmail = objOutlook.Session.Accounts.Item(1).SmtpAddress
End If
If myEmail = "" Then
    myEmail = objOutlook.Session.CurrentUser.AddressEntry.GetExchangeUser.PrimarySmtpAddress
End If
If myEmail = "" Then
    myEmail = objOutlook.Session.CurrentUser.Address
End If
On Error GoTo 0

testMode = MsgBox("2026년 화신그룹 공채 메일 발송 프로그램 (Outlook 자동 연동)" & vbCrLf & vbCrLf & _
                  "▶ [예 (Y)] : [테스트] 홍길동 메일을 내 사내 계정(" & myEmail & ")으로 즉시 발송" & vbCrLf & _
                  "▶ [아니오 (N)] : [본 발송] 실제 합격자 11명 전원에게 일괄 발송" & vbCrLf & _
                  "▶ [취소] : 작업 취소", vbYesNoCancel + vbQuestion, "화신 채용 메일 발송기")

If testMode = vbCancel Then WScript.Quit

Set objExcel = CreateObject("Excel.Application")
objExcel.Visible = False
objExcel.DisplayAlerts = False

Set objWorkbook = objExcel.Workbooks.Open(excelPath)
Set objSheet = objWorkbook.Sheets(1)
lastRow = objSheet.Cells(objSheet.Rows.Count, 1).End(-4162).Row ' xlUp

' 1. 홍길동 테스트 모드 (내 사내 계정으로 자동 전송)
If testMode = vbYes Then
    If myEmail = "" Then
        myEmail = InputBox("Outlook 계정 주소를 확인할 수 없습니다. 수신할 이메일을 입력하세요:", "테스트 발송", "")
        If Trim(myEmail) = "" Then
            objWorkbook.Close False
            objExcel.Quit
            WScript.Quit
        End If
    End If
    
    Set objMail = objOutlook.CreateItem(0)
    objMail.To = myEmail
    objMail.Subject = objSheet.Cells(2, 7).Value
    objMail.Body = objSheet.Cells(2, 8).Value
    objMail.Send
    
    objSheet.Cells(2, 9).Value = "발송완료 (" & Now & ")"
    objWorkbook.Save
    objWorkbook.Close
    objExcel.Quit
    
    MsgBox "홍길동 테스트 메일이 내 사내 계정으로 성공적으로 발송되었습니다!" & vbCrLf & vbCrLf & _
           "■ 수신 메일함: " & myEmail & vbCrLf & _
           "■ 내용: 홍길동 (010-1234-5678) 전용 링크" & vbCrLf & vbCrLf & _
           "Outlook 받은편지함(또는 보낸편지함)을 확인해보세요.", vbInformation, "테스트 발송 완료"
    WScript.Quit
End If

' 2. 1~11번 합격자 전원 본 발송 모드
If MsgBox("실제 합격자 11명 전원에게 이메일을 발송하시겠습니까?", vbYesNo + vbExclamation, "최종 발송 확인") = vbNo Then
    objWorkbook.Close False
    objExcel.Quit
    WScript.Quit
End If

sendCount = 0
For i = 3 To lastRow
    If Trim(objSheet.Cells(i, 3).Value) <> "" Then
        Set objMail = objOutlook.CreateItem(0)
        objMail.To = objSheet.Cells(i, 3).Value
        objMail.Subject = objSheet.Cells(i, 7).Value
        objMail.Body = objSheet.Cells(i, 8).Value
        objMail.Send
        
        objSheet.Cells(i, 9).Value = "발송완료 (" & Now & ")"
        sendCount = sendCount + 1
    End If
Next

objWorkbook.Save
objWorkbook.Close
objExcel.Quit

MsgBox "총 " & sendCount & "명의 합격자에게 이메일 발송이 성공적으로 완료되었습니다!", vbInformation, "본 발송 완료"
