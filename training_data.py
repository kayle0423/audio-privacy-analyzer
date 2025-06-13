import re
import random
import copy
import spacy
from spacy.tokens import DocBin
from tqdm import tqdm # 用於顯示進度條
from spacy.util import filter_spans # 用於處理重疊實體


# --- 換字資料 (Replacement Data) ---


states_list = {
            "Ohio", "California", "Montana", "Rhode Island", "California", "Northern Territory", "Victoria",
            "Western Australia", "South Australia", "ACT", "TAS", "VIC", "NT", "Tasmania", "New South Wales", "QLD",
            "Australian Capital Territory", "WA", "Leeton", "Denman", "SA", "Moranbah", "Oregon", "Delaware", "RA", "RI",
            "Texas", "Queensland", "Territory", "Florida", "Pennsylvania", "Illinois", "Georgia", "North Carolina",
            "Michigan", "Virginia", "Washington", "Arizona", "Massachusetts", "CA", "TX", "FL", "PA",
            "IL", "OH", "GA", "MI", "VA", "AZ", "MA"
}
countries_list = {"India", "Madagascar", "Ethiopian",
                "United States", "USA", "China", "Syria", "Brazil", "Russia",
                "Japan", "Germany", "France", "UK", "Italy", "Canada", "South Korea", "Thailand",
}
city_list = {"Geneva", "Chicago", "Hamden", "Denver", "Shresthire", "Camden Haven", "Kyabram", "Devonport",
             "Nambucca Heads", "Kiama", "Mount Eliza", "Bowen", "Bonny Hills", "Port Adelaide Enfield",
             "Orbost", "Northam", "Stirling", "Armidale", "Caboolture", "Cobar", "Penguin", "Coonabarabran",
             "Urraween", "Moura", "Kyabram", "Barwon Heads", "Banora Point, South", "Goondiwindi",
             "Smithton", "Gold Coast", "Howlong", "Beaconsfield Upper", "Batemans Bay", "Yamba", "Casino",
             "Richmond", "Newcastle", "Wauchope", "Gosford", "Bega", "Thirlmere", "Goolwa", "Newcastle",
             "Waterford", "Orbost", "Vincentia", "Moranbah", "Rockhampton", "Millicent", "Buninyong",
             "Tinonee", "Aldgate", "Lismore", "Williamstown", "Roxby Downs", "Leongatha", "LA", "Frederick",
             "Sydney", "Phoenix", "San Francisco", "Austin", "Taree", "Kingaroy", "Curlewis", "Silverdale",
             "Ipswich", "Bacchus Marsh", "Terranora", "Windsor", "Lara", "Encounter Bay", "Mulwala", "Gosford",
             "Blayney", "Redcliffe", "Launceston", "Bega", "Newcastle", "Sanctuary Point", "Tea Gardens", "Moama",
             "San Remo", "Miami", "San Antonio", "Chicago", "Wallingford",
}
STREET_list = {"Stratford House", "Rocky Spring", "Rossi", "Prairie Hill", "Devonport", "Cantello",
                 "Hamstrom", "Vincents", "Upper Mount Glen Lake", "N Cumnor", "Main Line", "Fort Foote",
                 "Capertee", "Fawkham", "Talbryn", "Richland Valley", "Glenview", "Lower Matchaponix", "Leestone",
                 "Midge Hall", "New Jefferson", "Juniper Point", "Pleasant Chase", "Daley", "Sylmar", "Belcourt",
                 "Northome", "Wokindon", "West Railroad", "Legra", "Mildura", "Forest Knoll", "Oxendon", "Stockdale",
                 "West Bolivar", "Nimco", "Marjorie Jackson", "E Joffre", "Kimball Hill", "South Tinnin", "Quincey",
                 "Tarporley", "North Napa", "Colemans"
}
LOCATION_OTHER_list = {"Mystic", "Canterbury", "Andover", "Chicago metro area", "P.O. Box 15",
                         "Tenterfield", "Tenterfield", "Brooklyn Bridge", "New Haven", "Genevieve", "Africa",
                         "African", "Denver", "Brown"}

