' ========================================================
' 2026년 화신그룹 공채 메일 발송 VBScript 실행기
' 더블 클릭 시 Outlook을 통해 자동으로 메일을 발송합니다.
' ========================================================

Option Explicit

Dim objExcel, objWorkbook, objSheet
Dim objOutlook, objMail
Dim fso, curDir, excelPath
Dim lastRow, i, sendCount, testMode, testEmail

Set fso = CreateObject("Scripting.FileSystemObject")
curDir = fso.GetParentFolderName(WScript.ScriptFullName)
excelPath = curDir & "\2026년_공채_입사확인_메일발송_명단.xlsx"

If Not fso.FileExists(excelPath) Then
    MsgBox "엑셀 파일을 찾을 수 없습니다:" & vbCrLf & excelPath, vbCritical, "오류"
    WScript.Quit
End If

testMode = MsgBox("2026년 화신그룹 공채 메일 발송 프로그램 (Outlook 연동)" & vbCrLf & vbCrLf & _
                  "▶ [예 (Y)] : [테스트] 홍길동 (010-1234-5678) 1건 발송" & vbCrLf & _
                  "▶ [아니오 (N)] : [본 발송] 1~11번 합격자 전원 일괄 발송" & vbCrLf & _
                  "▶ [취소] : 작업 취소", vbYesNoCancel + vbQuestion, "화신 채용 메일 발송기")

If testMode = vbCancel Then WScript.Quit

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

Set objExcel = CreateObject("Excel.Application")
objExcel.Visible = False
objExcel.DisplayAlerts = False

Set objWorkbook = objExcel.Workbooks.Open(excelPath)
Set objSheet = objWorkbook.Sheets(1)

lastRow = objSheet.Cells(objSheet.Rows.Count, 1).End(-4162).Row ' -4162 = xlUp

' 1. 홍길동 테스트 모드
If testMode = vbYes Then
    testEmail = InputBox("테스트 메일을 수신할 본인 이메일 주소를 입력하세요:", "홍길동 테스트 발송", "")
    If Trim(testEmail) = "" Then
        objWorkbook.Close False
        objExcel.Quit
        WScript.Quit
    End If
    
    Set objMail = objOutlook.CreateItem(0)
    objMail.To = testEmail
    objMail.Subject = objSheet.Cells(2, 7).Value
    objMail.Body = objSheet.Cells(2, 8).Value
    objMail.Send
    
    objSheet.Cells(2, 9).Value = "발송완료 (" & Now & ")"
    objWorkbook.Save
    objWorkbook.Close
    objExcel.Quit
    
    MsgBox "홍길동 테스트 메일이 성공적으로 발송되었습니다!" & vbCrLf & vbCrLf & _
           "■ 수신 이메일: " & testEmail & vbCrLf & _
           "■ 대상자: 홍길동 (010-1234-5678)" & vbCrLf & _
           "메일함을 확인해보세요.", vbInformation, "테스트 발송 완료"
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
