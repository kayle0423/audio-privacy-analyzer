# AI CUP 2025 醫病語音敏感個人資料辨識競賽
Team: TEAM_7254

隊員：吳國瑒(組長)、林仁凱、盧羿丞

Private leaderboard：0.331 / Rank 22

---

## 專案簡介

**AudioAnalyzer** 專案旨在自動轉錄醫療語音錄音，並從中識別和提取**個人可識別資訊 (Personally Identifiable Information, PII)**。它利用 **Whisper** 實現強大的語音轉文字功能，並結合 **spaCy** 和客製化訓練的模型進行進階的命名實體識別 (NER)。我們的目標是精確地找出醫病對話中的敏感資料，並為每個識別出的實體提供時間戳記。

---

## 功能特色

* **精確度語音轉文字**：利用 OpenAI 的 Whisper 模型，以卓越的精確度轉錄音訊。
* 識別多種敏感資訊，包括：
    * **個人姓名** (病患、醫生)
    * **病歷號碼**
    * **身分證字號**
    * **年齡**
    * **電話號碼**
    * **郵遞區號**
    * **網址**
    * **部門** (例如：醫院特定部門)
    * **街道地址**
    * **醫院/組織**
    * **日期** (完整日期和星期幾)
* **時間戳記**：為音訊片段中每個偵測到的 PII 提供確切的開始和結束時間。
* **智慧重疊處理**：防止因不同識別方法 (正規表達式和 spaCy) 導致的重複或衝突的 PII 偵測。
* **批次處理**：高效處理指定資料夾中的多個音訊檔案。

---



### 環境配置

* **作業系統**：Windows 11, macOS
* **開發平台**：PyCharm, Google Colab Pro (A100 GPU 支援)
* **程式語言**：Python 3.12

### 下載套件

```Python
pip install -U openai-whisper
!pip install spacy
python -m spacy download en_core_web_trf
```
```Python
from google.colab import drive
drive.mount('/content/drive')
```
若使用Google Colab，將音檔放到雲端並從雲端讀取。

---

### 程式碼解釋

---

以下是對 `AudioAnalyzer` 類別中各個方法和組件的詳細說明。

`class AudioAnalyzer`

`__init__(self)`:

1.` Whisper` 模型初始化：
```Python
self.model = whisper.load_model("large-v3")
```
初始化 `Whisper` 語音轉文字模型。選擇`large-v3`來提高轉錄的精確度。

2. `spaCy` 模型載入：
```Python
self.nlp = spacy.load("./output/model-best")
self.nlp_trf = spacy.load("en_core_web_trf")
```
`self.nlp` 載入一個客製化訓練的 spaCy 模型，它通常針對特定領域（例如醫療領域）進行了訓練，以識別出一般通用模型可能忽略的專有名詞或實體。 `self.nlp_trf `載入 `en_core_web_trf`，這是 spaCy 提供的一個基於 Transformer 的大型英文模型。它提供強大的通用命名實體識別能力，用於補充客製化模型可能未涵蓋的實體。

3.正規表達式定義：
```Python
self.AGE_PATTERN = re.compile(
    r"\b(\d{1,3}) years old|(\d{1,3}) year old|([a-z]{3,}) years old|I'm (\d{1,3})|([a-z]{3,})-year-old|I am (\d{1,3})|feel (\d{1,3})\b")
self.DEPARTMENT_PATTERN = re.compile(
    r'\b([A-Z][a-z]+(?: [A-Z][a-z]+)* Department|Department of [A-Z][a-z]+(?: [A-Z][a-z]+)*|[A-Z]{2,} Department)\b')
self.RE_PATTERNS_phrase = {
    # ... (其他正規表達式) ...
}
```
`self.AGE_PATTERN` 和 `self.DEPARTMENT_PATTERN` 定義了用於匹配年齡和部門的正規表達式 (Regular Expressions)，這些模式是為了精確捕捉特定格式的資訊。 `self.RE_PATTERNS_phrase` 是一個字典，匯集了多種敏感資訊類型（如病歷號碼 (`MEDICAL_RECORD_NUMBER`)、身分證字號 (`ID_NUMBER`)、郵遞區號 (`ZIP`)、電話 (`PHONE`)、網址 (`URL`)、街道 (`STREET`)）的正規表達式。這些正規表達式能夠識別出文字中具有特定格式的敏感資料。

