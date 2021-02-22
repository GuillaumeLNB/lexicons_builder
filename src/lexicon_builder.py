#!/usr/bin/env python3
"""
Main script to retrive data from the web, wordnet and language models
"""

import argparse
import logging
import sys

from touch import touch

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] -[%(name)s] - [%(levelname)s] - %(message)s",
    handlers=[logging.StreamHandler()],
)


from nlp_model_explorer.explorer import explore_nlp_model
from scrapper.scrappers import get_synonyms_from_scrappers
from wordnet_explorer.explorer import explore_wordnet, explore_wolf


def parse_args(arguments):
    parser = argparse.ArgumentParser(
        description="lexicon_builder, a tool to build lexicons"
    )
    parser.add_argument(
        "words", nargs="+", help="The word(s) we want to get synonyms from"
    )
    parser.add_argument("-l", "--lang", help="The word language")
    parser.add_argument(
        "-m",
        "--nlp-model",
        dest="nlp_model_paths",
        help="The path to the nlp model(s)",
        nargs="+",
    )
    parser.add_argument(
        "-wolf",
        "--wolf-path",
        dest="wolf_path",
        help="The path to WOLF (French wordnet)",
        type=str,
    )
    parser.add_argument(
        "-d",
        "--depth",
        dest="depth",
        type=int,
        default=2,
        help="The depth we want to dig in the models, websites, ...",
    )
    parser.add_argument(
        "-f",
        "--format",
        dest="format",
        choices=("ttl", "txt"),
        default="txt",
        help="The wanted output format (txt with indentation or ttl)",
    )
    parser.add_argument(
        "-o",
        "--out-file",
        dest="out_file",
        help="the outfile where the results will be stored",
    )
    parser.add_argument(
        "-w",
        "--wordnet",
        dest="wordnet",
        action="store_true",
        help="search on wordnet using nltk",
    )
    args = parser.parse_args(arguments)
    print(args.__dict__)

    if len(arguments) <= 1 or not args.words:
        parser.print_help()
        raise parser.error(f"no word provided or no enough arguments")

    if not args.out_file:
        raise parser.error(f"out file required !")

    if not args.lang:
        raise parser.error(f"language required !")
    return args


def main(arguments):

    args = parse_args(arguments)

    touch(args.out_file)

    graphs = []
    for word in args.words:
        if args.nlp_model_paths:
            for model in args.nlp_model_paths:
                # looking for words in nlp models
                logging.info(
                    f"exploring model '{model}' with word '{word}' at {args.depth} depth"
                )
                graphs.append(explore_nlp_model(word, model, args.depth))
        # looking for words online
        logging.info(f"looking up synonyms for word '{word}' at depth {args.depth}")
        graphs.append(get_synonyms_from_scrappers(word, args.lang, args.depth))
        # looking for word with WOLF
        if args.wolf_path:
            logging.info(f"exploring WOLF with word '{word}' at depth {args.depth}")
            graphs.append(explore_wolf(word, args.wolf_path, args.depth))
        # looking for word with WORDNET
        if args.wordnet:
            logging.info(f"exploring WORNET with word '{word}' at depth {args.depth}")
            graphs.append(explore_wordnet(word, args.lang, args.depth))

    # merging the graphs
    main_graph = graphs[0]
    for g in graphs[1:]:
        main_graph += g

    if args.format == "txt":
        main_graph.to_text_file(args.out_file)
    elif args.format == "ttl":
        with open(args.out_file, "w") as f:
            print(main_graph, file=f)
            logging.info(f"{args.out_file}")

    logging.info(f"done. {len(main_graph)} unique synonyms found")


if __name__ == "__main__":

    sys.exit(main(sys.argv[1:]))
