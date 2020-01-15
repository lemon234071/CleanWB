from utils import *
from helper.tokenization import FullTokenizer
import random
from tqdm import tqdm
import collections

random.seed(2020)


def onmt_stc(path, out_dir):
    data_list = load_json(path)
    data = {}
    random.shuffle(data_list)
    train_v1 = data_list
    valid_v1 = data_list[-10000:]

    temp_set = set([x[0] for x in valid_v1])
    print("set len:", len(temp_set))

    train_v2 = []
    temp_dialogs = []
    for dialog in train_v1:
        if dialog[0] in temp_set:
            temp_dialogs.append(dialog)
        else:
            train_v2.append(dialog)

    temp_list = list(temp_set)
    random.shuffle(temp_list)
    k = int(len(temp_list) / 2)
    valid_set = set(temp_list[:k])
    test_set = set(temp_list[k:])

    valid_v2 = []
    test_v2 = []
    for dialog in temp_dialogs:
        if dialog[0] in valid_set:
            valid_v2.append(dialog)
        else:
            test_v2.append(dialog)

    print("train len:", len(train_v2))
    print("valid len:", len(valid_v2))
    print("test len:", len(test_v2))
    data["train"] = train_v2
    data["valid"] = valid_v2
    data["test"] = test_v2

    for k, v in data.items():
        src = []
        tgt = []
        for line in tqdm(v, mininterval=2):
            src.append(" ".join([x for x in line[0].replace(" ", "")]))
            tgt.append(" ".join([x for x in line[1].replace(" ", "")]))

        if k == "dev":
            k = "valid"
        save_txt("\n".join(src), out_dir + "src-" + k + ".txt")
        save_txt("\n".join(tgt), out_dir + "tgt-" + k + ".txt")


def build_vocab():
    data = load_json("/home/wangyida/data_wash/data/v2/single_final.json")
    for i, dialog in enumerate(data):
        for j, seq in enumerate(dialog):
            seq = seq.strip().replace(" ", "")
            data[i][j] = [x for x in seq]
    data1 = load_json("/home/wangyida/data/stc/stc.json")
    for i, dialog in enumerate(data1):
        for j, seq in enumerate(dialog):
            seq = seq.strip().replace(" ", "")
            data1[i][j] = [x for x in seq]
    data.extend(data1)
    print(data[0])
    vocab = collections.Counter()
    for dialog in tqdm(data, mininterval=2):
        for utterance in dialog:
            vocab.update(utterance)
    sorted_vocab = sorted(vocab.items(), key=lambda x: x[1], reverse=True)
    vocab_list = [x[0] for x in sorted_vocab]
    print(len(vocab_list))
    save_txt("\n".join(vocab_list), "/home/wangyida/data/stc/vocab.txt")


def for_context():
    raw = load_json('/home/wangyida/data/stc/stc_weibo_train_data')
    data = []
    for dialog in tqdm(raw, mininterval=2):
        for resp in dialog[1]:
            post = dialog[0].strip()
            resp = resp.strip()
            data.append([post, resp])
    save_json(data, '/home/wangyida/data/stc/stc.json')
    posts = list(set([x[0] for x in data]))
    new_data = []
    for post in tqdm(posts, mininterval=2):
        line = ["0\t", post, "\n"]
        new_data.extend(line)
    data_out = "".join(new_data)
    save_txt(data_out, "/home/wangyida/data/stc/post.txt")


def get_context():
    labels = load_json("/home/wangyida/data/stc/cls/postfor_context_bad.json")
    posts = load_txt("/home/wangyida/data/stc/cls/post.txt")
    new_post = []
    for i, label in enumerate(labels):
        if label:
            new_post.append(posts[i])
    save_txt("\n".join(new_post), "/home/wangyida/data/stc/cls/post_context_bad.txt")

def get_clean():
    labels = load_json("/home/wangyida/data/stc/cls/cleanfor_clean_labels.json")
    posts = load_txt("/home/wangyida/data/stc/cls/clean.json")
    new_post = []
    for i, label in enumerate(labels):
        if not label:
            new_post.append(posts[i])
    save_txt("\n".join(new_post), "/home/wangyida/data/stc/cls/clean_bad.txt")


def gen_clean(path, outpath):
    data = load_json(path)
    new_data = []
    for dialog in tqdm(data, mininterval=2):
        line = ["0\t", " ; ".join(dialog), "\n"]
        new_data.extend(line)
    data_out = "".join(new_data)
    # save_txt(data_out, "/home/wangyida/data_wash/data/v2/cls/single_clean_cls.txt")
    save_txt(data_out, outpath)


