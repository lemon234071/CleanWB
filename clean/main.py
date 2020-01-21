import os
import collections
from utils import *
from tqdm import tqdm
from clean.filter import Filter


def main_filter(simple_filter: Filter, loader, path, out_dir, dirty_dir, resp_only=False):
    print("resp_only:", resp_only)
    fid = path[path.rindex("/") + 1:path.rindex(".")]
    out_path = out_dir + fid + "_multi.json"
    if not os.path.exists(out_path[:out_path.rindex("/")]):
        print(out_path[:out_path.rindex("/")], "not exist!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        return

    print("start:", fid)
    data = loader(path)
    print('length of data:', len(data))
    output_single = []
    output_multi = []
    dirty_data = collections.defaultdict(list)
    black = collections.defaultdict(list)
    name_dict = collections.defaultdict(list)
    not_en_dict = collections.defaultdict(list)
    confuse_dict = collections.defaultdict(list)
    generic_dict = []

    for dialog in tqdm(data, mininterval=60):
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
                    dialog[i] = dialog[i][dialog[i].index(":")+2:]
                if "¡ 评论" in dialog[i]:
                    dialog[i] = dialog[i][:dialog[i].index("¡ 评论")]
                # dialog[i] = dialog[i].replace("[ 挖 鼻屎 ]", "")
                if "[" in dialog[i] and "]" in dialog[i]:
                    if dialog[i].index("[") < dialog[i].index("]"):
                        str_in = dialog[i][dialog[i].index("["): dialog[i].index("]")+1]
                        dialog[i] = dialog[i].replace(str_in, "")
                ##############################################
                word_list = dialog[i].strip().split(None)
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
                    dialog[i] = dialog[i][dialog[i].index(":")+2:]
                if "¡ 评论" in dialog[i]:
                    dialog[i] = dialog[i][:dialog[i].index("¡ 评论")]
                if "[" in dialog[i] and "]" in dialog[i]:
                    if dialog[i].index("[") < dialog[i].index("]"):
                        str_in = dialog[i][dialog[i].index("["): dialog[i].index("]")+1]
                        dialog[i] = dialog[i].replace(str_in, "")
                #####################################
                word_list = dialog[i].strip().split(None)
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

    save_json(black, os.path.join(dirty_dir, 'black/black_%s.json' % fid))
    save_json(name_dict, os.path.join(dirty_dir, 'name/name_%s.json' % fid))
    save_json(not_en_dict, os.path.join(dirty_dir, 'not_en/not_en_%s.json' % fid))
    save_json(generic_dict, os.path.join(dirty_dir, 'generic/generic_%s.json' % fid))
    save_json(confuse_dict, os.path.join(dirty_dir, 'confuse/confuse_%s.json' % fid))
    print(fid, "over")
