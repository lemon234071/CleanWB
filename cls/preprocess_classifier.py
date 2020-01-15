import jieba
import random
from tqdm import tqdm
random.seed(2019)


def process_bert():
    path = "/home/wangyida/data_wash/data/tool_data/cleaned_qa_pairs_800k.txt"
    with open(path, 'r', encoding='UTF-8') as f:
        data = [i.strip() for i in f.readlines() if len(i) > 0]
    data_out = []
    for line in tqdm(data):
        line_list = line.strip().split('\t')
        post = [" ".join(jieba.lcut(seq)) for seq in line_list[:-1]]
        post = " ; ".join(post)
        label = int(line_list[-1])
        new_line = [str(label), '\t', post]
        new_str = "".join(new_line)
        data_out.append(new_str)

    random.shuffle(data_out)
    train = data_out[:-10000]
    test = data_out[-10000:]
    train_str = "\n".join(train)
    with open('./data/data.train', 'w', encoding='UTF-8') as f:
        f.write(train_str)
    test_str = "\n".join(test)
    with open('./data/data.test', 'w', encoding='UTF-8') as f:
        f.write(test_str)
    label = ["0", "1"]
    label_str = "\n".join(label)
    with open('./data/data.label', 'w', encoding='UTF-8') as f:
        f.write(label_str)


def process_bert_SEP():
    path = "/home/wangyida/data_wash/data/tool_data/cleaned_qa_pairs_800k.txt"
    with open(path, 'r', encoding='UTF-8') as f:
        data = [i.strip() for i in f.readlines() if len(i) > 0]
    data_out = []
    for line in tqdm(data):
        line_list = line.strip().split('\t')
        post = [" ".join(jieba.lcut(seq)) for seq in line_list[:-1]]
        post = " [SEP] ".join(post)
        label = int(line_list[-1])
        new_line = [str(label), '\t', post]
        new_str = "".join(new_line)
        data_out.append(new_str)

    random.shuffle(data_out)
    train = data_out[:-10000]
    test = data_out[-10000:]
    train_str = "\n".join(train)
    with open('./data/SEP.train', 'w', encoding='UTF-8') as f:
        f.write(train_str)
    test_str = "\n".join(test)
    with open('./data/SEP.test', 'w', encoding='UTF-8') as f:
        f.write(test_str)
    label = ["0", "1"]
    label_str = "\n".join(label)
    with open('./data/SEP.label', 'w', encoding='UTF-8') as f:
        f.write(label_str)


def process_fasttext():
    path = "/home/wangyida/data_wash/data/tool_data/cleaned_qa_pairs_800k.txt"
    with open(path, 'r', encoding='UTF-8') as f:
        data = [i.strip() for i in f.readlines() if len(i) > 0]
    data_out = []
    for line in tqdm(data):
        line_list = line.strip().split('\t')
        post = [" ".join(jieba.lcut(seq)) for seq in line_list[:-1]]

        post = " ; ".join(post)
        label = int(line_list[-1])
        new_line = ["__label__", str(label), " ", post]
        new_str = "".join(new_line)
        data_out.append(new_str)

    random.shuffle(data_out)
    train = data_out[:-10000]
    test = data_out[-10000:]
    train_str = "\n".join(train)
    with open('/home/wangyida/data_wash/data/tool_data/cls/fasttext.train', 'w', encoding='UTF-8') as f:
        f.write(train_str)
    test_str = "\n".join(test)
    with open('/home/wangyida/data_wash/data/tool_data/cls/fasttext.test', 'w', encoding='UTF-8') as f:
        f.write(test_str)


def process_fasttext1():
    path = "/home/wangyida/bert_based_task/bert/BERTFinetuner/data/data.train"
    with open(path, 'r', encoding='UTF-8') as f:
        data = [i.strip() for i in f.readlines() if len(i) > 0]
    data_out = []
    for line in data:
        line_list = line.split("\t")
        new_line = "".join(["__label__", line_list[0], " ", line_list[1]])
        data_out.append(new_line)
    train_str = "\n".join(data_out)
    with open('/home/wangyida/data_wash/data/tool_data/cls/fasttext_1.train', 'w', encoding='UTF-8') as f:
        f.write(train_str)

    path = "/home/wangyida/bert_based_task/bert/BERTFinetuner/data/data.test"
    with open(path, 'r', encoding='UTF-8') as f:
        data = [i.strip() for i in f.readlines() if len(i) > 0]
    data_out = []
    for line in data:
        line_list = line.split("\t")
        new_line = "".join(["__label__", line_list[0], " ", line_list[1]])
        data_out.append(new_line)
    test_str = "\n".join(data_out)
    with open('/home/wangyida/data_wash/data/tool_data/cls/fasttext_1.test', 'w', encoding='UTF-8') as f:
        f.write(test_str)


def main():
    #process_fasttext()
    process_fasttext1()


if __name__ == '__main__':
    main()
