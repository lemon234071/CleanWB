import os
import jieba

from utils import *
from clean.filter import BLACK_LIST, BLACK_STR


def dataloader(dir_path):
    json_path_list = [dir_path + name for name in os.listdir(dir_path)]
    txt_path_list = [dir_path + name for name in os.listdir(dir_path)]

    simple_loader = []
    for path in json_path_list:
        simple_loader.append((load_json, path))
    for path in txt_path_list:
        simple_loader.append((load_txt, path))

    return simple_loader


def temp_dataloader():
    json_path_list = ['/home/wangyida/data_wash/data/v2/from_dirty/' + name
                      for name in os.listdir('/home/wangyida/data_wash/data/v2/from_dirty/')]

    simple_loader = []
    for path in json_path_list:
        simple_loader.append((jsondata_loader, path))

    return simple_loader


# def stc_dataloader():
#     # data = load_json('/home/wangyida/data/stc/stc_weibo_train_data')
#     # new_data = []
#     # for dialog in tqdm(data, mininterval=2):
#     #     for resp in dialog[1]:
#     #         post = dialog[0].strip().replace(" ", "")
#     #         post = jieba.lcut(post)
#     #         resp = resp.strip().replace(" ", "")
#     #         resp = jieba.lcut(resp)
#     #         new_data.append([" ".join(post), " ".join(resp)])
#     # save_json(new_data, '/home/wangyida/data/stc/stc.json')
#     # del new_data, data
#
#     json_path_list = ['/home/wangyida/data/stc/result/v2/cls/our_cleaned-gen.json']
#     simple_loader = []
#     for path in json_path_list:
#         simple_loader.append((jsondata_loader, path))
#
#     return simple_loader


def jsondata_loader(path):
    return load_json(path)


def txtdata_loader(path):
    data = []
    if path[path.rindex("."):] == '.data':
        raw = load_txt(path)
        temp = []
        for line in raw:
            if line:
                line = jieba.lcut(line)
                temp.append(line)
            else:
                if temp:
                    data.append(temp)
                    temp = []
        del raw
    elif path[path.rindex("."):] == '.post':
        post = load_txt(path)
        res_path = path[:path.rindex(".")] + '.response'
        reponse = load_txt(res_path)
        assert len(post) == len(reponse)
        for i, src in enumerate(post):
            if src and reponse[i]:
                src = jieba.lcut(src)
                tgt = jieba.lcut(reponse[i])
                data.append([src, tgt])
        del post, reponse
    return data


def get_filter_set(tool_path):
    person_name = set(load_txt(os.path.join(tool_path, "ALL_name.txt")))
    special = load_txt(os.path.join(tool_path, "ALL_special_topic.txt"))
    black_str = set(load_txt(os.path.join(tool_path, "ALL_black_words.txt")))
    black_list = set(load_json(os.path.join(tool_path, "Part_black.json")))
    bad = load_txt(os.path.join(tool_path, "bad.txt"))
    is_en = set(os.path.join(tool_path, "not_en_keys.txt"))
    safe = set(os.path.join(tool_path, "checked.txt"))
    bert_dirty = load_txt(os.path.join(tool_path, "bert_dirty.txt"))

    black_str.update(special)
    black_str.update(bert_dirty)
    black_str.update(BLACK_STR)
    black_list.update(BLACK_LIST)
    black_list.update(bad)

    # safe_name = load_txt("/home/wangyida/data_wash/data/v3/tools_data/dirty/name_keys.txt")
    # good = load_txt("/home/wangyida/data_wash/data/v3/tools_data/good.txt")
    # safe_words = load_txt("/home/wangyida/data_wash/data/v3/tools_data/dirty/black_keys.txt")
    # for word in set(safe_name + good + safe_words + SAFE_LIST +
    #                 ["的", "重庆", "四川", "海南", "然后", "电影", "系", "爷爷", "娘", "工资", "支持", "机会", "女人", "实现",
    #         "能力", "机场", "身高", "体重", "滚", "渣男", "绿茶", "视奸", "隔壁老王", "me too" ,
    #                  "日", "色", "本", "干", "哥哥", "消息", "皮肤", "医院", "网络"]): # "鸡"
    #     black_str.discard(word)
    #     black_list.discard(word)
    #     person_name.discard(word)
    safe_str = ["烂", "性", "娘", "妈", "日", "鸡", "粉"]
    for word in safe_str:
        black_str.discard(word)
        black_str.update("weibo")

    for word in safe_str:
        safe.discard(word)
    for word in safe:
        black_str.discard(word)
        black_list.discard(word)
        person_name.discard(word)
    black_list.update(safe_str)

    extra_bad = ["@", "微博", '国务院', '配图', '麻痹', '尼玛', '泥马', '妈比', 'mabi', '满身大汉',
                 '政府', 'sb', 'SB', 'sB', 'Sb', '网页链接', '图片评论', '图片', '王俊凯', '王源', '[', '(',
                 '#']  # '出柜', '出轨' '黑幕', '艾滋'
    black_list.update(extra_bad)

    confused = []
    # confused = set(load_txt("/home/wangyida/data_wash/data/v3/tools_data/dirty/confuse.txt"))
    # confused.update(SAFE_STR)
    # confused.update(["日", "色", "本", "干", "鸡", "小姐", "哥哥", "消息", "妹妹", "皮肤", "医院", "网络"])

    return person_name, black_str, black_list, is_en, confused
