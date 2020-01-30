import os
import jieba
import random
from tqdm import tqdm
import pandas as pd
import collections

from utils import *

random.seed(2019)


def single_clean(data, outpath):
    #data = load_json(path)
    new_data = []
    for dialog in tqdm(data, mininterval=2):
        line = ["0\t", " ; ".join(dialog), "\n"]
        new_data.extend(line)
    data_out = "".join(new_data)
    save_txt(data_out, outpath)


def single_context(data, outpath):
    # data = load_json(path)
    new_data = []
    for dialog in tqdm(data, mininterval=2):
        line = ["0\t", dialog[0], "\n"]
        new_data.extend(line)
    data_out = "".join(new_data)

    save_txt(data_out, outpath)


def post_single(data, dir_temp, out_path):
    # clean_label_path = dir + "more_single_cleanfor_clean_labels.json"
    # clean_label_bad_path = dir + "single_clean_clsfor_clean_filter0.json"
    # context_label_path = dir + "more_single_contextfor_context_labels.json"
    # context_bad_label_path = dir + "more_single_contextfor_context_bad.json"

    clean_label_path = dir_temp + "single_clean_clean_0.5.json"
    context_label_path = dir_temp + "single_context_context_labels.json"
    clean_label = load_json(clean_label_path)
    # clean_label_bad = load_json(clean_label_bad_path)
    context_label = load_json(context_label_path)
    # context_bad_label_raw = load_json(context_bad_label_path)
    context_bad_label = []
    # for x in context_bad_label_raw:
    #     context_bad_label.extend(x)
    out = []
    for i in range(len(clean_label)):
        if clean_label[i] and not context_label[i]:
            out.append(1)
        else:
            out.append(0)
    # save_json(out, dir + "good_single.json")
    print(len(out))
    print(sum(out))

    # out_bad = []
    # for i in range(len(clean_label_bad)):
    #     if clean_label_bad[i] and not context_bad_label[i]:
    #         out_bad.append(1)
    #     else:
    #         out_bad.append(0)
    # print(sum(out_bad))
    # save_json(out_bad, dir + "bad.json")
    # data = load_json(data_path)
    assert len(data) == len(out)
    new_data = []
    for i, dialog in enumerate(data):
        if out[i]:
            new_data.append(dialog)
    print(len(new_data))
    save_json(new_data, out_path)


def multi_clen(data, outpath):
    new_data = []
    label = 0
    # data = load_json(path)
    for j, dialog in enumerate(tqdm(data, mininterval=2)):
        for i in range(len(dialog)-1):
            line = [str(label), "\t", dialog[i], " ; ", dialog[i + 1], "\n"]
            new_data.extend(line)
        label = 1 - label
    data_out = "".join(new_data)
    save_txt(data_out, outpath)
    print("multi clean len:", len(new_data))


def multi_context(data, outpath):
    #data = load_json(path)
    new_data = []
    k = 0
    for dialog in tqdm(data, mininterval=2):
        for i in range(len(dialog)-1):
            line = [str(k), "\t", dialog[i], "\n"]
            new_data.extend(line)
        k = 1 - k
    data_out = "".join(new_data)
    save_txt(data_out, outpath)
    print("multi context len:", len(new_data))


