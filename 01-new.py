import pandas as pd
import json
import os

excel_file_path = "input/input2.xlsx" # Excelファイルのパスを指定
input_header_num = 3 # ヘッダーの行数を指定
#total_row_info = {"1":[]} # 合計行の情報を指定


def toOneHeader(df):
    # ヘッダーの結合と整形
    new_columns = []
    for column in df.columns:
        if "" in column:
            new_column = "".join(column)
        else:
            new_column = "-".join(column)
        new_columns.append(new_column)

    df.columns = new_columns
    return df

def getHeaderList(input_header_num):
    return [i for i in range(input_header_num)]

def columnToStr(input_column_nums):
    column_str = {}
    if input_column_nums == "":
        return column_str

    selected_nums = input_column_nums.split(",")
    for i in selected_nums:
        column_str[int(i)-1] = "str"
    return column_str

# JSONデータ内の改行文字を除去する関数
def remove_newlines(obj):
    if isinstance(obj, str):
        return obj.replace('\n', ' ')
    elif isinstance(obj, list):
        return [remove_newlines(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: remove_newlines(value) for key, value in obj.items()}
    return obj

def toJSON(df, path):
    # Convert DataFrame to JSON string
    json_data = df.to_json(orient="records", indent=2, force_ascii=False)
    json_data = json_data.replace(r"\n", "")
    # print(type(json_data))
    # Write JSON data to a file
    with open("output/" + path, "w", encoding="utf-8") as f:
        json.dump(json.loads(json_data), f, indent=2, ensure_ascii=False)

def createA(df, input_header_num, label=""):
    # input_header_numの数だけtoOneHeaderを繰り返す
    for _ in range(input_header_num):
        df = toOneHeader(df)
    toJSON(df, "JSON/A{0}.json".format(label))

def createB(dfs):
    i = 1
    for name, group in dfs:
        group = toOneHeader(group)
        toJSON(group, "tmp/{0}-{1}.json".format(i, name))
        i += 1
        
# JSONデータを読み込んだ後、ハイフンを入れ子構造に変換
def createC(data, label=""):
    result = []
    for item in data:
        nested_item = {}
        for key, value in item.items():
            parts = key.split('-')
            current = nested_item
            for part in parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]
            current[parts[-1]] = value
        result.append(nested_item)
    with open("output/JSON/C{}.json".format(label), "w") as file:
        json.dump(result, file, ensure_ascii=False, indent=2)


def multi_columns(df):
    if type(df.columns) is not pd.MultiIndex:
        return df

    # 列にUnnamedという文字の入った内容を削除しインデックスを振り直す
    df = df.rename(columns=lambda x: x if not 'Unnamed' in str(x) else '')
    print(df)
    df = df.reset_index()

    cols = df.columns
    copy_col = list(cols)

    # column.namesを新しいcolumnの一番上(インデックスセルの一番左)に持ってくる
    name_col = tuple([(name if name is not None else '') for name in cols.names])
    copy_col[0] = name_col

    # 無効セルは上に詰める
    for i, col in enumerate(copy_col):
        pack = [content for content in col if content != ""]
        copy_col[i] = tuple(pack + ([""] * (len(col)  - len(pack))))

    df.columns = pd.MultiIndex.from_tuples(copy_col)
    cols.names = tuple([None for x in cols.names])
    return df

# 合計行の処理というよりか、不要な行を削除できる機能
def deleteTotalRow(df):
    df = df.copy()
    total_row_name = input("合計を意味する行の最左列の名前を記入（例：総数）:")
    # 合計行があれば合計行を削除
    if total_row_name != "":
        df = df.drop(df[df.iloc[:, 0] == total_row_name].index)
    print(df, "消した後のdf")
    return df

def processTotalRow(df, total_row_info):
    df = df.copy()
    return df

def grouping(df):
    # 列名の最初のハイフン前の部分を抽出
    group_keys = df.columns.str.split('-').str[0]

    # 列をグループ分け
    grouped = df.groupby(group_keys, axis=1)

    # 各グループごとに列をまとめる
    result = {key: grouped.get_group(key) for key in grouped.groups}
    
    return result.items()

