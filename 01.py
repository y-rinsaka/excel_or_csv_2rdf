import pandas as pd
import json

excel_file_path = "input/01.xls"


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

def columnToStr(input_column_nums):
    column_str = {}
    if input_column_nums == "":
        return column_str

    selected_nums = input_column_nums.split(",")
    for i in selected_nums:
        column_str[int(i)] = "str"
    return column_str

# JSONデータ内の改行文字を除去する関数
def remove_newlines(obj):
    if isinstance(obj, str):
        return obj.replace('\n', ' ')
    elif isinstance(obj, list):
        return [remove_newlines(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: remove_newlines(value) for key, value in obj.items()}
    print(obj)
    return obj

    
def toJSON(df, path):
    # Convert DataFrame to JSON string
    json_data = df.to_json(orient="records", indent=2, force_ascii=False)
    json_data = json_data.replace(r"\n", "")
    print(type(json_data))
    # Write JSON data to a file
    with open("output/" + path, "w", encoding="utf-8") as f:
        json.dump(json.loads(json_data), f, indent=2, ensure_ascii=False)


def createA(df):
    #複数データに対応させる
    df = toOneHeader(df)
    toJSON(df, "JSON/A.json")


def createBC(dfs):
    i = 1
    for name, group in dfs:
        group = toOneHeader(group)
        toJSON(group, "tmp/{0}-{1}.json".format(i, name))
        i += 1


input_df = pd.read_excel(
    excel_file_path,
    header=[0, 1],
    dtype=columnToStr(input("文字列としたい数値が含まれる列があれば選択（例:1,2）：")),
)

input_df = input_df.rename(columns=lambda x: x if not "Unnamed" in str(x) else "")
df_A = input_df
dfs_BC = input_df.groupby(level=0, axis=1)
createA(df_A)

createBC(dfs_BC)