def post_multi(data, dir_temp, out_path):
    clean_label_path = dir_temp + "multi_clean_clean_labels.json"
    # clean_label_bad_path = dir + "multi_clean_clsfor_clean_filter0.json"
    context_label_path = dir_temp + "multi_context_context_labels.json"
    # context_bad_label_path = dir + "multi_context_clsfor_context_bad.json"
    clean_label = load_json(clean_label_path)
    # clean_label_bad = load_json(clean_label_bad_path)
    context_label = load_json(context_label_path)
    # context_bad_label_raw = load_json(context_bad_label_path)
    # context_bad_label = []
    # for x in context_bad_label_raw:
    #     context_bad_label.extend(x)

    multi_clean = load_txt(dir_temp + "multi_clean.txt")
    # dialog_index = load_json(dir_temp + "dialog_index.json")
    assert len(clean_label) == len(multi_clean) == len(context_label)
    labels = collections.defaultdict(list)
    new_clean_label = []
    new_context_label = []
    last_label = 0
    for i in range(len(multi_clean)):
        label = int(multi_clean[i].strip().split("\t")[0])
        if label != last_label:
            labels["clean"].append(new_clean_label)
            labels["context"].append(new_context_label)
            new_clean_label = []
            new_context_label = []
        new_clean_label.append(clean_label[i])
        new_context_label.append(context_label[i])
        last_label = label
    labels["clean"].append(new_clean_label)
    labels["context"].append(new_context_label)

    assert len(data) == len(labels["clean"]) == len(labels["context"])
    # data = load_json(data_path)
    new_data = []
    for i, dialog in enumerate(data):
        assert len(dialog) - 1 == len(labels["context"][i]) == len(labels["clean"][i])
        start = 0
        while labels["context"][i][start] or not labels["clean"][i][start]:  # context label 0 is good
            start += 1
            if start > len(dialog)-2:
                break
        j = start
        while j < len(dialog)-1:
            if labels["clean"][i][j]:
                j += 1
            else:
                if len(dialog[start:j+1]) > 1:
                    new_data.append(dialog[start:j+1])
                start = j + 1
                if start > len(dialog)-2:
                    break
                while labels["context"][i][start] or not labels["clean"][i][start]:  # context label 0 is good
                    start += 1
                    if start > len(dialog) - 2:
                        break
                j = start

        if len(dialog[start:j+1]) > 1:
            new_data.append(dialog[start:j+1])
        # print(labels["context"][i], labels["clean"][i])
        # print(new_data)
        # import pdb
        # pdb.set_trace()

    print(len(new_data))
    save_json(new_data, out_path)


def post_cls_multi_before(data_path, dir_temp, out_path):
    clean_label_path = dir_temp + "multi_cleanfor_clean_labels.json"
    # clean_label_bad_path = dir + "multi_clean_clsfor_clean_filter0.json"
    context_label_path = dir_temp + "multi_contextfor_context_labels.json"
    # context_bad_label_path = dir + "multi_context_clsfor_context_bad.json"
    clean_label = load_json(clean_label_path)
    # clean_label_bad = load_json(clean_label_bad_path)
    context_label = load_json(context_label_path)
    # context_bad_label_raw = load_json(context_bad_label_path)
    # context_bad_label = []
    # for x in context_bad_label_raw:
    #     context_bad_label.extend(x)

    labels = load_txt(dir_temp + "multi_clean.json")
    assert len(clean_label) == len(labels)
    last_label = 0
    final_label = []
    count = 0
    clean = 0
    for i in range(len(labels)):
        label = int(labels[i].strip().split("\t")[0])
        if label == last_label:
            count += 1
            if clean_label[i]:
                clean += 1
        else:
            if clean > count / 2:
                final_label.append(1)
            else:
                final_label.append(0)
            count = 1
            if clean_label[i]:
                clean = 1
            last_label = label
    if clean > count / 2:
        final_label.append(1)
    else:
        final_label.append(0)

    assert len(final_label) == len(context_label)
    good_lable = []
    for i in range(len(final_label)):
        if final_label[i] and not context_label[i]:
            good_lable.append(1)
        else:
            good_lable.append(0)
    # save_json(good_lable, dir + "good_multi.json")
    print(len(good_lable))
    print(sum(good_lable))

    data = load_json(data_path)
    new_data = []
    for i, dialog in enumerate(data):
        if good_lable[i]:
            new_data.append(dialog)
    print(len(new_data))
    save_json(new_data, out_path)


def post_clean_multi(data_path, dir_temp):
    labels = load_txt(dir_temp + "multi_clean.json")
    clean_label = load_json(dir_temp + "multi_cleanfor_clean_labels.json")
    last_label = 0
    index_list = []

    last_clean = False
    conut = 0
    start = 0
    dialog_start = 0
    dialog_index = -1
    for i in range(len(labels)):
        label = int(labels[i].strip().split("\t")[0])
        if clean_label[i] == True:
            if label == last_label:
                if clean_label[i] == last_clean:
                    conut += 1
                else:
                    if conut > 1:
                        index_list.append([dialog_index, start - dialog_start,
                                           start - dialog_start + conut])  # [dialog_start, start, start + conut]
                    start = i
                    conut = 1
            else:
                if conut > 1:
                    index_list.append([dialog_index, start - dialog_start, start - dialog_start + conut])
                start = i
                conut = 1
                dialog_start = i
                dialog_index += 1
        else:
            if conut > 1:
                index_list.append([dialog_index, start - dialog_start, start - dialog_start + conut])
            start = i
            conut = 1
            if label != last_label:
                dialog_start = i
                dialog_index += 1
        last_label = label
        last_clean = clean_label[i]

    data = load_json(data_path)
    print(len(data))
    new_data = []
    for indece in index_list:
        start = indece[1]
        end = indece[2] + 1
        assert (end - start) > 2
        k = indece[0]
        new_data.append(data[k][start:end])
    print(len(new_data))
    save_json(new_data, dir_temp + "multi_after_clean_data.json")


