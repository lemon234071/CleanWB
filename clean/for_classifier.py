import os
import jieba
import random
from tqdm import tqdm
import pandas as pd
from utils import *

random.seed(2019)


def process_infer(path, outpath):
    data = load_json(path)
    new_data = []
    for dialog in tqdm(data, mininterval=2):
        line = ["0\t", " ; ".join(dialog), "\n"]
        new_data.extend(line)
    data_out = "".join(new_data)
    save_txt(data_out, outpath)


def process_infer_multi(path, outpath, infer=True):
    new_data = []
    label = 0
    data = load_json(path)
    for j, dialog in enumerate(tqdm(data, mininterval=2)):
        for i in range(len(dialog) - 1):
            line = [str(label), "\t", dialog[i], " ; ", dialog[i + 1], "\n"]
            new_data.extend(line)
        label = 1 - label if infer else label + 1
    data_out = "".join(new_data)
    save_txt(data_out, outpath)


def process_context(path, outpath):
    data = load_json(path)
    new_data = []
    for dialog in tqdm(data, mininterval=2):
        line = ["0\t", dialog[0], "\n"]
        new_data.extend(line)
    data_out = "".join(new_data)

    save_txt(data_out, outpath)


def process_context_multi(path, outpath):
    data = load_json(path)
    new_data = []
    k = 0
    for dialog in tqdm(data, mininterval=2):
        for seq in dialog:

            line = [k, "\t", seq, "\n"]
            new_data.extend(line)
        k = 1 - k
    data_out = "".join(new_data)
    save_txt(data_out, outpath)


def post_cls_single(data_path, dir_temp, out_path):
    #clean_label_path = dir + "more_single_cleanfor_clean_labels.json"
    # clean_label_bad_path = dir + "single_clean_clsfor_clean_filter0.json"
    #context_label_path = dir + "more_single_contextfor_context_labels.json"
    # context_bad_label_path = dir + "more_single_contextfor_context_bad.json"

    clean_label_path = dir_temp + "single_cleanfor_clean_labels.json"
    context_label_path = dir_temp + "single_contextfor_context_labels.json"
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
    #save_json(out, dir + "good_single.json")
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
    data = load_json(data_path)
    assert len(data) == len(out)
    new_data = []
    for i, dialog in enumerate(data):
        if out[i]:
            new_data.append(dialog)
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
    #save_json(good_lable, dir + "good_multi.json")
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
                        index_list.append([dialog_index, start-dialog_start, start-dialog_start+conut]) # [dialog_start, start, start + conut]
                    start = i
                    conut = 1
            else:
                if conut > 1:
                    index_list.append([dialog_index, start-dialog_start, start-dialog_start+conut])
                start = i
                conut = 1
                dialog_start = i
                dialog_index += 1
        else:
            if conut > 1:
                index_list.append([dialog_index, start-dialog_start, start-dialog_start+conut])
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
    # dir = "/home/wangyida/data_wash/data/v2/cls/labels/"
    # post_cls_single(dir)
    # original_path = "/home/wangyida/data_wash/data/v2/cls/raw/multi_clean_cls.txt"
    # post_cls_multi(dir, original_path)

    # dir = "/home/wangyida/data_wash/data/v2/cls/more_lables/"
    # post_cls_single(dir)
    # path = "/home/wangyida/data_wash/data/v2/from_dirty/more_multi.json"
    # outpath = "/home/wangyida/data_wash/data/v2/cls/more_lables/more_multi_clean_cls.txt"
    # process_infer_multi(path, outpath, False)
    # original_path = "/home/wangyida/data_wash/data/v2/cls/more_lables/more_multi_clean_cls.txt"
    # post_cls_multi(dir, original_path)
    # merge_more()
    #post_cls_single("/home/wangyida/data/stc/cls/")

    # process_infer("/home/wangyida/data_wash/data/v3/output/after_rules/single_after_rules.json",
    #               "/home/wangyida/data_wash/data/v3/output/cls/single_clean.json")
    # process_infer_multi("/home/wangyida/data_wash/data/v3/output/after_rules/multi_after_rules.json",
    #               "/home/wangyida/data_wash/data/v3/output/cls/multi_clean.json")
    # process_context("/home/wangyida/data_wash/data/v3/output/after_rules/single_after_rules.json",
    #               "/home/wangyida/data_wash/data/v3/output/cls/single_context.json")
    # process_context("/home/wangyida/data_wash/data/v3/output/after_rules/multi_after_rules.json",
    #               "/home/wangyida/data_wash/data/v3/output/cls/multi_context.json")
    ############################################################################################
    # post_clean_multi("", "./")
    # post_clean_multi("/home/wangyida/data_wash/data/v3/output/after_rules/multi_after_rules.json",
    #                "/home/wangyida/data_wash/data/v3/output/cls/")
    # process_context_multi("/home/wangyida/data_wash/data/v3/output/cls/multi_after_clean_data.json",
    #               "/home/wangyida/data_wash/data/v3/output/cls/multi_after_clean_data_context.json")
    ###########################################################################
    # post_cls_single("/home/wangyida/data_wash/data/v3/output/after_rules/single_after_rules.json",
    #                 "/home/wangyida/data_wash/data/v3/output/cls/",
    #                 "/home/wangyida/data_wash/data/v3/output/single_final_v1.json")
    post_cls_multi_before("/home/wangyida/data_wash/data/v3/output/after_rules/multi_after_rules.json",
                          "/home/wangyida/data_wash/data/v3/output/cls/",
                          "/home/wangyida/data_wash/data/v3/output/multi_final_v1.json")


    print(1)


if __name__ == '__main__':
    main()