ORG_list = {"Bank of America", "YMCA", "Cambridge Business", "Subway", "Sealed Air Corporation",
        "Delta Air Lines", "Ameren Corporation", "Boston Scientific", "Google", "Orizia", "Starbucks",
        "Divinity School Library", "Wesley", "Cambridge", "Michaels", "Datsun", "libraries",
        "Western Convention Center", "Career Services", "seekers workshop", "Jewish girl's school"
        }

PATIENT_names = {
             "Jessa", "Ramona", "Audrey", "Taylor", "Jessica", "Tanya", "Crazy", "Stacy", "Mason", "Gordan", "Chris", "Nida",
             "Jolin", "Sabrina", "Eric", "Roy", "Ashley", "Alan", "Katrina", "Oliva", "Carol", "Dora", "Cathy", "Nikola",
             "Oliver", "Maria", "Calvin", "Jessup", "Kinkos", "Mike", "Virgina", "George", "Tomas", "Gordan", "Anny", "Mark",
             "Tereasa", "Sara", "Leon", "Jeremy", "Isa", "Ella", "Ariel", "Derrick", "Brendon", "Florrie", "Jasper", "Katrina",
             "Roy", "Dillon", "Garry", "Calvin", "Connie", "Sabrina", "Nikola", "Ariel", "Kenny", "Susan",
             "June", "Jesse", "Elizabeth", "Cameron", "Tonya", "Meg",

}

DOCTOR_names = {
             "Dave", "Debbie", "VX", "Jamie", "Kantarian", "YQ", "A Saylor", "IJ", "Theis", "Nora Melvin Morreale", "Mr. Hunter",
             "Nguya Adolfo Tries", "Henson", "Yu DiRenzo", "Sharla Carithers", "WG", "XW", "Raul Errol Paulhus", "GE", "fr",
             "Quade Edison Jenness", "Tarka Williams Krahn", "X Nalley", "Stewart", "Hook", "Rickson Naya Marcus",
             "Barnes", "Bourd", "Board", "Jones", "Micah", "Green", "Farrow", "Chad", "Yep",
}

family_names = {
             "Ivan", "Josh", "Lucille", "Smith", "Johnson", "Williams", "Brown", "Jones",
             "Miller", "Davis", "Wilson", "Stefan", "Tanya", "Harold", "Steppen",
             "Taunia", "Thompson", "Allen", "Parker", "Lewis", "Emma"
}

PERSONALNAME_list = {"Jess", "Kelly", "Franco", "Riley", "David", "Jeez", "Sydney", "Hooray", "Josh", "Emma", "Damien", "Carl",
                     "Candice", "Vanessa", "Lucy", "Yvonne", "Ian",
                     "James", "Martin", "David", "Madison", "Christopher", "Lucille", "Amy", "Tanya"}

AGE_list = {"20", "15", "68", "75", "24", "50", "35", "46"}

# 將所有列表轉換為 list，並匯集到 replacement_dict
replacement_dict = {
    "PATIENT": list(PATIENT_names),
    "DOCTOR": list(DOCTOR_names),
    "PERSONALNAME": list(PERSONALNAME_list),
    "FAMILYNAME": list(family_names),
    "STREET": list(STREET_list),
    "CITY": list(city_list),
    "STATE": list(states_list),
    "AGE": list(AGE_list),
    "ORGANIZATION": list(ORG_list), # 這裡將 ORG_list 對應到 ORGANIZATION，這是 spaCy 常用標籤
    # 如果您有其他 PII 類型及其對應的替換列表，請在此處添加
    # 例如： "COUNTRY": list(countries_list),
    # "LOCATION_OTHER": list(LOCATION_OTHER_list),
}

# --- 讀取train_text文本 ---
def load_full_text(path):
    """
    讀取train_text文本，將檔案名稱對應到文本內容。
    """
    full_text_dict = {}
    with open(path, 'r', encoding='utf-8-sig') as f:
        for line in f:
            if not line.strip():
                continue
            # 使用 maxsplit=1 確保只在第一個 '\t' 處分割
            file_name, text = line.strip().split('\t', maxsplit=1)
            full_text_dict[file_name] = text
    return full_text_dict


