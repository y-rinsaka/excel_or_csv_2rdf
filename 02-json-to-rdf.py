import json
import os

def json_to_rdf(json_data, prefix_map):
    rdf_text = ""
    rdf_text += "@prefix ex: {} .\n".format(prefix_map["ex"])
    rdf_text += "[\n"

    def serialize_value(value):
        if value is None:
            return ""
        elif isinstance(value, str):
            return '"{}"'.format(value)
        else:
            return value

    for i, entry in enumerate(json_data, start=1):
        if isinstance(entry, dict):
            rdf_text += "  ex:{} [".format(i)
            rdf_text += "\n"

            for key, value in entry.items():
                if isinstance(value, dict):
                    rdf_text = dict_value_to_rdf(key, value, rdf_text, 2)
                elif isinstance(value, list):
                    for dvalue_in_li in value:
                        if isinstance(dvalue_in_li, dict):
                            rdf_text = dict_value_to_rdf(key, dvalue_in_li, rdf_text, 2)
                        else:
                            print("error")
                else:
                    rdf_text += '    ex:{} {};\n'.format(key, serialize_value(value))
            rdf_text += "  ] ;\n\n"
        elif isinstance(entry, str):
            entry_value = json_data[entry]
            rdf_text += "  ex:{} [\n".format(entry)

            for key, value in entry_value.items():
                if isinstance(value, dict):
                    rdf_text = dict_value_to_rdf(key, value, rdf_text, 2)
                else:
                    rdf_text += '    ex:{} {};\n'.format(key, serialize_value(value))
            rdf_text += "  ] ;\n\n"
        else:
            print("error: {} is neither a string nor a dictionary".format(entry))

    rdf_text += "] .\n"

    return rdf_text

def dict_value_to_rdf(key, value, rdf_text, depth):
    indent = "  " * depth
    rdf_text += indent + "ex:{} [\n".format(key)
    for sub_key, sub_value in value.items():
        if isinstance(sub_value, dict):
            rdf_text = dict_value_to_rdf(sub_key, sub_value, rdf_text, depth + 1)
        else:
            rdf_text += indent + '  ex:{} {};\n'.format(sub_key, serialize_value(sub_value))
    rdf_text += indent + "] ;\n"
    return rdf_text

def serialize_value(value):
    if value is None:
        return '"-"'
    elif isinstance(value, str):
        return '"{}"'.format(value)
    else:
        return value

def list_json_files(directory):
    json_files = [f for f in os.listdir(directory) if f.endswith('.json')]
    return json_files

def main():
    # RDF Turtle形式のプレフィックス定義
    rdf_prefixes = {
        "ex": "<http://example.org/>",
        "rdf": "<http://www.w3.org/1999/02/22-rdf-syntax-ns#>",
    }
    json_file_names = list_json_files("output/JSON")
    print(json_file_names)
    # jsonファイルの読み込み

    for file_name in json_file_names:
        with open("output/JSON/{}".format(file_name), "r", encoding="utf-8") as json_file:
            input_data = json.load(json_file)

        # RDFデータ生成
        rdf_text = json_to_rdf(input_data, rdf_prefixes)

        with open("output/RDF/{}.ttl".format(file_name.replace('.json', '')), "w") as file:
            file.write(rdf_text)

if __name__ == '__main__':
    main()