from multiprocessing import Pool
from tqdm import tqdm
from argparse import ArgumentParser

from clean.main import main_filter
from clean.filter import Filter
from clean.dataset import dataloader, get_filter_set


def main():
    parser = ArgumentParser()
    parser.add_argument("--tool_dir", type=str,
                        default="/home/wangyida/data/CleanWB/tool_data/", help="Path of the tool data.")
    parser.add_argument("--data_dir", type=str, default="./data/", help="Path of the dataset.")
    parser.add_argument("--out_dir", type=str, default="./data/cleaned_data/", help="Path of the output.")
    parser.add_argument("--dirty_dir", type=str, default="./data/dirty_data/", help="Path of the ouput of dirty cases.")

    args = parser.parse_args()

    simple_loader = dataloader(args.data_dir)
    person_name_set, black_str_set, black_list_set, is_en, confuse_set = get_filter_set(args.tool_dir)
    simple_filter = Filter(person_name_set=person_name_set, black_str_set=black_str_set,
                           black_list_set=black_list_set, confuse_set=confuse_set, is_en=is_en)
    # print("bug tested")
    #loader, path = simple_loader[0]
    #main_filter(simple_filter, loader, path, args.out_dir, args.dirty_dir, False)
    p = Pool(40)
    for loader, path in tqdm(simple_loader):
        p.apply_async(main_filter, args=(simple_filter, loader, path, args.out_dir, args.dirty_dir, False))
    p.close()
    p.join()
    print("main over")


if __name__ == "__main__":
    main()
