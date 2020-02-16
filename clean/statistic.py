from utils import *
import collections
import os
from tqdm import tqdm


def sta_black_keys():
    temp_dir = "/home/wangyida/data_wash/data/v2/dirty_dialog/black/"
    paths = [temp_dir + file for file in os.listdir(temp_dir)]
    black = {}
    for path in paths:
        data = load_json(path)
        for key in list(data.keys()):
            if key not in black.keys():
                black[key] = len(data[key])
            else:
                black[key] += len(data[key])
    black_dict = sorted(black.items(), key=lambda x: x[1], reverse=True)
    save_json(black_dict, "/home/wangyida/data_wash/data/v3/tools_data/dirty/black.json")
    save_txt("\n".join([x[0] for x in black_dict]), "/home/wangyida/data_wash/data/v3/tools_data/dirty/black_keys.txt")

    name_data = load_json("/home/wangyida/data/stc/dirty_dialog/name_stc.json")
    name = {}
    for k, v in name_data.items():
        if k in name:
            name[k] += len(v)
        else:
            name[k] = len(v)
    name_dict = sorted(name.items(), key=lambda x: x[1], reverse=True)
    save_json(name_dict, "/home/wangyida/data_wash/data/v3/tools_data/dirty/name.json")
    save_txt("\n".join([x[0] for x in name_dict]), "/home/wangyida/data_wash/data/v3/tools_data/dirty/name_keys.txt")


def long_filter(path, outpath, multi=False):
    data = load_json(path)
    print(len(data))
    new_data = []

    dupl = []
    long = []
    total_long = []
    for dialog in data:
        dupl_set = list()
        n = 0
        start = 0
        flag = False
        for i, seq in enumerate(dialog):
            if seq not in dupl_set:
                dupl_set.append(seq)
            word_list = seq.strip().split()
            k = len(word_list)
            n += k
            if k > 128 or len(seq.strip()) < 2:
                flag = True
                long.append(seq)
                # long.extend(seq)
                if multi:
                    if (i - start) > 2:
                        new_data.append(dialog[start: i])
                    start = i + 1
                else:
                    break

        if len(dupl_set) < 2:
            dupl.append(dialog)
            continue
        elif len(dupl_set) < 3 and len(dialog) > 4:
            dupl.append(dialog)
            continue
        if n > 256:
            total_long.append(dialog)
            continue
        if flag:
            if multi and (len(dialog) - start) > 2:
                new_data.append(dialog[start:])
            continue
        new_data.append(dialog)
    dir = "/home/wangyida/data_wash/data/v2/dirty_dialog_post/multi" if multi \
        else "/home/wangyida/data_wash/data/v2/dirty_dialog_post/single"
    save_json(dupl, dir + "_dupl.json")
    long.sort(reverse=True)
    save_json(long, dir + "_long.json")
    save_json(total_long, dir + "_total_long.json")

    min_len = min([len(dialog) for dialog in new_data])
    print(min_len)
    print(len(new_data))
    data_set = set(["[SEP]".join(dialog) for dialog in new_data])
    data_list = [dialog.split("[SEP]") for dialog in list(data_set)]
    print(len(data_list))
    save_json(data_list, outpath)


