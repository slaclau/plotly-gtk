import json
import sys

codes_dict = {"DEP002": "Project should not contain unused dependencies"}

with open(sys.argv[1]) as f:
    data = json.load(f)
    if len(sys.argv) > 1:
        print(f"# {sys.argv[2]}")
    codes = list({d["error"]["code"] for d in data})
    for code in codes:
        if code in codes_dict:
            print(f"## {code}: {codes_dict[code]}")
        else:
            print(f"# {code}")
        modules = [d["module"] for d in data if d["error"]["code"] == code]
        for module in modules:
            print(module)
