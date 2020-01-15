import random
from collections import defaultdict
import gc
import pandas as pd
from tqdm import tqdm
import os

from helper.tokenization import FullTokenizer
from utils import *

random.seed(42)


def train_test_split_single(path, outpath):
    data = load_json(path)

    random.shuffle(data)
    len_data = int(0.01 * len(data))
    data_out = defaultdict(list)
    data_out['train'] = data[:-len_data]
    data_out['dev'] = data[-len_data: int(-len_data / 2)]
    data_out['test'] = data[int(-len_data / 2):]
    del data
    gc.collect()
    save_json(data_out, outpath)


def train_test_split_multi(path, outpath):
    data = load_json(path)
    random.shuffle(data)
    len_data = int(0.01 * len(data))

    data_out = defaultdict(list)
    data_raw = data[:-len_data]
    test = data[-len_data:]

    print(len(data_raw))
    for dialog in data_raw:
        for i in range(3, len(dialog) + 1):
            data_out['train'].append(dialog[:i])
    random.shuffle(data_out['train'])
    print(len(data_out['train']))

    del data, data_raw
    gc.collect()

    C = 20
    new_test = []
    random.seed(2019)
    for dialog in test:
        t = len(dialog)
        eta = random.uniform(C / 20, 10 * C)
        n = int(10 * C / eta + 2)
        c = min(t, n)
        new_test.append(dialog[:c])

    data_out['dev'] = new_test[-len_data: int(-len_data / 2)]
    data_out['test'] = new_test[int(-len_data / 2):]
    save_json(data_out, outpath)


def pre_char_onmt(path, outdir):
    tokenizer = FullTokenizer("/home/wangyida/data/char_level/vocab.txt")
    data = load_json(path)
    for k, v in data.items():
        src = []
        tgt = []
        for line in v:
            new_seq = []
            for seq in line[:-1]:
                new_seq.append(" ".join(tokenizer.tokenize(seq.strip())))
            src.append(" [SEP] ".join(new_seq))
            tgt.append(" ".join(tokenizer.tokenize(line[-1].strip())))

        if k == "dev":
            k = "valid"
        save_txt("\n".join(src), outdir + "src-" + k + ".txt")
        save_txt("\n".join(tgt), outdir + "tgt-" + k + ".txt")


def pre_char_hred():
    path = "/home/wangyida/data/char_level/onmt_multi/"
    for name in ["train", "valid", "test"]:
        src = load_txt(path + "src-" + name + ".txt")
        tgt = load_txt(path + "tgt-" + name + ".txt")
        Context = []
        Utterance = []
        n = 0
        for i in range(len(src)):
            bug_tgt = tgt[i].split()
            if len(bug_tgt) < 2:
                n += 1
                continue
            Context.append(" __eot__ ".join([x + " __eou__" for x in src[i].split("[SEP]")]) + " __eot__ ")
            Utterance.append(tgt[i] + " __eou__")
        print(n)

        out = pd.DataFrame({'Context': Context, 'Utterance': Utterance, 'Label': ['1.0' for x in Utterance]})
        out.to_csv("/home/wangyida/data/char_level/ubuntu/ubuntu_corpus_%s.csv" % name, index=False)


def help_preare_trans(dataset, len_dataset, i, new_dialog, select_list):
    utterance = []
    utterance.append(" [SEP] ".join(new_dialog[:-1]))
    utterance.append("\t")
    sample_list = random.sample(select_list, 1)
    # sample_list = random.sample(select_list, 9)
    if i in sample_list:
        new_i = i
        while new_i in sample_list:
            new_i = random.randint(0, len_dataset - 1)
        sample_list.remove(i)
        sample_list.append(new_i)
    for k in sample_list:
        l = random.randint(1, len(dataset[k]) - 1) if len(dataset[k]) > 2 else -1
        utterance.append(dataset[k][l])
        utterance.append(" [SEP] ")
    utterance.append(new_dialog[-1])
    return "".join(utterance)


