import json
import sys

with open(sys.argv[1]) as f:
    data = json.load(f)
    if len(sys.argv) > 1:
        print(f"# {sys.argv[2]}")
    n = 0
    for i in data:
        for line in data[i]:
            n += data[i][line]
    print(f"{len(data)} files checked, {n} issues found")
    for i in data:
        print(f"## {i}")
        print("| Occurrences | Message |")
        print("| - | - |")
        for line in data[i]:
            print(f"| {data[i][line]} | {line} |")
        print()
