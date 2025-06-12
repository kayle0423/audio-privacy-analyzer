# AI CUP 2025 醫病語音敏感個人資料辨識競賽

---

## 專案簡介

**AudioAnalyzer** 專案旨在自動轉錄醫療語音錄音，並從中識別和提取**個人可識別資訊 (Personally Identifiable Information, PII)**。它利用 **Whisper** 實現強大的語音轉文字功能，並結合 **spaCy** 和客製化訓練的模型進行進階的命名實體識別 (NER)。我們的目標是精確地找出醫病對話中的敏感資料，並為每個識別出的實體提供時間戳記。

---

## 功能特色

* **精確度語音轉文字**：利用 OpenAI 的 Whisper 模型，以卓越的精確度轉錄音訊。
* **全面性 PII 偵測**：識別多種敏感資訊，包括：
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

### 安裝步驟


1.  **建立並啟動虛擬環境：**

    ```bash
    python -m venv venv
    # Windows 系統
    .\venv\Scripts\activate
    # macOS/Linux 系統
    source venv/bin/activate
    ```

    

2.  **安裝所需的 Python 套件：**

    ```bash
    pip install -U openai-whisper
    pip install spacy
    ```

   

3.  **下載 spaCy 模型：**

   

    ```bash
    python -m spacy download en_core_web_trf
    ```

    對於客製化模型，請確保你將訓練好的模型 (`model-best`) 放置在專案中：

    ```
    AudioAnalyzer/
    ├──   model-best/  # 你的客製化 spaCy 模型檔案
    ├── AudioAnalyzer.py
    └── requirements.txt
    ```

---

## 使用方式

安裝完成後，你可以輕鬆分析你的音訊檔案。

1.  **準備你的音訊檔案：** 將所有要分析的音訊檔案 (例如：`.wav`, `.mp3`) 放入一個資料夾中。為了方便依序處理，建議將檔案命名為數字 (例如：`1.wav`, `2.mp3` 等)。

2.  **更新腳本：** 打開 `AudioAnalyzer.py`，修改 `if __name__ == "__main__":` 區塊中的 `folder_path` 變數，使其指向你的音訊目錄：

    ```python
    # AudioAnalyzer.py 檔案中的程式碼片段
    if __name__ == "__main__":
        analyzer = AudioAnalyzer()
        # 重要：請將此路徑替換為你的音訊檔案的實際路徑
        folder_path = "path/to/your/audio/folder"
        analyzer.process_folder(folder_path)
    ```

3.  **執行分析器：**

    ```bash
    python AudioAnalyzer.py
    ```

### 輸出結果

腳本會將識別出的敏感資訊及其對應的時間戳記列印到你的控制台。如果你取消 `analyze_audio` 和 `process_folder` 中寫入檔案部分的註解，它還會將完整的轉錄文字儲存到 `task1_answer.txt`，並將詳細的 PII 結果 (類型、開始時間、結束時間、資訊) 儲存到 `task2_answer.txt`。

---

## `requirements.txt` 檔案內容

建立一個名為 `requirements.txt` 的檔案，內容如下。你可能需要根據相容性或特定需求調整版本。

