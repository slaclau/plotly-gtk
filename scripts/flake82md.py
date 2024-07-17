import json
import sys

with open(sys.argv[1]) as f:
    data = json.load(f)
    if len(sys.argv) > 1:
        print(f"# {sys.argv[2]}")
    n = 0
    errors = {}
    for i in data:
        n += len(data[i])
        errors[i] = len(data[i])
    print(f"{len(data)} files checked, {n} issues found")
    print("| File | Issues |")
    print("| - | - |")
    for i in errors:
        print(f"| {i.replace("_", "\_")} | {errors[i]} |")
    for i in data:
        if len(data[i]) > 0:
            print(f"## {i.replace("_", "\_")}:")
            print(f"{len(data[i])} issues found")
            print("The following code(s) occurred in this file")
            print("| Occurences | Code | Meaning |")
            print("| - | - | - |")
            codes = sorted(set(d["code"] for d in data[i]))
            codeCount = {}
            codeText = {}
            for line in data[i]:
                codeCount[line["code"]] = codeCount.get(line["code"], 0) + 1
                codeText[line["code"]] = line["text"]
            for code in codes:
                print(f"| {codeCount[code]} | {code} | {codeText[code]} |")
            print()
            count = 0
            for line in data[i]:
                count += 1
                print(
                    f'{line["code"]}:{line["line_number"]}:{line["column_number"]}: {line["text"]}'
                )
                print("```python")
                if line["physical_line"] is not None:
                    print(line["physical_line"].strip())
                print("```")
                if count > 100:
                    print(f"Truncated at {count} errors")
                    break
