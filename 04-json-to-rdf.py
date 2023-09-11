import json

def jsonToRDF(json_data, parent_key=""):
    rdf_text = ""

    for data in json_data:
        rdf_text += "[\n"
        for key, value in data.items():
            full_key = f"{parent_key}:{key}" if parent_key else key

            if isinstance(value, dict):
                rdf_text += jsonToRDF([value], full_key)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        rdf_text += jsonToRDF([item], full_key)
            elif isinstance(value, str):
                rdf_text += f'{full_key} "{value}" ;\n'
            else:
                rdf_text += f"{full_key} {value} ;\n"

        rdf_text = rdf_text.rstrip(";\n") + "\n"
        rdf_text += "] .\n"

    return rdf_text

# JSONファイルを読み込む
input_json = "B/B.json"
with open("output/" + input_json, "r") as file:
    json_data = json.load(file)
rdf_data = jsonToRDF(json_data)

# プレフィックスを追加
rdf_data = f"@prefix : <http://purl.org/net/ns/jsonrdf/> .\n{rdf_data}"
with open("output/RDF/B.txt", "w") as file:
    file.write(rdf_data)
