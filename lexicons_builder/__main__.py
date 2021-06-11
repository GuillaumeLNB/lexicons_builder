#!/usr/bin/env python3
"""
Main script to retrive data from the web, wordnet and language models
"""

import argparse
import logging
import sys

from touch import touch


# logging.basicConfig(
#     level=logging.DEBUG,
#     format="[%(asctime)s] -[%(name)s] - [%(levelname)s] - %(message)s",
#     handlers=[logging.StreamHandler()],
# )


from lexicons_builder import build_lexicon
from .wordnet_explorer.explorer import assert_lang_supported_by_wordnet


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
        choices=("ttl", "txt", "xlsx"),
        default="txt",
        help="The wanted output format (txt with indentation, ttl or xlsx)",
    )
    parser.add_argument(
        "-o",
        "--out-file",
        dest="out_file",
        help="The file where the results will be stored",
    )
    parser.add_argument(
        "-w",
        "--wordnet",
        dest="wordnet",
        action="store_true",
        help="search on wordnet using nltk",
    )
    parser.add_argument(
        "--web",
        dest="web",
        help="Search on dictionnaries online",
        action="store_true",
    )
    args = parser.parse_args(arguments)
    # print(args.__dict__)

    if len(arguments) <= 1 or not args.words:
        parser.print_help()
        raise parser.error(f"no word provided or no enough arguments")

    if not args.out_file:
        raise parser.error(f"out file required !")

    if not args.lang:
        raise parser.error(f"language required !")

    if (
        not args.web
        and not args.wordnet
        and not args.wolf_path
        and not args.nlp_model_paths
    ):
        raise parser.error(
            f"Nowhere to took up for words. Perharps you wanted to add the --web option?"
        )

    return args


def main(arguments):

    args = parse_args(arguments)

    if args.wordnet:
        assert_lang_supported_by_wordnet(args.lang)

    touch(args.out_file)

    main_graph = build_lexicon(
        args.words,
        args.lang,
        args.depth,
        nlp_model_paths=args.nlp_model_paths,
        wolf_path=args.wolf_path,
        wordnet=args.wordnet,
        web=args.web,
    )

    if args.format == "txt":
        main_graph.to_text_file(args.out_file)
    elif args.format == "xlsx":
        main_graph.to_xlsx_file(args.out_file)
    elif args.format == "ttl":
        with open(args.out_file, "w") as f:
            print(main_graph, file=f)
            logging.info(f"{args.out_file}")

    logging.info(f"done. {len(main_graph)} unique synonyms found")


if __name__ == "__main__":

    sys.exit(main(sys.argv[1:]))