# def post_cls_multi(data_path, label_path, out_path):
#     data = load_json(data_path)
#     labels = load_json(label_path)
#     new_data = []
#     for dialog in data:
#
#     save_json(new_data, out_path)


def merge_more():
    single_path = "/home/wangyida/data_wash/data/v2/cls/labels/good.json"
    multi_path = "/home/wangyida/data_wash/data/v2/cls/labels/multi_good.json"
    single_more_path = "/home/wangyida/data_wash/data/v2/cls/more_lables/good.json"
    multi_more_path = "/home/wangyida/data_wash/data/v2/cls/more_lables/multi_good.json"
    single_label = load_json(single_path)
    more_single_label = load_json(single_more_path)
    multi_label = load_json(multi_path)
    multi_more_label = load_json(multi_more_path)
    single_data_path = "/home/wangyida/data_wash/data/v2/single_after_rule.json"
    multi_data_path = "/home/wangyida/data_wash/data/v2/multi_after_rule_v2.json"
    single = load_json(single_data_path)
    multi = load_json(multi_data_path)
    assert len(single) == len(single_label)
    assert len(multi) == len(multi_label)
    single_out = []
    multi_out = []
    for i in range(len(single)):
        if single_label[i]:
            single_out.append(single[i])
    for i in range(len(multi)):
        if multi_label[i]:
            multi_out.append(multi[i])
    more_single_data = "/home/wangyida/data_wash/data/v2/from_dirty/more_single.json"
    multi_more_data = "/home/wangyida/data_wash/data/v2/from_dirty/more_multi.json"
    more_single = load_json(more_single_data)
    multi_more = load_json(multi_more_data)
    assert len(more_single) == len(more_single_label)
    assert len(multi_more) == len(multi_more_label)
    for i in range(len(more_single)):
        if more_single_label[i]:
            single_out.append(more_single[i])
    for i in range(len(multi_more)):
        if multi_more_label[i]:
            multi_out.append(multi_more[i])
    print(len(single_out))
    print(len(multi_out))
    save_json(single_out, "/home/wangyida/data_wash/data/v2/single_after_cls.json")
    save_json(multi_out, "/home/wangyida/data_wash/data/v2/multi_after_cls.json")


def main():
    # data = load_json("/home/wangyida/git/temp/CleanWB/data/after_rules.json")
    # print(len(data), "len all")
    # single = [dialog for dialog in data if len(dialog) < 3]
    # multi = [dialog for dialog in data if len(dialog) > 2]
    # print(len(single), "len single")
    # print(len(multi), "len multi")
    # #
    # # single_clean(single, "../data/cls/single_clean.txt")
    # # single_context(single, "../data/cls/single_context.txt")
    # # multi_clen(multi, "../data/cls/multi_clean.txt")
    # # multi_context(multi, "../data/cls/multi_context.txt")
    # post_single(single,
    #             "/home/wangyida/git/temp/CleanWB/data/cls/",
    #             "/home/wangyida/git/temp/CleanWB/data/single_cls.json")
    # post_multi(multi,
    #            "/home/wangyida/git/temp/CleanWB/data/cls/",
    #            "/home/wangyida/git/temp/CleanWB/data/multi_cls.json")

    single = load_json("/home/wangyida/211/v3/after_rules/single_after_rules.json")
    # single_clean(single, "../data/cls_WB/single_clean.txt")
    # single_context(single, "../data/cls_WB/single_context.txt")
    print(len(single), "len single")
    post_single(single,
                "../data/cls_WB/",
                "/home/wangyida/git/temp/CleanWB/data/single_cls_WB.json")

    # multi = load_json("/home/wangyida/211/v3/after_rules/multi_after_rules.json")
    #
    # # multi_clen(multi, "../data/cls_WB/multi_clean.txt")
    # # multi_context(multi, "../data/cls_WB/multi_context.txt")
    # print(len(multi), "len multi")
    # post_multi(multi,
    #            "../data/cls_WB/",
    #            "/home/wangyida/git/temp/CleanWB/data/multi_cls_WB.json")

    print(1)


if __name__ == '__main__':
    main()
