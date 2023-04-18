#! /usr/bin/env python3
import argparse
import glob
import os
import sys

from icecream import ic

from . import bag_stream

ic.configureOutput(includeContext=True)

"""
This main file is meant to help interface users with the python package.

"""


def refine_args(args: argparse.Namespace) -> argparse.Namespace:
    # Refine the arguments to handle simplified inputs such as directories, files with lists of topics, etc.
    retval = args

    # make sequence of topics from a topic file
    if args.topic_file:
        if ("topics" not in args) or (not args.topics):
            args.topics = []
        with open(args.topic_file) as f:
            lines = [line.strip() for line in f]
        args.topics.extend(lines)
        ic(args.topics)
    # input files into the respective args Namespace
    if len(args.input_paths):
        for path in args.input_paths:
            for f in os.listdir(path):
                full_file_path = os.path.join(path, f)
                if (f.endswith(".csv")):
                    if "input_csvs" not in args:
                        args.input_csvs = []
                    args.input_csvs.append(full_file_path)
                elif (f.endswith(".bag")):
                    if "input_bags" not in args:
                        args.input_bags = []
                    args.input_bags.append(full_file_path)
    # TODO, if outpath, then join outpath with out file paths, must also do with the csv writer
    no_outbag_actions = (not args.outbag_name) and (args.write_bag)
    if (no_outbag_actions):
        ic("Writing bags requires an outbag suffix.")
    no_input_files = (("input_bags" not in args) or (not len(args.input_bags)))
    args.write_bag = True if args.output_path and args.outbag_name else False
    requesting_write_without_output_path = not args.output_path and (
        args.merge_csvs or args.write_csvs or args.write_bag)
    if (no_outbag_actions or no_input_files or requesting_write_without_output_path):
        if no_outbag_actions:
            ic(no_outbag_actions)
        if no_input_files:
            ic(no_input_files)
        if requesting_write_without_output_path:
            ic(requesting_write_without_output_path)

        create_parser().print_help()
        retval = None  # Invalid args, so make it clear
    return retval


def create_parser() -> argparse.ArgumentParser:
    # Creates the appropriate argument parser (separated out to enable printing helps, etc.)
    # create an argument parser to read arguments from the command line
    parser = argparse.ArgumentParser(description=__doc__)
    # add an argument for the output bag to create
    parser.add_argument('--output_path', '-op',
                        type=str,
                        help='The output path for all outputted files. (global paths)',
                        default="./",
                        )
    parser.add_argument('--outbag_name', '-obn',
                        type=str,
                        help='The output bag name ( file to write to )',
                        default=None,
                        )
    parser.add_argument('--write_bag', action='store_true')
    # add an argument for the sequence of input bags
    parser.add_argument('--input_bags', '-ib',
                        type=str,
                        nargs='+',
                        help='A list of input bag files. (global paths)',
                        default=[],
                        )
    parser.add_argument('--input_paths', '-ip',
                        type=str,
                        nargs='+',
                        help='A list of input directories with bag files. (global paths)',
                        default="./",
                        )
    # add an argument for the topics to filter
    parser.add_argument('--topics', '-t',
                        type=str,
                        nargs='*',
                        help='A sequence of topics to include from the input bags.',
                        default=None,  # or list of strings ['*'],
                        required=False,
                        )
    parser.add_argument('--topic-file', '-f',
                        type=str,
                        help='A file representing a list of topics. One topic per line.',
                        default=None,
                        required=False,
                        )
    parser.add_argument('--exists-ok', '-eo',
                        type=bool,
                        help='A true value will remove the file and prevent rosbags exception if the file exists.',
                        default=True,
                        required=False,
                        )
    return parser


def parse_args(args) -> argparse.Namespace:
    parser = create_parser()
    # Get the arguments from the argument parser and return
    return parser.parse_args(args)


def main(args: argparse.Namespace = None):
    if not args:
        args = parse_args(sys.argv[1:])
    # Refine arguments here so simplified args can be used.
    args = refine_args(args)
    if args is None:
        return  # Invalid arguments, return
    bag_stream.main(input_bags=args.input_bags, output_path=args.output_path, outbag_name=args.outbag_name, topics=args.topics, exists_ok=args.exists_ok
                    )


if __name__ == "__main__":
    # Load command line arguments here so that the main function can be called directly from import
    args = parse_args(sys.argv[1:])
    main(args)

# explicitly define the outward facing API of this module (either command line or direct call to the main function)
__all__ = [main.__name__, main]