def sta_final(data, outpath):
    #data = load_json(path)
    cnt_seq_len = collections.Counter()
    cnt_chars_perseq = collections.Counter()
    cnt_words_dialog = collections.Counter()
    cnt_turns = collections.Counter()
    vocab_dict = collections.Counter()

    all_num_char = 0
    num_max_chars = 0
    num_words = 0
    num_seq = 0
    num_davg_len = 0
    max_turns = 0
    max_seq = 0

    turn_len_list = []
    dupl = []

    long_turn_threshold = 30
    long_turns = []
    long_seq_threshold = 140
    long_seq = []
    words_dialog_threshold = 320
    longlong_list = []

    for dialog in tqdm(data):
        num_turns = len(dialog)
        max_turns = max(num_turns, max_turns)
        num_seq += num_turns
        turn_len_list.append(num_turns)
        if num_turns > long_turn_threshold:
            long_turns.append(dialog)

        flag = False
        words_dialog = 0
        dupl_set = set()
        for seq in dialog:
            dupl_set.add(seq)
            num_chars = len(seq.strip().replace(" ", ""))
            num_max_chars = max(num_max_chars, num_chars)
            all_num_char += num_chars
            cnt_chars_perseq.update([num_chars])

            word_list = seq.strip().split()
            num_seq_len = len(word_list)
            max_seq = max(max_seq, num_seq_len)
            words_dialog += num_seq_len
            vocab_dict.update(word_list)

            num_words += num_seq_len
            cnt_seq_len.update([num_seq_len])
            if num_seq_len > long_seq_threshold:
                long_seq.append(seq)
                #     flag = True
                #     break
        cnt_words_dialog.update([words_dialog])
        num_davg_len += words_dialog / num_turns
        if words_dialog > words_dialog_threshold:
            longlong_list.append(dialog)
        #     continue
        # if flag:
        #     continue

        # filtered in rules
        # if len(dupl_set) < 2 < num_turns:
        #     dupl.append(dialog)
        #     continue
        # if len(dupl_set) < 3 and 4 < num_turns:
        #     dupl.append(dialog)
        #     continue

    print("all chars", all_num_char)
    print("number dialog", len(data))
    print("number seq", num_seq)
    print("avg seq per dialog", num_seq / len(data))
    print("avg words per seq", num_words / num_seq)
    print("avg words per seq2", num_davg_len / len(data))
    print("max turns ", max_turns)
    print("max seq", max_seq)

    cnt_turns.update(turn_len_list)
    turn_len_list.sort()
    if len(turn_len_list) % 1 == 1:
        num_media = turn_len_list[int((len(turn_len_list) - 1) / 2)]
    else:
        num_media = turn_len_list[int((len(turn_len_list) / 2 + len(turn_len_list) / 2 - 1) / 2)]
    print("median of number of turns ", num_media)

    save_json(long_turns, outpath + 'long_turns.json')
    save_json(long_seq, outpath + 'long_seq.json')
    save_json(longlong_list, outpath + 'long_all.json')
    # save_json(dupl, outpath + 'dupl_list.json')

    vocab_dict = sorted(vocab_dict.items(), key=lambda x: int(x[1]), reverse=True)
    save_json(vocab_dict, outpath + 'vocab.json')
    cnt_seq_len = sorted(cnt_seq_len.items(), key=lambda x: int(x[0]), reverse=False)
    save_json(cnt_seq_len, outpath + 'seq_len.json')
    cnt_chars_perseq = sorted(cnt_chars_perseq.items(), key=lambda x: int(x[0]), reverse=False)
    save_json(cnt_chars_perseq, outpath + 'seq_len_char.json')
    cnt_turns = sorted(cnt_turns.items(), key=lambda x: int(x[0]), reverse=False)
    save_json(cnt_turns, outpath + 'cnt_turns.json')
    cnt_dialog_len = sorted(cnt_words_dialog.items(), key=lambda x: int(x[0]), reverse=False)
    save_json(cnt_dialog_len, outpath + 'dialog_words.json')


def main():
    # sta_black_keys()
    # sta_final("/home/wangyida/211/v3/data/CleanWB/single_final_v1.json",
    #           "/home/wangyida/211/v3/data/CleanWB/sta_single/")
    # sta_final("/home/wangyida/211/v3/data/CleanWB/multi_final_v1.json",
    #           "/home/wangyida/211/v3/data/CleanWB/sta_multi/")
    data = load_json("/home/wangyida/data/LCCD/LCCD.json")
    data = [x for x in data if len(x) > 2]
    sta_final(data, "/home/wangyida/data/LCCD/sta_multi/")
    print(1)


if __name__ == '__main__':
    main()
