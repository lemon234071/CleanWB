import os
import gc
import collections
import jieba
from tqdm import tqdm
import unicodedata

from utils import *
from clean.filter import Filter


def main_filter(simple_filter: Filter, data, fid, out_dir, dirty_dir, resp_only=False, cut=False):
    print("resp_only:", resp_only)
    print("cut :", cut)
    # fid = path[path.rindex("/") + 1:path.rindex(".")]
    out_path = os.path.join(out_dir, fid + "_multi.json")
    print(out_path)
    if not os.path.exists(out_path[:out_path.rindex("/")]):
        print(out_path[:out_path.rindex("/")], "not exist!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        return

    print("start:", fid)
    # data = loader(path)
    print('length of data:', len(data))
    output_single = []
    output_multi = []
    dirty_data = collections.defaultdict(list)
    black = collections.defaultdict(list)
    name_dict = collections.defaultdict(list)
    not_en_dict = collections.defaultdict(list)
    confuse_dict = collections.defaultdict(list)
    generic_dict = []

    print(data[0][0])
    for dialog in tqdm(data, mininterval=1):
        assert isinstance(dialog[0], str)
        # de duplicated utter
        if len(set(dialog)) < 2:
            dirty_data["repeater"].append(dialog)
            continue
        # start
        if len(dialog) < 3:
            flag = False
            for i in range(len(dialog)):
                if resp_only:
                    if i < 1:
                        continue
                #### de {\\1c&H4080FF&}
                if "{\\1c&H4080FF&}" in dialog[i]:
                    dialog[i] = dialog[i].replace("{\\1c&H4080FF&}", "")
                #### de @
                if "回复 @" in dialog[i] and ":" in dialog[i]:
                    dialog[i] = dialog[i][dialog[i].index(":") + 2:]
                if "¡ 评论" in dialog[i]:
                    dialog[i] = dialog[i][:dialog[i].index("¡ 评论")]
                # dialog[i] = dialog[i].replace("[ 挖 鼻屎 ]", "")
                if "[" in dialog[i] and "]" in dialog[i]:
                    if dialog[i].index("[") < dialog[i].index("]"):
                        str_in = dialog[i][dialog[i].index("["): dialog[i].index("]") + 1]
                        dialog[i] = dialog[i].replace(str_in, "")
                ##############################################
                if cut:
                    dialog[i] = " ".join(jieba.cut(dialog[i]))
                word_list = dialog[i].strip().split()
                dialog[i] = " ".join(word_list)

                word_str = simple_filter.dedup("".join(word_list))
                if not word_str:
                    dirty_data["dupl"].append(dialog)
                    flag = True
                    break
                # word level
                if i > 0:
                    en_word = simple_filter.not_en(word_list)
                    if en_word:
                        not_en_dict[en_word].append(dialog)
                        flag = True
                        break
                    name = simple_filter.person_name(word_list)
                    if name:
                        name_dict[name].append(dialog)
                        flag = True
                        break

                confuse_word = simple_filter.check_confuse(word_list)
                if confuse_word:
                    confuse_dict[confuse_word].append(dialog)

                dirty_word = simple_filter.black_wordlist(word_list)
                if dirty_word:
                    black[dirty_word].append(dialog)
                    flag = True
                    break
                # str-level

                if simple_filter.too_short(word_str, 2):
                    dirty_data["dupl"].append(dialog)
                    flag = True
                    break
                dirty_word = simple_filter.black_str(word_str)
                if dirty_word:
                    black[dirty_word].append(dialog)
                    flag = True
                    break
                if simple_filter.emoji(word_str):
                    dirty_data["emoji"].append(dialog)
                    flag = True
                    break
                if simple_filter.duplicated(word_str, 3):
                    dirty_data["dupl"].append(dialog)
                    flag = True
                    break

                if simple_filter.my_duplicated(word_list):
                    generic_dict.append(dialog)

            if not flag:
                output_single.append(dialog)
        else:
            start = 0
            for i in range(len(dialog)):
                if "{\\1c&H4080FF&}" in dialog[i]:
                    dialog[i] = dialog[i].replace("{\\1c&H4080FF&}", "")
                ###### de @
                if "回复 @" in dialog[i] and ":" in dialog[i]:
                    dialog[i] = dialog[i][dialog[i].index(":") + 2:]
                if "¡ 评论" in dialog[i]:
                    dialog[i] = dialog[i][:dialog[i].index("¡ 评论")]
                if "[" in dialog[i] and "]" in dialog[i]:
                    if dialog[i].index("[") < dialog[i].index("]"):
                        str_in = dialog[i][dialog[i].index("["): dialog[i].index("]") + 1]
                        dialog[i] = dialog[i].replace(str_in, "")
                #####################################
                if cut:
                    dialog[i] = " ".join(jieba.cut(dialog[i]))
                word_list = dialog[i].strip().split()
                dialog[i] = " ".join(word_list)
                word_str = simple_filter.dedup("".join(word_list))
                if not word_str:
                    dirty_data["dupl"].append(dialog)
                    if (i - start) > 2:
                        output_multi.append(dialog[start: i])
                    start = i + 1
                    continue
                ##############################################
                # word level
                confuse_word = simple_filter.check_confuse(word_list)
                if confuse_word:
                    confuse_dict[confuse_word].append(dialog[i])

                dirty_word = simple_filter.black_wordlist(word_list)
                if dirty_word:
                    black[dirty_word].append(dialog[i])
                    if (i - start) > 2:
                        output_multi.append(dialog[start: i])
                    start = i + 1
                    continue
                name = simple_filter.person_name(word_list)
                if name:
                    name_dict[name].append(dialog[i])
                    if (i - start) > 2:
                        output_multi.append(dialog[start: i])
                    start = i + 1
                    continue
                en_word = simple_filter.not_en(word_list)
                if en_word:
                    not_en_dict[en_word].append(dialog[i])
                    if (i - start) > 2:
                        output_multi.append(dialog[start: i])
                    start = i + 1
                    continue
                # str-level

                if simple_filter.too_short(word_str, 2):
                    dirty_data["dupl"].append(dialog[i])
                    if (i - start) > 2:
                        output_multi.append(dialog[start: i])
                    start = i + 1
                    continue
                if simple_filter.emoji(word_str):
                    dirty_data["emoji"].append(dialog[i])
                    if (i - start) > 2:
                        output_multi.append(dialog[start: i])
                    start = i + 1
                    continue
                dirty_word = simple_filter.black_str(word_str)
                if dirty_word:
                    black[dirty_word].append(dialog[i])
                    if (i - start) > 2:
                        output_multi.append(dialog[start: i])
                    start = i + 1
                    continue
                if simple_filter.duplicated(word_str, 3):
                    dirty_data["dupl"].append(dialog[i])
                    if (i - start) > 2:
                        output_multi.append(dialog[start: i])
                    start = i + 1
                    continue

                if (i - start) > 30:
                    output_multi.append(dialog[start: i])
                    start = i + 1

                if simple_filter.my_duplicated(word_list):
                    generic_dict.append(dialog[start: i])

            if (len(dialog) - start) > 2:
                output_multi.append(dialog[start:])
            # else:
            #     # bug here
            #     output_multi.append(dialog[-3:])

    if len(output_multi) > 0:
        save_json(output_multi, out_path)
    if len(output_single) > 0:
        save_json(output_single, out_path.replace("multi", "single"))

    for file in ["other", "black", "name", "not_en", "generic", "confuse"]:
        temp_path = os.path.join(dirty_dir, file)
        if not os.path.exists(temp_path):
            os.makedirs(temp_path)
    for key, value in dirty_data.items():
        if len(value) > 0:
            dirty_dialog_path = os.path.join(dirty_dir, 'other/%s_%s.json' % (key, fid))
            save_json(value, dirty_dialog_path)

    # dirty_dic = {"black": black, "name": name_dict, "not_en": not_en_dict, "generic": generic_dict,
    #              "confuse": confuse_dict}
    # for k, v in dirty_dic.items():
    #     k_dir = os.path.join(dirty_dir, k)
    #     if not os.path.isdir(k_dir):
    #         os.mkdir(k_dir)
    #     save_json(v, os.path.join(k_dir, str(fid)))
    save_json(black, os.path.join(dirty_dir, 'black/black_%s.json' % fid))
    save_json(name_dict, os.path.join(dirty_dir, 'name/name_%s.json' % fid))
    save_json(not_en_dict, os.path.join(dirty_dir, 'not_en/not_en_%s.json' % fid))
    save_json(generic_dict, os.path.join(dirty_dir, 'generic/generic_%s.json' % fid))
    save_json(confuse_dict, os.path.join(dirty_dir, 'confuse/confuse_%s.json' % fid))
    print(fid, "over")


def data_merge(dir, save_path=None):
    pathes = [os.path.join(dir, name) for name in os.listdir(dir)]
    data = []
    for path in pathes:
        if "json" in path:
            dataset = load_json(path)
            data.extend(dataset)
    print("dialogs len:", len(data))
    temp = set(["[SEP]".join(x) for x in data])
    data = [x.strip().split("[SEP]") for x in temp]
    print("unique dialogs num", len(data))
    if save_path:
        save_json(data, save_path)
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


def de_ad(data, ad_path, save_path=None):
    resp_dict = collections.defaultdict(set)
    for dialog in data:
        for i in range(len(dialog)):
            if i < 1:
                continue
            resp_dict[dialog[i]].add(dialog[i - 1])
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
                    if i - start > 2:
                        new_data.append(dialog[start:i])
                        start = i + 1
            if (len(dialog) - start) > 2:
                new_data.append(dialog[start:])
        else:
            if dialog[-1] not in resp_set:
                new_data.append(dialog)
    if save_path:
        save_json(new_data, save_path)
    print("data len :", len(new_data))
    return new_data


def bert_clean(data, vocab_path, safe_path, dirty_dir, save_path=None):
    def is_number(s):
        try:
            float(s)
            return True
        except ValueError:
            pass

    def _is_whitespace(char):
        """Checks whether `chars` is a whitespace character."""
        # \t, \n, and \r are technically contorl characters but we treat them
        # as whitespace since they are generally considered as such.
        if char == " " or char == "\t" or char == "\n" or char == "\r":
            return True
        cat = unicodedata.category(char)
        if cat == "Zs":
            return True
        return False

    def _is_control(char):
        """Checks whether `chars` is a control character."""
        # These are technically control characters but we count them as whitespace
        # characters.
        if char == "\t" or char == "\n" or char == "\r":
            return False
        cat = unicodedata.category(char)
        if cat.startswith("C"):
            return True
        return False

    def _clean_text(text):
        """Performs invalid character removal and whitespace cleanup on text."""
        output = []
        for char in text:
            if char != " ":
                # if is_number(char):
                #     import pdb
                #     pdb.set_trace()
                if char not in vocab:
                    if char not in safe_vocab:
                        dirty.add(char)
                        continue
            # if is_number(char):
            #     continue
            cp = ord(char)
            if cp == 0 or cp == 0xfffd or _is_control(char):
                dirty.add(char)
                continue
            if _is_whitespace(char):
                output.append(" ")
            else:
                output.append(char)
        return "".join(output)

    vocab = set(load_txt(vocab_path))
    safe_vocab = set(load_txt(safe_path))
    # data = load_json(path)
    single_data = [dialog for dialog in data if len(dialog) < 3]
    multi_data = [dialog for dialog in data if len(dialog) > 2]
    del data
    gc.collect()
    print(safe_vocab)

    dirty = set()
    n_multi = 0
    n_single = 0
    new_multi = []
    white_multi = []
    white_single = []
    white_multi_dialog = []
    for dialog in tqdm(multi_data, mininterval=1):
        flag = False
        new_dialog = []
        for seq in dialog:
            one = _clean_text(seq).strip()
            if one:
                new_dialog.append(one)
            else:
                white_multi.append(seq)
                white_multi_dialog.append(dialog)
                n_multi += 1
                flag = True
                break
                # new_seq.append("哦")
                # import pdb
                # pdb.set_trace()
        if flag:
            continue
        new_multi.append(new_dialog)

    new_single = []
    for dialog in tqdm(single_data, mininterval=1):
        flag = False
        new_dialog = []
        for seq in dialog:
            one = _clean_text(seq).strip()
            if one:
                new_dialog.append(one)
            else:
                white_single.append(seq)
                n_single += 1
                flag = True
                break
        if flag:
            continue
        new_single.append(new_dialog)

    print(n_single, "multi:", n_multi)
    print(len(new_multi), "multi len")
    print(len(new_single), "single len")
    bert_dirty_dir = os.path.join(dirty_dir, "bert_dirty")
    print(bert_dirty_dir)
    if not os.path.isdir(bert_dirty_dir):
        os.mkdir(bert_dirty_dir)
    save_json(white_multi_dialog, os.path.join(bert_dirty_dir, "multi_dirty_dialog.json"))
    # save_json(list(dirty), os.path.join(bert_dirty_dir, "bert_dirty.json"))
    save_json(white_single, os.path.join(bert_dirty_dir, "white_single.json"))
    save_json(white_multi, os.path.join(bert_dirty_dir, "multi_white.json"))
    if save_path:
        save_json(new_multi + new_single, save_path)
    return new_multi + new_single


def de_generic(data, dirty_dir, tri_path, num, save_path=None):
    # data = load_json(path)

    def ngrams(resp, n):
        ngram = []
        if len(resp) >= n:
            for i in range(len(resp) - n + 1):
                ngram.append(''.join(resp[i: i + n]))
        return ngram

    if os.path.exists(tri_path):
        generic = load_json(tri_path)
        print("load from :", tri_path)
    else:
        print("len raw: ", len(data))
        generic = collections.Counter()
        # assert isinstance(dataset[0][0], str)
        for dialog in tqdm(data, mininterval=1):
            for seq in dialog:
                seq = seq.replace(" ", "")
                tri_grams = ngrams(seq, 3)
                generic.update(list(set(tri_grams)))

        generic = sorted(generic.items(), key=lambda x: x[1], reverse=True)
        save_json(generic, tri_path)
    screen = [(x, cnt) for x, cnt in generic if cnt > num]
    # print(screen)
    generic = set([x for x, cnt in screen])
    dirty_cnt = []
    dirty_gram = []

    new_dataset = []
    for dialog in tqdm(data, mininterval=1):
        resp = dialog[-1].replace(" ", "")
        tri_grams = ngrams(resp, 3)
        flag = False
        cnt = collections.Counter(tri_grams)
        for word, num in cnt.items():
            if 1 > tri_grams.count(num) * 3 / len(resp) > 0.9:
                if word in generic:
                    dirty_cnt.append(resp)
                    flag = True
                    break
            # if 1 > num/len(tri_grams) > 0.9:
            #     if word in generic:
            #         dirty_gram.append(resp)
            #         flag = True
            #         break
        if flag:
            continue
        new_dataset.append(dialog)
    print("len new: ", len(new_dataset))

    save_json(dirty_cnt, os.path.join(dirty_dir, "generic_resp.json"))
    # save_json(dirty_gram, "./temp/gram.json")

    if save_path:
        save_json(new_dataset, save_path)
    print("over")
    return new_dataset