# --- 處理train_data敏感資料註解 ---
def process_entities(path):
    """
    處理train_data敏感資料註解，將檔案名稱對應到其敏感實體列表。
    """
    entity_dict = {}
    with open(path, 'r', encoding='utf-8-sig') as f:
        for line in f:
            items = line.strip().split('\t')
            if len(items) < 5: # 確保行有足夠的列
                print(f"跳過格式錯誤的行: {line.strip()}")
                continue
            file_name = items[0]
            ent = {
                "label": items[1],
                # 實體文本可能包含空格，因此需要將剩餘部分拼接起來
                "text": " ".join(items[4:]).strip()
            }
            # 使用 setdefault 確保每個 file_name 都有一個列表
            entity_dict.setdefault(file_name, []).append(ent)
    return entity_dict


# --- 建立原始訓練集和擴增的訓練集 ---
def build_training_data(full_text_dict, entity_dict, augment_count=1):
    """
    建立原始訓練集和擴增的訓練集。
    將文本與其註解的敏感實體配對，並可選擇進行資料擴增。
    """
    train_data = [] # 這將包含擴增後的資料
    original_data_only = [] # 這將只包含原始資料

    for file_name, text in tqdm(full_text_dict.items(), desc="正在建立訓練資料"):
        ents = []
        # 如果該檔案沒有對應的實體註解，則跳過
        if file_name not in entity_dict:
            continue

        used_spans = set()  # 判斷是否為重複的實體跨度

        for ent in entity_dict[file_name]:
            label = ent["label"]
            # escape 正則表達式特殊字元，以確保精確匹配
            entity_text = re.escape(ent["text"])
            # 使用 finditer 找到所有匹配項
            matches = list(re.finditer(entity_text, text))
            found = False
            for match in matches:
                start, end = match.start(), match.end()
                # 檢查這個跨度是否已經被使用過 (避免重複註解同一個實體)
                if (start, end) not in used_spans:
                    ents.append((start, end, label))
                    used_spans.add((start, end))
                    found = True
                    break # 找到第一個不重複的匹配就夠了
            if not found:
                # 提示找不到在文本中匹配的註解實體 (這通常表示註解或文本有問題)
                print(f"警告: 在檔案 '{file_name}' 中找不到敏感資料 '{ent['text']}' (標籤: {ent['label']})")

        if ents:
            # 加入原始訓練集
            original_data_only.append((text, {"entities": ents}))
            # 訓練資料集一開始包含原始數據
            train_data.append((text, {"entities": ents}))

            # 進行字元層級的資料擴增
            for _ in range(augment_count):
                text_chars = list(text)  # 將文本轉換為字元列表以便修改
                new_ents = []

                # 打亂實體順序，然後按結束位置降序排序。
                # 這樣替換時從後往前處理，避免修改文本長度導致後續實體位置錯亂。
                shuffled_ents = copy.deepcopy(ents) # 深度複製，以免影響原始ents
                random.shuffle(shuffled_ents)
                shuffled_ents.sort(key=lambda x: x[1], reverse=True) # 按結束位置逆序排序

                for start, end, label in shuffled_ents:
                    repl_list = replacement_dict.get(label)
                    if not repl_list:
                        # 如果沒有定義替換列表，則跳過此實體
                        # 否則，將原始實體添加到新的註解中，以保留它
                        # new_ents.append((start, end, label))
                        continue

                    replacement = random.choice(repl_list)

                    # 在字元列表中進行替換
                    text_chars[start:end] = list(replacement)

                    # 計算新實體的跨度。
                    # 因為是從後往前替換，新的 start 和 end 會自動正確。
                    new_ents.append((start, start + len(replacement), label))

                # 將新實體的順序按開始位置升序回復
                new_ents.sort(key=lambda x: x[0])
                aug_text = ''.join(text_chars) # 將字元列表重新組合成字串

                if new_ents: # 確保有生成新的實體註解
                    train_data.append((aug_text, {"entities": new_ents}))

    return train_data, original_data_only


