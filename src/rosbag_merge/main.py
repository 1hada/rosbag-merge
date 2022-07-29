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

def parse_args(args)-> argparse.Namespace:
    # create an argument parser to read arguments from the command line
    parser = argparse.ArgumentParser(description=__doc__)
    # add an argument for the output bag to create
    parser.add_argument('--global_output_path', '-gop',
        type=str,
        help='The output path for all outputted files. (global paths)',
        default=None,
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
        default=[],
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
    # get the arguments from the argument parser
    args = parser.parse_args(args)
    # make sequence of topics from a topic file
    if args.topic_file :
      if not args.topics:
        args.topics = []
      with open(args.topic_file) as f:
          lines = [line.strip() for line in f]
      args.topics.extend(lines)
      ic(args.topics)
    # input files into the respective args Namespace
    if len(args.input_paths):
      for path in  args.input_paths:
        for f in os.listdir(path):
          full_file_path = os.path.join(path,f)
          if (f.endswith(".csv")):
            args.input_csvs.append(full_file_path)
          elif (f.endswith(".bag")):
            args.input_bags.append(full_file_path)
    # TODO, if outpath, then join outpath with out file paths, must also do with the csv writer
    no_outbag_actions = (not args.outbag_name) and (args.write_bag) 
    if (no_outbag_actions):
      ic("Writing bags requires an outbag suffix.")
    no_input_files = (not len(args.input_bags)) and (not len(args.input_csvs))
    args.write_bag = True if args.global_output_path and args.outbag_name else False
    requesting_write_without_output_path =  not args.global_output_path and (args.merge_csvs or args.write_csvs or args.write_bag)
    no_csvs_to_merge = (not (len(args.input_csvs) or args.write_csvs)) and args.merge_csvs
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
      parser.print_help()
      exit(1)
    return args

def main():
  args = sys.argv[1:]
  args = parse_args(args)
  if(args.merge_csvs):
    # TODO , see why can't make csvs and merge in the same call to main
    expecting_to_merge_newly_written_csvs = args.write_csvs and (not len(args.input_csvs))
    if(expecting_to_merge_newly_written_csvs):
      # gather newly made csvs from the output path
      args.input_csvs.extend(glob.glob(os.path.join(args.global_output_path,"*-single-topic.csv")))
    csv_merge.merge_csvs_using_dask(args.input_csvs)
  else:
    bag_stream.main(input_bags=args.input_bags 
                    ,write_bag=args.write_bag
                    ,write_csvs=args.write_csvs
                    ,global_output_path=args.global_output_path
                    ,outbag_name=args.outbag_name
                    ,topics=args.topics
                    ) 

if __name__ == "__main__":
  args = sys.argv[1:]
  args = parse_args(args)
  if(args.merge_csvs):
    # TODO , see why can't make csvs and merge in the same call to main
    expecting_to_merge_newly_written_csvs = args.write_csvs and (not len(args.input_csvs))
    if(expecting_to_merge_newly_written_csvs):
      # gather newly made csvs from the output path
      args.input_csvs.extend(glob.glob(os.path.join(args.global_output_path,"*-single-topic.csv")))
    csv_merge.merge_csvs_using_dask(args.input_csvs)
  else:
    bag_stream.main(input_bags=args.input_bags 
                    ,write_bag=args.write_bag
                    ,write_csvs=args.write_csvs
                    ,global_output_path=args.global_output_path
                    ,outbag_name=args.outbag_name
                    ,topics=args.topics
                    ) 

# explicitly define the outward facing API of this module
__all__ = [ main.__name__ ]
