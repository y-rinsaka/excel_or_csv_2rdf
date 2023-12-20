import pandas as pd
import json
import os

def read_input_file(file_path, header_num):
    """
    Read the input file and return a DataFrame.
    """
    if file_path.endswith((".xls", ".xlsx", ".csv")):
        if file_path.endswith((".xls", ".xlsx")):
            return pd.read_excel(f"input/{file_path}", header=[i for i in range(header_num)], dtype=columnToStr(input("文字列としたい数値が含まれる列があれば列番号を記入（例:1,2）：")),)
        else:
            return pd.read_csv(f"input/{file_path}", header=[i for i in range(header_num)], dtype=columnToStr(input("文字列としたい数値が含まれる列があれば列番号を記入（例:1,2）：")),)
    else:
        print("Invalid file extension.")
        exit()

def process_header(df):
    """
    Process the DataFrame headers by combining and formatting them.
    """
    new_columns = ['-'.join(column) if "" not in column else "".join(column) for column in df.columns]
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

def generate_json_file(json_data, path):
    # Convert DataFrame to JSON string
    with open("output/JSON/" + path, "w", encoding="utf-8") as f:
        json.dump(json_data, f, indent=2, ensure_ascii=False)

def createA(df, input_header_num):
    # input_header_numの数だけprocess_headerを繰り返す
    for _ in range(input_header_num):
        df = process_header(df)
    A_json = df.to_json(orient="records", indent=2, force_ascii=False)
    A_json = json.loads(A_json.replace(r"\n", ""))
    
    generate_json_file(A_json, "A.json")
    return A_json
        
# JSONデータを読み込んだ後、ハイフンを入れ子構造に変換
def createC(A_json):
    C_json = []
    for item in A_json:
        nested_item = {}
        for key, value in item.items():
            parts = key.split('-')
            current = nested_item
            for part in parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]
            current[parts[-1]] = value
        C_json.append(nested_item)
    generate_json_file(C_json, "C.json")
    return C_json

def createB(C_json):
    def transform_values(values):
        transformed_values = []
        count = 1
        for column, value in values.items():
            if isinstance(value, dict):
                # Recursive call for nested dictionaries
                transformed_values.append({"キー": column, "値": transform_values(value)})
            else:
                transformed_values.append({"キー": column, "値": value})
            count += 1
        return transformed_values

    B_json = []
    for entry in C_json:
        transformed_entry = {}
        for key, values in entry.items():
            if isinstance(values, dict):
                transformed_entry[key] = transform_values(values)
            else:
                transformed_entry[key] = values
        B_json.append(transformed_entry)
    generate_json_file(B_json, "B.json")
    return B_json


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

def grouping(df):
    # 列名の最初のハイフン前の部分を抽出
    group_keys = df.columns.str.split('-').str[0]

    # 列をグループ分け
    grouped = df.groupby(group_keys, axis=1)

    # 各グループごとに列をまとめる
    result = {key: grouped.get_group(key) for key in grouped.groups}
    
    return result.items()

def createA_T(df, input_header_num):
    for _ in range(input_header_num):
        df = process_header(df)
    df.index = df.iloc[:, 0].tolist()
    data_for_transpose = df.iloc[:, 1:].values.tolist()
    primary_column = df.columns.values.tolist()[1:]
    df = pd.DataFrame(data_for_transpose, index=df.index, columns=df.columns[1:]).transpose()
    df = df.reset_index(drop=True)
    df.insert(0, "項目", primary_column)
    A_T_json = df.to_json(orient="records", indent=2, force_ascii=False)
    A_T_json = json.loads(A_T_json.replace(r"\n", ""))
    generate_json_file(A_T_json, "A-Transposed.json")
    return A_T_json

def createC_T(A_T_json):
    C_T_json = {}
    
    for row in A_T_json:
        current_dict = C_T_json
        parts = row["項目"].split("-")

        for part in parts:
            if part.isdigit():
                part = int(part)
            current_dict = current_dict.setdefault(part, {})

        for key, value in row.items():
            if key != "項目":
                current_dict[key] = value
    generate_json_file(C_T_json, "C-Transposed.json")
    return C_T_json

def createB_T(C_T_json):
    def createB_T_recursive(values):
        transformed_values = []
        for key, value in values.items():
            if isinstance(value, dict):
                # Recursive call for nested dictionaries
                transformed_values.append({"キー": key, "値": createB_T_recursive(value)})
            else:
                transformed_values.append({"キー": key, "値": value})
        return transformed_values
    
    B_T_json = createB_T_recursive(C_T_json)
    generate_json_file(B_T_json, "B-Transpo.json")
    return B_T_json


def main():
    input_file_path = "input_3h.xlsx" # Excelファイルのパスを指定
    input_header_num = 3 # ヘッダーの行数を指定
    is_transpose_required = True # 行と列を入れ替える構造を出力するかどうかを指定
    is_total_row_existing = False # 合計行があるかどうかを指定
    
    df = read_input_file(input_file_path, input_header_num)
        
    if input_header_num != 1:
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
    
    A_json = createA(df, input_header_num)
    C_json = createC(A_json)
    B_json = createB(C_json)
    
    if is_transpose_required:
        A_T_json = createA_T(df, input_header_num)
        C_T_json = createC_T(A_T_json)
        B_T_json = createB_T(C_T_json)

if __name__ == "__main__":
    main()