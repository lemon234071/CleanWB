import os
import logging
from tqdm import tqdm
from multiprocessing import Pool
from argparse import ArgumentParser

from clean.rules import main_filter, data_merge, de_ad, bert_clean, de_generic
from clean.filter import Filter
from clean.dataset import dataloader, get_filter_set
from utils import *

logger = logging.getLogger(__file__)


def main():
    parser = ArgumentParser()
    parser.add_argument("--n_p", type=int, default=32, help="Number of subprocess")
    parser.add_argument("--n_degeneric", type=int, default=1000,
                        help="Number of degeneric. Using if not None. (from Dialogpt)")
    parser.add_argument("--tool_dir", type=str, default="/home/wangyida/data/CleanWB/tool_data/",
                        help="Path of the tool data.")

    parser.add_argument("--data_dir", type=str, default="./data/", help="Main data dir.")
    parser.add_argument("--raw_dir", type=str, default="./data/raw/", help="Dir of the raw dataset.")
    args = parser.parse_args()

    logger.info("Preparing")
    dirty_dir = os.path.join(args.data_dir, "drity_data")
    after_dist_dir = os.path.join(args.data_dir, "after_dist")

    simple_loader = dataloader(args.raw_dir)
    person_name_set, black_str_set, black_list_set, is_en, confuse_set = get_filter_set(args.tool_dir)
    simple_filter = Filter(person_name_set=person_name_set, black_str_set=black_str_set,
                           black_list_set=black_list_set, confuse_set=confuse_set, is_en=is_en)

    # single process debug
    # loader, path = simple_loader[0]
    # main_filter(simple_filter, loader, path, after_dist_dir, args.dirty_dir, False)
    logger.info("Rules start")
    p = Pool(args.n_p)
    for loader, path in tqdm(simple_loader):
        p.apply_async(main_filter, args=(simple_filter, loader, path, after_dist_dir, dirty_dir, False, True))
    p.close()
    p.join()

    logger.info("Stage 2 start")
    data = data_merge(after_dist_dir)
    data = bert_clean(data,
                      os.path.join(args.tool_dir, "wangyida_vocab.txt"),
                      os.path.join(args.tool_dir, "safe_inbert.txt"),
                      dirty_dir)
    data = de_ad(data, os.path.join(dirty_dir, "ad.json"))
    if args.n_degeneric:
        data = de_generic(data, dirty_dir, os.path.join(args.tool_dir, "tri_grams.json"), args.n_degeneric)

    save_json(data, os.path.join(args.data_dir, "after_rules.json"))
    logger.info("Classifier start")


if __name__ == "__main__":
    main()