4.日期模式與星期集合：
```Python
self.full_date_pattern = re.compile(
    r"^(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}$"
)
self.day = {"Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"}
self.full_date_pattern 用於識別完整日期的正規表達式（例如 "July 22, 1980"）。 self.day 包含所有星期名稱的集合，用於日期相關的識別。
```
---
### 方法:

`remove(self, word)`:

功能：從輸入的 `word` 字串中移除常見的標點符號，如句號、逗號、問號。

```Python
def remove(self, word):
    return re.sub(r'[.,\?]', '', word)
```
目的：用於在進行比對前，對單字進行清理，減少標點符號的干擾。

`remove_punctuation(self, word)`:

功能：移除 word 字串中的標點符號、空格或所有格的 's。

```Python
def remove_punctuation(self, word):
    return re.sub(r"[.,\?\s]|'s", '', word)
```
目的：更徹底地清理單字，使其適合在時間戳記匹配時與轉錄結果中的單字進行精確比對。

---

`time_stamp(self, sensitive_info, result)`:

功能：這是核心的時間戳記匹配方法。它會根據 `extract_sensitive_entities `識別出的敏感資訊，在 `Whisper` 轉錄結果的單字級別時間戳記中找到這些資訊對應的精確開始和結束時間。

```Python
def time_stamp(self, sensitive_info, result):
    # ... (方法內部邏輯) ...
```
流程：
 
1.計算每條敏感資訊的出現次數。

2.遍歷 `Whisper` 轉錄的每個語音片段 (`segment`)。

3.將語音片段中的每個單字進行清理（移除標點符號）。

4.嘗試在清理後的單字序列中找到完整的敏感資訊短語。

5.特別處理如 `"the"`, `"about"` 等可能出現在敏感資訊前的介詞或副詞，進行偏移處理，以確保時間戳記精確地捕捉敏感資訊本身。

6.如果短語完全匹配，則記錄其類型、內容及在原始音訊中的開始和結束時間。

7.如果直接短語匹配失敗，會嘗試尋找連續單字連接形成敏感資訊的情況（例如，當 `Whisper` 將 `"ID number"` 轉錄為 `"ID" `和 `"number" `兩個單字時，它仍能識別出它們的組合）。

8.使用 `used_indices` 集合來追蹤已匹配的單字索引，防止重複匹配同一段語音。

---

`is_overlapping(self, ent, matcher_list)`:

功能：檢查一個新的 spaCy 實體 (ent) 是否與之前已識別的任何實體或正規表達式匹配的範圍 (matcher_list) 存在字元位置上的重疊。

```Python
def is_overlapping(self, ent, matcher_list):
    for start, end, _ in matcher_list:
        if not (ent.end_char <= start or ent.start_char >= end):
            return True # 有重疊
    return False # 無重疊
```
目的：避免將同一個敏感資訊重複識別和報告，例如，如果一個正規表達式已經找到了電話號碼，而 spaCy 也將它識別為一個數字實體，此方法會跳過 spaCy 的重複識別。

---

`extract_sensitive_entities(self, text)`:

功能：這是從轉錄文本中抽取出所有敏感實體的主要方法。

```Python
def extract_sensitive_entities(self, text):
    sensitive_info = []
    time_matcher_list = []
    doc = self.nlp(text)
    doc_trf = self.nlp_trf(text)

    # ... (方法內部邏輯) ...
    return sensitive_info
```
流程：

1.初始化 `sensitive_info` 列表（存放結果）和 `time_matcher_list`（記錄已識別實體的字元範圍，用於重疊檢查）。

2.首先應用所有預定義的正規表達式 (`RE_PATTERNS_phrase`) 尋找特定格式的敏感資料。找到的匹配會被添加到 `sensitive_info` 和 `time_matcher_list`。