def prepare_trans(path, out_path, name):
    print(out_path+name)
    train = load_txt(path+name+"train.txt")
    dev = load_txt(path+name+"dev.txt")
    test = load_txt(path+name+"test.txt")

    def temp(data):
        data_list = data.split("\t")
        res = data_list[0].split("[SEP]")
        res.append(data_list[1])
        return res
    new_train = [temp(x) for x in train]
    new_dev = [temp(x) for x in dev]
    new_test = [temp(x) for x in test]

    data = {"train": new_train, "dev": new_dev, "test": new_test}

    datasets = {"train": [], "dev": [], "test": []}
    # history [SEP] history \t response_false [SEP] response_true
    for key, dataset in data.items():
        len_dataset = len(dataset)
        select_list = range(0, len_dataset)
        for i, dialog in enumerate(tqdm(dataset, mininterval=5)):
            utterance = help_preare_trans(dataset, len_dataset, i, dialog, select_list)
            datasets[key].append(utterance)
    save_txt("\n".join(datasets["train"]), out_path + name + "_train.txt")
    save_txt("\n".join(datasets["dev"]), out_path + name + "_dev.txt")
    save_txt("\n".join(datasets["test"]), out_path + name + "_test.txt")


def prepare_trans_new(path, out_path):
    name = "single" if "single" in path else "multi"
    print(out_path+name)
    datasets = defaultdict(list)
    for type in ["train", "valid", "test"]:
        src = load_txt(path + "src-" + type + ".txt")
        tgt = load_txt(path + "tgt-" + type + ".txt")
        utterances = []
        n = 0
        for i in range(len(src)):
            flag = False
            for x in src[i].split("[SEP]"):
                if not x:
                    flag = True
                    break
            if flag:
                n += 1
                continue
            if not tgt[i]:
                n += 1
                continue
            utterances.extend([src[i], "\t", tgt[i], "\n"])
        datasets[type] = utterances
        print(n)
    save_txt("".join(datasets["train"]), out_path + name + "_train.txt")
    save_txt("".join(datasets["valid"]), out_path + name + "_dev.txt")
    save_txt("".join(datasets["test"]), out_path + name + "_test.txt")


def fix_bug(path1, out_path):
    paths = [path1 + name1 for name1 in os.listdir(path1)]
    for path in paths:
        name = "onmt_single/" if "single" in path else "onmt_multi/"
        if "train" in path:
            dataset = "train"
        elif "test" in path:
            dataset = "test"
        else:
            dataset = "valid"
        print(out_path + name + "src-%s.txt"%dataset)
        data = load_txt(path)
        src = []
        tgt = []
        for line in data:
            data_l = line.strip().split("\t")
            src.extend([data_l[0], "\n"])
            tgt.extend([data_l[1], "\n"])
        assert len(src) == len(tgt)
        new_src = "".join(src)
        print(len(new_src))
        save_txt(new_src, out_path + name + "src-%s.txt"%dataset)
        save_txt("".join(tgt), out_path + name + "tgt-%s.txt"%dataset)

def fix_bug2():
    path = "/home/wangyida/data/char_level/onmt_multi/"
    for name in ["train", "valid", "test"]:
        src = load_txt(path + "backup/src-" + name + ".txt")
        tgt = load_txt(path + "backup/tgt-" + name + ".txt")
        Context = []
        Utterance = []
        n = 0
        for i in range(len(src)):
            bug_tgt = tgt[i].split()
            if len(bug_tgt) < 2:
                n += 1
                continue
            Context.extend([src[i], "\n"])
            Utterance.extend([tgt[i], "\n"])
        print(n)
        save_txt("".join(Context), path + "src-" + name + ".txt")
        save_txt("".join(Utterance), path + "tgt-" + name + ".txt")


