import json

# RDF Turtle形式のプレフィックス定義
rdf_prefixes = {
    "": "<http://purl.org/net/ns/jsonrdf/>",
    "rdf": "<http://www.w3.org/1999/02/22-rdf-syntax-ns#>",
}

def json_to_rdf(json_data, base_uri, prefix_map):
    rdf_text = ""
    rdf_text += "@prefix : {} .\n".format(prefix_map[""])
    rdf_text += "@prefix rdf: {} .\n\n".format(prefix_map["rdf"])

    for i, entry in enumerate(json_data, start=1):
        rdf_text += ":rdf_{} ".format(i)
        rdf_text += "\n"
        for key, value in entry.items():
            if isinstance(value, dict):
                rdf_text = dict_value_to_rdf(key, value, rdf_text)
            
            elif isinstance(value, list):
                for dvalue_in_li in value:
                    if isinstance(dvalue_in_li, dict):
                        rdf_text = dict_value_to_rdf(key, dvalue_in_li, rdf_text)
                    else:
                        print("error")
                
            else:
                rdf_text += '  :{} "{}";\n'.format(key, value)
        rdf_text += " .\n\n"

    return rdf_text

def dict_value_to_rdf(key, value, rdf_text):
    rdf_text += "  :{} [\n".format(key)
    for sub_key, sub_value in value.items():
        rdf_text += '    :{} "{}";\n'.format(sub_key, sub_value)
    rdf_text += "  ];\n"
    return rdf_text
  


#jsonファイルの読み込み
json_file_names = ["A", "B", "C"]
for file_name in json_file_names:
    with open("output/{0}/{0}.json".format(file_name), "r", encoding="utf-8") as json_file:
        input_data = json.load(json_file)

    # RDFデータ生成
    base_uri = "http://example.org/"
    rdf_text = json_to_rdf(input_data, base_uri, rdf_prefixes)

    with open("output/RDF/{0}.txt".format(file_name), "w") as file:
        file.write(rdf_text)