# --- 建立DocBin檔案，儲存成train.spacy ---
def create_docbin(training_data, nlp_blank_model, save_path):
    """
    建立DocBin檔案，將處理好的訓練資料儲存為 .spacy 格式。
    """
    doc_bin = DocBin()
    # 使用 tqdm 顯示進度條
    for text, annotations in tqdm(training_data, desc=f"正在為 {save_path} 建立 DocBin"):
        doc = nlp_blank_model.make_doc(text) # 創建一個空的 Doc 物件
        spans = []
        for start, end, label in annotations["entities"]:
            # doc.char_span 根據字元偏移量創建 Span 物件。
            # alignment_mode="contract" 處理文本可能有多餘空白的情況。
            span = doc.char_span(start, end, label=label, alignment_mode="contract")
            if span:
                spans.append(span)
            else:
                # 打印出任何 char_span 建立失敗的情況，有助於調試。
                print(f"警告: char_span 建立失敗 (可能原因: 字元偏移量不正確或實體跨越了非連續的空白):")
                print(f"  文本片段: '{text[max(0, start-20):min(len(text), end+20)]}'")
                print(f"  有問題的實體: 原始文本片段未找到 (start={start}, end={end}, label='{label}')")
                # 您可以選擇跳過這個 span 或實施更強健的錯誤處理。

        # 過濾重疊的 span。spaCy 訓練時通常不允許重疊的實體。
        # filter_spans 會智慧地選擇最長的非重疊跨度。
        doc.ents = filter_spans(spans)
        doc_bin.add(doc)

    doc_bin.to_disk(save_path)
    print(f"成功儲存 DocBin 檔案到: {save_path}")


# --- 主程式 (Main Execution Block) ---
if __name__ == "__main__":
    # --- 設定 ---
    # 定義您的輸入文本檔案和註解檔案的路徑。
    # 請確保這些路徑相對於您執行腳本的位置是正確的，或者使用絕對路徑。
    text_file = "data/train_text.txt"
    entity_file = "data/train_data.txt"
    output_train_spacy_path = "output/train.spacy"
    
    # 定義每個原始樣本要創建的擴增樣本數量。
    # augment_count=1 表示每個原始樣本會產生一個擴增樣本。
    augmentation_multiplier = 1 

    # --- 步驟 1: 載入原始文本和註解 ---
    print(f"正在從 {text_file} 載入完整文本")
    texts = load_full_text(text_file)
    print(f"正在從 {entity_file} 處理實體註解")
    entities = process_entities(entity_file)

    # --- 步驟 2: 初始化一個空的 spaCy 語言模型 ---
    # 這個空白模型用於 `make_doc` 和 `char_span` 以建立 Doc 物件。
    # 它不包含任何預訓練的管道，因為我們只需要它的基本功能來構建用於訓練的 Doc 物件。
    # 根據您的資料語言設定為 "en" (英文) 或 "zh" (中文) 等。
    nlp_blank = spacy.blank("en") 

    # --- 步驟 3: 建立訓練資料集 (包含資料擴增) ---
    print(f"正在建立訓練資料集 (擴增倍數={augmentation_multiplier})...")
    train_data, original_data_only = build_training_data(texts, entities, augment_count=augmentation_multiplier)
    
    print(f"原始資料樣本數: {len(original_data_only)}")
    print(f"擴增後總訓練資料樣本數 (原始 + 擴增): {len(train_data)}")

    # --- 步驟 4: 以 spaCy DocBin 格式儲存訓練資料 ---
    print(f"正在建立 DocBin 檔案並儲存到: {output_train_spacy_path}")
    create_docbin(train_data, nlp_blank, output_train_spacy_path)

    print("\n資料準備完成！您現在可以使用 'output/train.spacy' 檔案來訓練您的 spaCy 模型。")