3.使用客製化訓練的 `spaCy` 模型 (`self.nlp`) 對文本進行處理，識別出命名實體。

4.遍歷客製化模型識別出的每個實體，如果它不與現有匹配重疊，並且不是已被正規表達式處理的類型（如 `ZIP`、`PHONE`），則將其添加到 `sensitive_info`。特別處理了人名和醫生名的判斷。

5.使用通用 `spaCy` 模型 (`self.nlp_trf`) 對文本進行處理，進一步識別命名實體。

6.遍歷通用模型識別出的每個實體，如果它不與現有匹配重疊，則將其添加到 `sensitive_info`。這裡處理了 `PERSON`、`ORG `(組織，特別是包含 `"department"` 或 `"hospital"` 的組織會被進一步歸類) 和 `DATE` (特別是星期幾) 等實體類型。

---
`correct_time_format(self, text)`:

功能：對轉錄後的文本進行格式校正。例如，將數字之間的點（如 "10.30"）替換為冒號（"10:30"），並移除文本中的連字號 -。

```Python
def correct_time_format(self, text):
    text = re.sub(r'\b(\d{1,2})\.(\d{2})\b', r'\1:\2', text)
    text = text.replace('-', '')
    return text
```
目的：提高文本的一致性，有助於後續的正規表達式或 spaCy 識別。

---

```analyze_audio(self, file_path)```:

功能：分析單個音訊檔案的端到端流程。

```Python
def analyze_audio(self, file_path):
    file_name = os.path.basename(file_path).split(".")[0]
    print(f"開始: {file_name}")

    text = ""
    result = self.model.transcribe(file_path, fp16=False, word_timestamps=True)

    # ... (方法內部邏輯) ...
    return sensitive_segments, result, file_name
```
流程：

1.獲取檔案名稱。

2.使用 `self.model.transcribe()` 將音訊檔案轉錄成文字，並獲取單字級別的時間戳記。

3.拼接所有轉錄的文本，並進行時間格式校正。

4.呼叫 `self.extract_sensitive_entities()` 從文本中提取敏感資訊。

5.列印轉錄文本和識別出的敏感資訊。

6.返回敏感資訊列表、原始轉錄結果和檔案名稱。

---

`process_folder(self, folder_path)`:

功能：處理指定資料夾中的所有音訊檔案。

```Python
def process_folder(self, folder_path):
    files = sorted(os.listdir(folder_path), key=lambda x: int(x.split('.')[0]))
    file_paths = [os.path.join(folder_path, file) for file in files[:]]

    for file_path in file_paths:
        segments, result, file_name = self.analyze_audio(file_path)
        timestamps = self.time_stamp(segments, result)
        sorted_timestamps = sorted(timestamps, key=lambda x: x['start'])
        print(sorted_timestamps)
        
```
流程：

1.讀取資料夾中的所有檔案，並根據檔名（假設為數字）進行排序。

2.遍歷每個檔案的路徑。

3.對每個檔案呼叫 `self.analyze_audio()` 進行分析。

4.呼叫 `self.time_stamp()` 獲取每個敏感資訊的精確時間戳記。

5.將所有時間戳記按其開始時間排序。

6.列印排序後的時間戳記。

7.包含被註解掉的程式碼，用於將結果寫入 `task2_answer.txt` 文件）。

---

主程式執行 `(if __name__ == "__main__":)`


```Python
if __name__ == "__main__":
    analyzer = AudioAnalyzer()
    folder_path = "音檔路徑" 
    analyzer.process_folder(folder_path)
```
1.創建 `AudioAnalyzer` 類別的一個實例。

2.定義 `folder_path` 變數，你需要將其設定為你存放音訊檔案的實際路徑。

3.呼叫 `analyzer.process_folder(folder_path)` 開始處理指定資料夾中的所有音訊檔案。

---


 執行：

```Bash
python audio.py
```
---

輸出結果

腳本會將識別出的敏感資訊及其對應的時間戳記列。會將完整的轉錄文字儲存到 `task1_answer.txt`，並將詳細的  結果 (類型、開始時間、結束時間、資訊、時間戳) 儲存到 `task2_answer.txt`。

---


