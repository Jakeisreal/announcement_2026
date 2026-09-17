' ========================================================
' 2026년 화신그룹 정규직 전환 입사확인 이메일 발송 매크로
' 현재 로그인된 Outlook 사내 계정으로 자동 발송됩니다.
' ========================================================

Sub SendConfirmationEmails()
    Dim OutlookApp As Object
    Dim OutlookMail As Object
    Dim ws As Worksheet
    Dim lastRow As Long
    Dim i As Long
    Dim sendCount As Long
    Dim testMode As VbMsgBoxResult
    Dim myEmail As String
    
    On Error Resume Next
    Set ws = ThisWorkbook.Sheets("메일발송명단")
    If ws Is Nothing Then
        Set ws = ActiveSheet
    End If
    On Error GoTo 0
    
    lastRow = ws.Cells(ws.Rows.Count, "A").End(xlUp).Row
    
    On Error Resume Next
    Set OutlookApp = GetObject(, "Outlook.Application")
    If OutlookApp Is Nothing Then
        Set OutlookApp = CreateObject("Outlook.Application")
    End If
    On Error GoTo 0
    
    If OutlookApp Is Nothing Then
        MsgBox "Microsoft Outlook을 실행할 수 없습니다. Outlook이 설치되어 있는지 확인해주세요.", vbCritical, "Outlook 오류"
        Exit Sub
    End If
    
    ' 로그인된 사내 계정 이메일 자동 추출
    myEmail = ""
    On Error Resume Next
    If OutlookApp.Session.Accounts.Count > 0 Then
        myEmail = OutlookApp.Session.Accounts.Item(1).SmtpAddress
    End If
    If myEmail = "" Then
        myEmail = OutlookApp.Session.CurrentUser.AddressEntry.GetExchangeUser.PrimarySmtpAddress
    End If
    If myEmail = "" Then
        myEmail = OutlookApp.Session.CurrentUser.Address
    End If
    On Error GoTo 0
    
    testMode = MsgBox("2026년 화신그룹 공채 메일 발송 매크로 (Outlook 자동 연동)" & vbCrLf & vbCrLf & _
                      "▶ [예 (Y)] : [테스트] 홍길동 메일을 내 사내 계정(" & myEmail & ")으로 즉시 발송" & vbCrLf & _
                      "▶ [아니오 (N)] : [본 발송] 실제 합격자 11명 전원에게 일괄 발송" & vbCrLf & _
                      "▶ [취소] : 작업 취소", vbYesNoCancel + vbQuestion, "화신 채용 메일 발송기")
                      
    If testMode = vbCancel Then Exit Sub
    
    ' 1. 홍길동 테스트 모드 (내 사내 계정으로 자동 발송)
    If testMode = vbYes Then
        If myEmail = "" Then
            myEmail = InputBox("Outlook 계정 주소를 확인할 수 없습니다. 수신할 이메일을 입력하세요:", "테스트 발송", "")
            If Trim(myEmail) = "" Then Exit Sub
        End If
        
        Set OutlookMail = OutlookApp.CreateItem(0)
        With OutlookMail
            .To = myEmail
            .Subject = ws.Cells(2, "G").Value
            .Body = ws.Cells(2, "H").Value
            .Send
        End With
        
        ws.Cells(2, "I").Value = "발송완료 (" & Format(Now, "yyyy-mm-dd hh:mm") & ")"
        MsgBox "홍길동 테스트 메일이 내 사내 계정(" & myEmail & ")으로 성공적으로 발송되었습니다!" & vbCrLf & vbCrLf & _
               "Outlook 받은편지함(또는 보낸편지함)을 확인해보세요.", vbInformation, "테스트 발송 완료"
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