def pre_char_ubuntu():
    def dedupl(str_list):
        new_list = []
        str_list = sorted(str_list, key=lambda x: len(x), reverse=True)
        for one in str_list:
            flag_this = False
            for res in new_list:
                if one in res:
                    flag_this = True
                    break
            if flag_this:
                continue
            new_list.append(one)
        return new_list

    path = "/home/wangyida/data/char_level/onmt_multi/"
    for name in ["train", "valid", "test"]:
        src = load_txt(path + "src-" + name + ".txt")
        tgt = load_txt(path + "tgt-" + name + ".txt")
        Context = []
        Utterance = []
        n = 0
        if name == "train":
            dupl_dict = defaultdict(list)
            for i in range(len(src)):
                seq_list = src[i].split("[SEP]")
                flag = False
                for seq in seq_list:
                    word_list = seq.split()
                    if len(word_list) < 2:
                        flag = True
                        break
                if flag:
                    n += 1
                    continue

                new_seq = "".join([src[i], " [SEP] ", tgt[i]])
                if i == 0:
                    print(new_seq)

                dupl_dict[seq_list[0]].append(new_seq)

                # if seq_list[0] not in dupl_dict.keys():
                #     dupl_dict[seq_list[0]] = new_seq
                # else:
                #     if dupl_dict[seq_list[0]] in new_seq:
                #         dupl_dict[seq_list[0]] = new_seq
                #     else:
                    # if len(new_seq) > len(dupl_dict[seq_list[0]]):
                    #     dupl_dict[seq_list[0]] = new_seq
            dupl_list = []
            for k, v in dupl_dict.items():
                v = dedupl(v)
                dupl_list.extend(v)
            random.shuffle(dupl_list)
            for src in dupl_list:
                res_list = src.split("[SEP]")
                Context.append(" __eot__ ".join([x + " __eou__" for x in res_list[:-1]]) + " __eot__ ")
                Utterance.append(res_list[-1] + " __eou__")
        else:
            for i in range(len(src)):
                bug_tgt = tgt[i].split()
                if len(bug_tgt) < 2:
                    n += 1
                    continue
                Context.append(" __eot__ ".join([x + " __eou__" for x in src[i].split("[SEP]")]) + " __eot__ ")
                Utterance.append(tgt[i] + " __eou__")
        print(n)

        out = pd.DataFrame({'Context': Context, 'Utterance': Utterance, 'Label': ['1.0' for x in Utterance]})
        out.to_csv("/home/wangyida/data/char_level/ubuntu/ubuntu_corpus_%s.csv" % name, index=False)


def main():
    # path = "/home/wangyida/data_wash/data/v2/single_final.json"
    # outpath = "/home/wangyida/data_wash/data/v2/single_v1.json"
    # train_test_split_single(path, outpath)
    # path = "/home/wangyida/data_wash/data/v2/multi_final.json"
    # outpath = "/home/wangyida/data_wash/data/v2/multi_v1.json"
    # train_test_split_multi(path, outpath)
    # path = "/home/wangyida/data_wash/data/v2/single_v1.json"
    # outdir = "/home/wangyida/data/char_level/onmt_single/"
    # pre_char_onmt(path, outdir)
    # path = "/home/wangyida/data_wash/data/v2/multi_v1.json"
    # outdir = "/home/wangyida/data/char_level/onmt_multi/"
    # pre_char_onmt(path, outdir)
    # pre_char_hred()
    # path = "/home/wangyida/data_wash/data/v2/multi_v1.json"
    # outpath = "/home/wangyida/data/char_level/trans"
    # prepare_trans(path, outpath)
    # path = "/home/wangyida/data_wash/data/v2/single_v1.json"
    # prepare_trans(path, outpath)
    # pre_char_hred()
    #########################bug
    # path = "/home/wangyida/data/char_level/onmt_multi/"
    # outpath = "/home/wangyida/data/char_level/trans/"
    # prepare_trans_new(path, outpath)
    # path = "/home/wangyida/data/char_level/onmt_single/"
    # prepare_trans_new(path, outpath)
    # path = "/home/wangyida/data/char_level/trans/"
    # outpath = "/home/wangyida/data/char_level/"
    # fix_bug(path, outpath)
    # fix_bug(path, outpath)
    #pre_char_hred()
    #fix_bug2()
    # path = "/home/wangyida/data/char_level/onmt_multi/"
    # outpath = "/home/wangyida/data/char_level/trans/"
    # prepare_trans_new(path, outpath)
    # pre_char_ubuntu()

    path = "/home/wangyida/data/char_level/gpt/"
    outpath = "/home/wangyida/data/char_level/trans/"
    prepare_trans(path, outpath, "multi_")
    prepare_trans(path, outpath, "single_")


if __name__ == '__main__':
    main()
