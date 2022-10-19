from aijson.build import build

import json

with open('mymodel.ai.json') as f:
    cf = json.load(f)

out = build(cf)

print(out)
print(out.__dict__)