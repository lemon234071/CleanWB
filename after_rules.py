import os
import collections
from utils import *


def data_merge(dir):
    pathes = [dir + name for name in os.listdir(dir)]
    data = []
    for path in pathes:
        dataset = load_json(path)
        data.extend(dataset)
    print("dialogs len:", len(data))
    temp = set(["[SEP]".join(x) for x in data])
    data = [x.strip().split("[SEP]") for x in temp]
    print("unique dialogs num", len(data))
    #save_json(data, outpath)
    return data


def de_same_post_resp(path, outpath):
    data = load_json(path)
    print(len(data))
    new_data = []
    dupl = []
    for dialog in data:
        dupl_set = set()
        for i, seq in enumerate(dialog):
            dupl_set.add(seq)
        if len(dupl_set) < 2:
            dupl.append(dialog)
            continue
        elif len(dupl_set) < 3 and len(dialog) > 4:
            dupl.append(dialog)
            continue
        new_data.append(dialog)

    save_json(dupl, outpath.replace(".json", "_dupl.json"))
    save_json(new_data, outpath)
    print(len(new_data))


def de_ad(data, outpath, ad_path):
    resp_dict = collections.defaultdict(set)
    for dialog in data:
        for i in range(len(dialog)):
            if i < 1:
                continue
            resp_dict[dialog[i]].add(dialog[i-1])
    ad_resp_dict = {}
    for k, v in resp_dict.items():
        if len(k.replace(" ", "")) > 20 and len(v) > 2:
            ad_resp_dict[k] = len(v)
    ad_resp = sorted(ad_resp_dict.items(), key=lambda x: x[1], reverse=True)
    save_json(ad_resp, ad_path)
    print("ad len", len(ad_resp))

    resp_set = set(ad_resp_dict.keys())
    new_data = []
    for dialog in data:
        if len(dialog) > 2:
            start = 0
            for i in range(len(dialog)):
                if i < 1:
                    continue
                if dialog[i] in resp_set:
                    if i-start > 2:
                        new_data.append(dialog[start:i])
                        start = i+1
            if (len(dialog) - start) > 2:
                new_data.append(dialog[start:])
        else:
            if dialog[-1] not in resp_set:
                new_data.append(dialog)
    save_json(new_data, outpath)
    print("data len :", len(new_data))


def main():
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument("--data_dir", type=str, default="./data/", help="Dir of the dataset.")
    parser.add_argument("--out_path", type=str, default="./data/cleaned_data/", help="Path of the output.")
    parser.add_argument("--ad_path", type=str, default="./data/dirty_data/", help="Path of the ad cases.")
    args = parser.parse_args()

    data = data_merge(args.data_dir)
    de_ad(data, args.out_path, args.ad_path)

    print("after rules over")


if __name__ == '__main__':
    main()
