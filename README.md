# AI CUP 2025 醫病語音敏感個人資料辨識競賽
本專案提供一個名為 AudioAnalyzer 的類別，專門用於處理音訊檔案，將語音內容轉錄為文字，並從中識別出潛在的敏感資訊。該類別整合了 OpenAI Whisper 模型進行高準確度的語音轉文字處理，並結合 spaCy 進行命名實體識別（NER），同時輔以自訂的正規表達式，以提升對敏感資料的偵測能力，如個人資訊、時間資訊及職業等。

功能特色


語音轉文字： 使用 Whisper 模型將音訊檔案轉錄成文字。

敏感資訊提取： 識別並提取多種敏感資訊類型，包括：

年齡 (AGE)

病歷號碼(MEDICAL_RECORD_NUMBER)

身分證字號 (ID Number)

郵遞區號 (ZIP Code)

電話號碼 (PHONE_NUMBER)

網址 (URL)

部門 (DEPARTMENT)

街道地址 (STREET)

個人姓名 (PERSONAL NAME/FAMILY NAME)

醫院和組織 (HOSPITAL/ORGANIZATION)

日期(DATE)

時間戳記： 為所有識別出的敏感實體提供在音訊中的開始和結束時間戳記。

重疊實體處理： 智慧處理不同方法 (正規表達式和 spaCy 模型) 偵測到的重疊實體，避免重複。

音訊資料夾處理： 能夠處理指定資料夾內的所有音訊檔案。

1. 建立虛擬環境
python -m venv venv
# Windows 系統
.\venv\Scripts\activate
# macOS/Linux 系統
source venv/bin/activate
2. 
3. 

