class AudioAnalyzer:
    def __init__(self):
        # Initialize Whisper model
        self.model = whisper.load_model("small")  # medium
        # 載入訓練好的模型
        self.nlp = spacy.load("./output/model-best")
        # trf
        self.nlp_trf = spacy.load("en_core_web_trf")

        # Regular expressions
        self.AGE_PATTERN = re.compile(
            r"\b(\d{1,3}) years old|(\d{1,3}) year old|([a-z]{3,}) years old|I'm (\d{1,3})|([a-z]{3,})-year-old|I am (\d{1,3})|feel (\d{1,3})\b")
        self.DEPARTMENT_PATTERN = re.compile(
            r'\b([A-Z][a-z]+(?: [A-Z][a-z]+)* Department|Department of [A-Z][a-z]+(?: [A-Z][a-z]+)*|[A-Z]{2,} Department)\b')
        self.RE_PATTERNS_phrase = {
            "AGE": self.AGE_PATTERN,
            "MEDICAL_RECORD_NUMBER": re.compile(r"\b([0-9]{6,}[.][A-Za-z]{2,})|([0-9]{6,}[A-Za-z]{2,})|([0-9]{3}.[0-9]{3}.[A-Za-z]{2,})|([0-9][0-9]{5}[A-Za-z]{2,})\b"),
            "ID_NUMBER": re.compile(
                r"\b([0-9]{2}[A-Z][0-9]{5,}[A-Z])\b"  # 2數+1大寫+5數以上+1大寫
                r"|\b([0-9]{2}[A-Z][0-9]{5,})\b"  # 2數+1大寫+5數以上
                r"|\b([0-9]{6,}[A-Z])\b"  # 6數以上 + 大寫字母
                r"|\b([0-9]{9,})\b"
                r"|\b([0-9]{2,3}[A-Z][0-9]{5})\b"  # 39C75774 440D59224 61B09485
                r"|\b([0-9]{2}[A-Z]{2}[0-9]{4})\b"  # 92RA5354
                r"|\b([0-9]{4}[A-Z][0-9]{2})\b"  # 7807A32
                r"|\b([0-9]{2}[A-Z][0-9]{5}[A-Z]{2})\b"  # 94T80766AP
                r"|\b([0-9]{2}[A-Z][0-9]{5}[A-Z][0-9])\b"  # 53P77846A5
                r"|\b([0-9]{2}[A-Z]{4}[0-9]{4}[A-Z])\b"  # 38WiFi7950
                r"|\b([0-9]{2}[A-Z]{2}[0-9]{5}[A-Z])\b"  # 52PA28726X
                r"|\b([0-9]{2}[A-Z][0-9]{4}[A-Z][0-9])\b"  # 30W2344A6
                r"|\b([0-9]{2}[A-Z][0-9]{4}[A-Z])\b"  # 30W2344A
            ),
            "ZIP": re.compile(r"\bcode of (\d{3,4})|code (\d{3,4})|zipco (\d{3,4})\b", re.IGNORECASE),
            "PHONE": re.compile(r'\b(?:([0-9]+) call|called ([0-9]+))\b'),
            "URL": re.compile(r'\b([a-z]{4,}.com)\b'),
            "DEPARTMENT": self.DEPARTMENT_PATTERN,
            "STREET": re.compile(r"\b([A-Z][a-z]+(?: [A-Z][a-z]+)* Street) \b")
        }
        # July 22, 1980
        self.full_date_pattern = re.compile(
            r"^(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}$"
        )

        self.day = {"Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"}
    # 去標點符號
    def remove(self, word):
        return re.sub(r'[.,\?]', '', word)

    # 去標點符號和空格
    def remove_punctuation(self, word):
        return re.sub(r"[.,\?\s]|'s", '', word)
    # 找時間戳
    def time_stamp(self, sensitive_info, result):
        if not sensitive_info:
            return []

        timestamps = []
        info_doc = {}
        info_counter = Counter(sensitive_info)

        for (info_type, info_value), count in info_counter.items():
            info_doc[info_value] = count
        #print("info_doc:", info_doc)
        used_indices = []
        for (info_type, info_value), count in info_counter.items():
            if isinstance(info_value, str):
                info = self.remove(info_value)
                info_list = info.split()
                info_no_find = "".join(info_list)
                #print(info_no_find)
                print(f"Searching for: {info_list}")
                found = False
                remaining = info_doc.get(info_value, 0)

                for idx, segment in enumerate(result['segments']):
                    words = [self.remove_punctuation(w['word']) for w in segment['words']]
                    for i in range(len(words) - len(info_list) + 1):
                        if (info_value, idx, i) in used_indices:
                            continue

                        offset = 0
                        if words[i:i + len(info_list)] == info_list:
                            offset_info_list = info_list[:]
                            if info_list[0].lower() in ["the", "about", "precisely", "exactly"]:
                                offset_info_list = offset_info_list[1:]
                                offset = 1  # 偏移值

                            # 取得對應位置的 start/end
                            start_index = i + offset
                            end_index = i + offset + len(offset_info_list) - 1  # len是從1以上，index要-1

                            start_time = segment['words'][start_index]['start']
                            end_time = segment['words'][end_index]['end']

                            timestamps.append({
                                "type": info_type,
                                "info": " ".join(offset_info_list),
                                "start": round(float(start_time), 2),
                                "end": round(float(end_time), 2)
                            })
                            found = True
                            used_indices.append((info_value, idx, i))
                            #print("used_indices:", used_indices)
                            remaining -= 1
                            info_doc[info_value] -= 1
                            if remaining <= 0:
                                break

                    if remaining <= 0:
                        break
                    if not found:
                        for j in range(len(words)):
                            string = ""
                            for k in range(j, min(j + 4, len(words))):
                                string += words[k]
                                #print(string)
                                if (info_value, idx, k) in used_indices:
                                    continue
                                if string == info_no_find:
                                    start_time = segment['words'][j]['start']
                                    end_time = segment['words'][k]['end']
                                    timestamps.append({
                                        "type": info_type,
                                        "info": info_value,
                                        "start": round(float(start_time), 2),
                                        "end": round(float(end_time), 2)
                                    })
                                    used_indices.append((info_value, idx, k))
                                    remaining -= 1
                                    info_doc[info_value] -= 1
                                    if remaining <= 0:
                                        break

                            if remaining <= 0:
                                break
                    if remaining <= 0:
                        break
        return timestamps

    def is_overlapping(self, ent, matcher_list):
        for start, end, _ in matcher_list:
            if not (ent.end_char <= start or ent.start_char >= end):
                return True
        return False

    def extract_sensitive_entities(self, text):
        sensitive_info = []
        time_matcher_list = []
        doc = self.nlp(text)
        doc_trf = self.nlp_trf(text)

        for category, pattern in self.RE_PATTERNS_phrase.items():
            for match in pattern.finditer(text):
                #print("match:", match)
                match_info = next((g for g in match.groups() if g), None)
                #print("match_info:", match_info)
                if match_info:
                    sensitive_info.append((category, match_info))
                    time_matcher_list.append((match.start(), match.end(), category))

        for i, ent in enumerate(doc.ents):
            print("ent.text:", ent.text, ent.label_)
            if self.is_overlapping(ent, time_matcher_list) or ent.label_ in {"ZIP", "PHONE"}:
                continue
            start = ent.start_char
            if ent.label_ in ["PERSONALNAME", "FAMILYNAME", "PATIENT", "DOCTOR"]:
                if ent.start_char >= 4 and text[start - 4:start] == "Dr. ":
                    sensitive_info.append(("DOCTOR", ent.text))
                else:
                    sensitive_info.append((ent.label_, ent.text))
            else:
                sensitive_info.append((ent.label_, ent.text))

            time_matcher_list.append((ent.start_char, ent.end_char, ent.label_))

        for i, ent in enumerate(doc_trf.ents):
            print("ent.text_trf:", ent.text, ent.label_)
            if self.is_overlapping(ent, time_matcher_list):
                continue

            start = ent.start_char
            if ent.label_ == "PERSON":
                if ent.start_char >= 4 and text[start - 4:start] == "Dr. ":
                    sensitive_info.append(("DOCTOR", ent.text))
            elif ent.label_ == "ORG":
                ent_text = re.sub(r'\bthe\b', '', ent.text).strip()
                if "department" in ent_text.lower():
                    sensitive_info.append(("DEPARTMENT", ent_text))
                elif "hospital" in ent_text.lower() or "health" in ent_text.lower():
                    sensitive_info.append(("HOSPITAL", ent_text))
            elif ent.label_ == "DATE":
                if ent.text.lower() in self.day:
                    sensitive_info.append((ent.label_, ent.text))

        return sensitive_info
    # 時間拼寫
    def correct_time_format(self, text):
        # 時間表達修正
        text = re.sub(r'\b(\d{1,2})\.(\d{2})\b', r'\1:\2', text)
        text = text.replace('-', '')  # 去掉-
        return text

    def analyze_audio(self, file_path):
        file_name = os.path.basename(file_path).split(".")[0]
        print(f"開始: {file_name}")

        text = ""
        result = self.model.transcribe(file_path, fp16=False, word_timestamps=True)

        sensitive_segments = []

        for segment in result["segments"]:
            text += segment["text"]
        # 時間拼寫
        text = self.correct_time_format(text)

        print(f'text: {text}')
        """
        # 取得 "text" 內容，並寫入 task1_answer.txt
        with open("task1_answer.txt", "a", encoding="utf-8") as task1:
            task1.write(f"{file_name}\t{text}\n")
        """
        sensitive_info = self.extract_sensitive_entities(text)
        if sensitive_info:
            sensitive_segments.extend(sensitive_info)

        print(f"{file_name}: {sensitive_segments}")
        return sensitive_segments, result, file_name

    def process_folder(self, folder_path):
        files = sorted(os.listdir(folder_path), key=lambda x: int(x.split('.')[0]))
        file_paths = [os.path.join(folder_path, file) for file in files[:]]  

        for file_path in file_paths:
            segments, result, file_name = self.analyze_audio(file_path)
            timestamps = self.time_stamp(segments, result)
            # 按 start 時間戳升序排序
            sorted_timestamps = sorted(timestamps, key=lambda x: x['start'])
            print(sorted_timestamps)
            """
            # 取得敏感資料內容，並寫入 task2_answer.txt
            with open("task2_answer.txt", "a", encoding="utf-8") as task2:
                for timestamp in sorted_timestamps:
                    task2.write(f"{file_name}\t{timestamp['type']}\t{timestamp['start']}\t{timestamp['end']}\t{timestamp["info"]}\n")

            print("完成")
            """
if __name__ == "__main__":
    analyzer = AudioAnalyzer()
    folder_path = "音檔路徑"
    analyzer.process_folder(folder_path)
