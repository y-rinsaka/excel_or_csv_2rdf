import os
import json

def read_json_files(directory_path):
    json_data = []
    for filename in os.listdir(directory_path):
        if filename.endswith(".json") and filename != "3-総農家数.json":
            file_path = os.path.join(directory_path, filename)
            with open(file_path, "r") as file:
                data = json.load(file)
                json_data.append(data)
    return json_data

def combine_json_lists(json_lists):
    combined_list = [{} for _ in range(len(json_lists[0]))]
    for json_data in json_lists:
        for i, item in enumerate(json_data):
            combined_list[i].update(item)
    return combined_list

output_directory = "output/tmp"
ireko_B_path = os.path.join(output_directory, "ireko/B")
ireko_C_path = os.path.join(output_directory, "ireko/C")

# ファイルを読み込んで結合
json_lists_B = read_json_files(output_directory)
json_lists_C = read_json_files(output_directory)

# ireko ディレクトリ内のファイルを読み込んで結合
json_lists_B.extend(read_json_files(ireko_B_path))
json_lists_C.extend(read_json_files(ireko_C_path))

# 結合処理
combined_list_B = combine_json_lists(json_lists_B)
combined_list_C = combine_json_lists(json_lists_C)

# 結合結果を出力
with open("output/JSON/B.json", "w") as output_file_B:
    json.dump(combined_list_B, output_file_B, indent=2, ensure_ascii=False)

with open("output/JSON/C.json", "w") as output_file_C:
    json.dump(combined_list_C, output_file_C, indent=2, ensure_ascii=False)



