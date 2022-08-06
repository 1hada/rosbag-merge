#! /usr/bin/env python3
from . import bag_stream
from . import csv_merge
import argparse

import os
import sys
import glob 

from icecream import ic
ic.configureOutput(includeContext=True)

"""
This main file is meant to help interface users with the python package.

"""

def refine_args(args:argparse.Namespace)-> argparse.Namespace:
    # Refine the arguments to handle simplified inputs such as directories, files with lists of topics, etc.
    retval = args

    # Handle default arguments
    if "merge_csvs" not in args:
        args.merge_csvs = False
    if "write_csvs" not in args:
        args.write_csvs = False
    if "write_bag" not in args:
        args.write_bag = False

    # make sequence of topics from a topic file
    if args.topic_file :
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
                full_file_path = os.path.join(path,f)
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
    no_input_files = (("input_bags" not in args) or (not len(args.input_bags))) and (("input_csvs" not in args) or (not len(args.input_csvs)))
    args.write_bag = True if args.output_path and args.outbag_name else False
    requesting_write_without_output_path =  not args.output_path and (args.merge_csvs or args.write_csvs or args.write_bag)
    no_csvs_to_merge = (("input_csvs" not in args) or not (len(args.input_csvs) or args.write_csvs)) and args.merge_csvs
    if (no_csvs_to_merge):
        ic("unable to merge non-existent (present tense and future) csvs.")
    if (no_outbag_actions or no_input_files or requesting_write_without_output_path or no_csvs_to_merge):
        if no_outbag_actions : 
            ic(no_outbag_actions)
        if no_input_files : 
            ic(no_input_files)
        if requesting_write_without_output_path : 
            ic(requesting_write_without_output_path)
        if no_csvs_to_merge : 
            ic(no_csvs_to_merge)
        
        create_parser().print_help()
        retval = None  # Invalid args, so make it clear
    return retval


def create_parser()-> argparse.ArgumentParser:
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
    parser.add_argument('--write_csvs', action='store_true')
    parser.add_argument('--merge_csvs', action='store_true')
    # add an argument for the sequence of input bags
    parser.add_argument('--input_bags', '-ib',
        type=str,
        nargs='+',
        help='A list of input bag files. (global paths)',
        default=[],
    )
    parser.add_argument('--input_csvs', '-ic',
        type=str,
        nargs='+',
        help='A list of input csv files. (global paths)',
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
        default=None, # or list of strings ['*'],
        required=False,
    )
    parser.add_argument('--topic-file', '-f',
        type=str,
        help='A file representing a list of topics. One topic per line.',
        default=None,
        required=False,
    )
    return parser


def parse_args(args)-> argparse.Namespace:
    parser = create_parser()
    # Get the arguments from the argument parser and return
    return parser.parse_args(args)
    

def main(args:argparse.Namespace=None):
    if not args:
        args = parse_args(sys.argv[1:])
    # Refine arguments here so simplified args can be used.
    args = refine_args(args)
    if args is None:
        return  # Invalid arguments, return
    if(args.merge_csvs):
        # TODO , see why can't make csvs and merge in the same call to main
        expecting_to_merge_newly_written_csvs = args.write_csvs and (not len(args.input_csvs))
        if(expecting_to_merge_newly_written_csvs):
            # gather newly made csvs from the output path
            args.input_csvs.extend(glob.glob(os.path.join(args.output_path,"*-single-topic.csv")))
            csv_merge.merge_csvs_using_dask(args.input_csvs)
    else:
        bag_stream.main(input_bags=args.input_bags 
                        ,write_bag=args.write_bag
                        ,write_csvs=args.write_csvs
                        ,output_path=args.output_path
                        ,outbag_name=args.outbag_name
                        ,topics=args.topics
                        ) 

if __name__ == "__main__":
    # Load command line arguments here so that the main function can be called directly from import
    args = parse_args(sys.argv[1:])
    main(args)

# explicitly define the outward facing API of this module (either command line or direct call to the main function)
__all__ = [ main.__name__, main ]