def createA_T(df):
    df.index = df.iloc[:, 0].tolist()
    data_for_transpose = df.iloc[:, 1:].values.tolist()
    primary_column = df.columns.values.tolist()[1:]
    df = pd.DataFrame(data_for_transpose, index=df.index, columns=df.columns[1:]).transpose()
    df = df.reset_index(drop=True)
    df.insert(0, "項目", primary_column)
    toJSON(df, "JSON/A-T.json")
    
def createC_T(original_data):
    result = {}
    
    for row in original_data:
        current_dict = result
        parts = row["項目"].split("-")

        for part in parts:
            if part.isdigit():
                part = int(part)
            current_dict = current_dict.setdefault(part, {})

        for key, value in row.items():
            if key != "項目":
                current_dict[key] = value

    # 結果を "C-T.json" に書き込み
    with open("output/JSON/C-T.json", "w", encoding="utf-8") as output_file:
        json.dump(result, output_file, ensure_ascii=False, indent=2)


df = pd.read_excel(
    excel_file_path,
    header=getHeaderList(input_header_num),
    dtype=columnToStr(input("文字列としたい数値が含まれる列があれば列番号を記入（例:1,2）：")),
)

df = multi_columns(df)

# MultiIndexから各要素を結合して新しいカラム名を生成
if type(df.columns) is pd.MultiIndex:
    df.columns = ['-'.join(filter(None, col)) for col in df.columns]
    
# 新しいカラム名をDataFrameに設定
data = df.values.tolist()
new_index_values = df.iloc[:, 0].tolist()
df = pd.DataFrame(data, columns=df.columns)

# 意味をなさない列を削除
df = df.drop(df.columns[0], axis=1)
# print(df, "dfやで")

createA(df, input_header_num)
createA(deleteTotalRow(df), input_header_num, "-NoTotal")
createA_T(df)

dfs = grouping(df)

with open("output/JSON/A.json", "r", encoding="utf-8") as file:
    A_json = json.load(file)
with open("output/JSON/A-T.json", "r", encoding="utf-8") as file:
    A_T_json = json.load(file)
with open("output/JSON/A-NoTotal.json", "r", encoding="utf-8") as file:
    A_deleteTotalRow_json = json.load(file)
    
createC(A_json)
createC(A_deleteTotalRow_json, "-NoTotal")
# createB_T(A_T_json)
createC_T(A_T_json)

#やったこと
# 1. A.json, C.jsonを作成
# 2. A-T.json, C-T.jsonを作成（行と列を入れ替えた）

#今後
# 1. B.jsonを作成
# 2. B-T.jsonを作成
# 3. 合計行の処理を、JSON上で行う（まず方法論見直し）
# 4. CSVファイルを読み込み、共通リソースの正規化を行う


    
# def transposedDfsToJSON(transposed_dfs):
#     count=0
    
#     for transposed_df in transposed_dfs:
#         if transposed_df.values.tolist()[0][0] == transposed_df.columns.values.tolist()[0]: # すなわち1行ヘッダーのカラムについて

#             toJSON(transposed_df, "JSON/tmp/A-T{}.json".format(count))
            
#             continue
#         else:
#             toJSON(transposed_df, "JSON/tmp/A-T{}.json".format(count))
#             count+=1
        
#     merged_data = []
#     for filename in os.listdir("output/JSON/tmp"):
#         if filename.endswith(".json"):
#             file_path = os.path.join("output/JSON/tmp", filename)
            
#             # 各JSONファイルを読み込んでリストに追加
#             with open(file_path, 'r') as file:
#                 json_data = json.load(file)
#                 merged_data.extend(json_data)
                
#     print(merged_data)
    
#     with open("output/JSON/A-T.json", "w", encoding="utf-8") as f:
#         json.dump(merged_data, f, indent=2, ensure_ascii=False)
        
# transposed_dfs = transposeDfs(dfs)
# transposedDfsToJSON(transposed_dfs)
