from utils import *
import os
import json


data = []
for path in ["./" + name for name in os.listdir("./data/dirty/black/")]:
    with open(path, "r", encoding="utf-8") as f:
        one = json.load(f)
        data.append(one)

cnt = {}
for one in data:
    for k, v in one.items():
        if k not in cnt:
            cnt[k] = len(v)
        else:
            cnt[k] += len(v)
sorted(cnt.items(), key=lambda x: x[1], reverse=True)
save_json(cnt, "./data/dirty/cnt_black.json")

