import json

input_json_filename = "3-総農家数"
# JSONファイルを読み込む
with open("output/" + input_json_filename + ".json", "r") as file:
    data = json.load(file)
    
def transform_data_for_C(data):
    transformed_data = []
    # ハイフンで区切られたキーを解析して辞書を作成
    for d in data:
        converted_data = {}
        for key, value in d.items():
            parts = key.split("-")
            current_dict = converted_data
            for i, part in enumerate(parts[:-1]):
                if part not in current_dict:
                    current_dict[part] = {}
                current_dict = current_dict[part]
            current_dict[parts[-1]] = value
        transformed_data.append(converted_data)
    return transformed_data
    
json_for_C = transform_data_for_C(data)

# 変換結果を出力する
print(json.dumps(json_for_C, ensure_ascii=False, indent=2))
# 新しいJSONファイルとして出力する
with open("output/ireko/C/" + input_json_filename + "-C.json", "w") as file:
    json.dump(json_for_C, file, ensure_ascii=False, indent=2)
    
def transform_data_for_B(data_for_C):
    transformed_data = []
    
    for entry in data_for_C:
        transformed_entry = {}
        for key, values in entry.items():
            transformed_values = []
            for column, value in values.items():
                transformed_values.append({
                    "種": column,
                    "値": value
                })
            transformed_entry[key] = transformed_values
        transformed_data.append(transformed_entry)

    return transformed_data


json_for_B = transform_data_for_B(json_for_C)

# 変換結果を出力する
print(json.dumps(json_for_B, ensure_ascii=False, indent=2))
# 新しいJSONファイルとして出力する
with open("output/ireko/B/" + input_json_filename + "-B.json", "w") as file:
    json.dump(json_for_B, file, ensure_ascii=False, indent=2)
