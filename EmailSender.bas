' ========================================================
' 2026년 화신그룹 정규직 전환 입사확인 이메일 발송 매크로
' Excel VBA 모듈 (Alt + F11 -> 모듈 삽입 후 붙여넣기)
' ========================================================

Sub SendConfirmationEmails()
    Dim OutlookApp As Object
    Dim OutlookMail As Object
    Dim ws As Worksheet
    Dim lastRow As Long
    Dim i As Long
    Dim sendCount As Long
    Dim testMode As VbMsgBoxResult
    Dim testEmail As String
    
    On Error Resume Next
    Set ws = ThisWorkbook.Sheets("메일발송명단")
    If ws Is Nothing Then
        Set ws = ActiveSheet
    End If
    On Error GoTo 0
    
    lastRow = ws.Cells(ws.Rows.Count, "A").End(xlUp).Row
    
    testMode = MsgBox("2026년 화신그룹 공채 메일 발송 매크로입니다." & vbCrLf & vbCrLf & _
                      "▶ [예 (Y)] : [테스트] 홍길동 (010-1234-5678) 1건 발송" & vbCrLf & _
                      "▶ [아니오 (N)] : [본 발송] 1~11번 합격자 전원 일괄 발송" & vbCrLf & _
                      "▶ [취소] : 작업 취소", vbYesNoCancel + vbQuestion, "화신 채용 메일 발송기")
                      
    If testMode = vbCancel Then Exit Sub
    
    On Error Resume Next
    Set OutlookApp = GetObject(, "Outlook.Application")
    If OutlookApp Is Nothing Then
        Set OutlookApp = CreateObject("Outlook.Application")
    End If
    On Error GoTo 0
    
    If OutlookApp Is Nothing Then
        MsgBox "Microsoft Outlook을 실행할 수 없습니다. Outlook이 설치되어 있는지 확인해주세요.", vbCritical
        Exit Sub
    End If
    
    ' 1. 홍길동 테스트 발송 모드
    If testMode = vbYes Then
        testEmail = InputBox("테스트 메일을 수신받을 본인 이메일 주소를 입력하세요:", "홍길동 테스트 발송", "")
        If Trim(testEmail) = "" Then Exit Sub
        
        Set OutlookMail = OutlookApp.CreateItem(0)
        With OutlookMail
            .To = testEmail
            .Subject = ws.Cells(2, "G").Value
            .Body = ws.Cells(2, "H").Value
            .Send
        End With
        
        ws.Cells(2, "I").Value = "발송완료 (" & Format(Now, "yyyy-mm-dd hh:mm") & ")"
        MsgBox "홍길동 테스트 메일이 성공적으로 발송되었습니다!" & vbCrLf & "수신함(" & testEmail & ")을 확인해주세요.", vbInformation, "테스트 발송 완료"
        Exit Sub
    End If
    
    ' 2. 1~11번 실제 합격자 전원 본 발송 모드
    If MsgBox("실제 합격자 11명 전원에게 이메일을 발송하시겠습니까?", vbYesNo + vbExclamation, "최종 발송 확인") = vbNo Then
        Exit Sub
    End If
    
    sendCount = 0
    For i = 3 To lastRow
        If ws.Cells(i, "C").Value <> "" Then
            Set OutlookMail = OutlookApp.CreateItem(0)
            With OutlookMail
                .To = ws.Cells(i, "C").Value
                .Subject = ws.Cells(i, "G").Value
                .Body = ws.Cells(i, "H").Value
                .Send
            End With
            ws.Cells(i, "I").Value = "발송완료 (" & Format(Now, "yyyy-mm-dd hh:mm") & ")"
            sendCount = sendCount + 1
        End If
    Next i
    
    MsgBox "총 " & sendCount & "명의 합격자에게 이메일 발송이 성공적으로 완료되었습니다!", vbInformation, "발송 완료"
End Sub