def sta_our():
    data = load_json("/home/wangyida/data_wash/data/v2/single_final.json")
    n = 0
    for dialog in data:
        resp = dialog[1].replace(" ", "")
        if resp.startswith("我也") or resp.startswith("哈哈"):
            n += 1
    print(n)
    # resp = [x[1].split() for x in data]
    # len_list = [len(x) for x in resp]
    # temp_dic = collections.Counter()
    # temp_dic.update(len_list)
    # sta_len = sorted(temp_dic.items(), key=lambda x: x[0], reverse=False)
    # save_json(sta_len, "/home/wangyida/data/stc/sta_len_our.json")


def exper_longresp():
    data = load_json("/home/wangyida/data_wash/data/v2/single/single_after_rule.json")
    new_data = []
    for dialog in data:
        resp = dialog[1].replace(" ", "")
        if len(resp) > 10:
            new_data.append(dialog)
    print(len(new_data))
    #save_json(new_data, "/home/wangyida/data/stc/our_single_long.json")
    src = []
    tgt = []
    for line in tqdm(new_data, mininterval=2):
        src.append(" ".join([x for x in line[0].replace(" ", "")]))
        tgt.append(" ".join([x for x in line[1].replace(" ", "")]))

    out_dir = "/home/wangyida/data/char_level/onmt_single_long/"
    save_txt("\n".join(src), out_dir + "src-train.txt")
    save_txt("\n".join(tgt), out_dir + "tgt-train.txt")


def sta_gen():
    data = load_txt("/home/wangyida/data/stc/transformer_our_test.txt")
    cut_data = [x.replace(" ", "") for x in data]
    sta_dict = collections.Counter()
    sta_dict.update(cut_data)
    sorted_vocab = sorted(sta_dict.items(), key=lambda x: x[1], reverse=True)
    save_json(sorted_vocab, "/home/wangyida/data/stc/sta_safe.json")


def gen_our_desafe():
    data = load_json("/home/wangyida/data_wash/data/v2/single_final.json")
    src = []
    tgt = []
    for line in data:
        post = line[0].replace(" ", "")
        resp = line[1].replace(" ", "")
        if resp.startswith("哈哈") or resp.startswith("我也") or resp.startswith("是的") or resp.startswith("嗯嗯")\
                or resp.startswith("是啊") or resp.startswith("晚安"):
            continue
        src.append(" ".join([x for x in post]))
        tgt.append(" ".join([x for x in resp]))
    print(len(tgt))

    outdir = "/home/wangyida/data/char_level/onmt_single_dehaha/"
    save_txt("\n".join(src), outdir + "src-train.txt")
    save_txt("\n".join(tgt), outdir + "tgt-train.txt")

def get_response():
    src_valid = load_txt("/home/wangyida/data/stc/onmt_single/src-valid.txt")
    tgt_valid = load_txt("/home/wangyida/data/stc/onmt_single/tgt-valid.txt")
    src_test = load_txt("/home/wangyida/data/stc/onmt_single/src-test.txt")
    tgt_src = load_txt("/home/wangyida/data/stc/onmt_single/tgt-test.txt")
    src_valid.extend(src_test)
    tgt_valid.extend(tgt_src)
    data = []
    for i, seq in enumerate(src_valid):
        data.append([seq, tgt_valid[i]])
    save_json(data, "/home/wangyida/data/stc/output/valid_test.json")
    new_data = []
    for dialog in tqdm(data, mininterval=2):
        line = ["0\t", " ; ".join(dialog), "\n"]
        new_data.extend(line)
    data_out = "".join(new_data)
    # save_txt(data_out, "/home/wangyida/data_wash/data/v2/cls/single_clean_cls.txt")
    save_txt(data_out, "/home/wangyida/data/stc/cls/valid_test.txt")


def merge_valid_test():
    # resp_dir = "/home/wangyida/data/stc/result/v2/"
    # src_dir = "/home/wangyida/data/stc/onmt_single/"
    resp_dir = "/home/wangyida/data/stc/result/v2/"
    src_dir = "/home/wangyida/data/char_level/onmt_single_fulltokenized/"
    src_test = load_txt(src_dir + "src-test.txt")
    resp_test = load_txt(resp_dir + "cleaned_test.txt")

    data = []
    for i in range(len(src_test)):
        data.append([src_test[i], resp_test[i]])

    save_json(data, "/home/wangyida/data/stc/result/v2/cls/our_cleaned-gen.json")


def main():
    # onmt_stc("/home/wangyida/data_wash/data/v2/single_final.json", "/home/wangyida/data/char_level/onmt_single_fulltokenized/")
    # onmt_stc("/home/wangyida/data/stc/stc.json", "/home/wangyida/data/stc/onmt_single/")
    # build_vocab()
    # merge_valid_test()
    # for_context()
    # get_context()
    # get_response()
    # get_clean()
    # gen_clean("/home/wangyida/data/stc/output/valid_test_single.json", "/home/wangyida/data/stc/cls/stc_gen_forclean.txt")
    # sta_our()
    # exper_longresp()
    # sta_gen()
    # gen_our_desafe()
    merge_valid_test()
    print(1)


if __name__ == '__main__':
    main()
