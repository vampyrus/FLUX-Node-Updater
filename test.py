import json

file = open(f"update_times.json", "r")
json_obj = json.loads(file.read())
file.close()
json_obj["cumulus01"] = "hi"
print(json_obj)
file = open(f"update_times.json", "w")
file.write(json.dumps(json_obj, indent=4))
file.close()
