import pandas as pd
import json

excel_file_path = "input/input.xlsx"


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


def toJSON(df, path):
    # Convert DataFrame to JSON string
    json_data = df.to_json(orient="records", indent=2, force_ascii=False)

    # Write JSON data to a file
    with open("output/" + path, "w", encoding="utf-8") as f:
        json.dump(json.loads(json_data), f, indent=2, ensure_ascii=False)


def createA(df):
    #複数データに対応させる
    df = toOneHeader(df)
    toJSON(df, "A/A.json")


def createBC(dfs):
    i = 1
    for name, group in dfs:
        print(name)
        group = toOneHeader(group)
        toJSON(group, "{0}-{1}.json".format(i, name))
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
print(df_A)

createBC(dfs_BC)
