"""
Example script that calls the main function directly

Note that this needs to be moved to the main directory prior to running since Python does not seem to enjoy
 parallel directories.
Also, create data in the tests directory per the structure below prior to running.
"""

from src.rosbag_merge.main import main
import argparse


main_args = argparse.Namespace()
main_args.input_paths = ["./tests/data/raw"]
main_args.global_output_path = "./tests/data"
main_args.outbag_name = "merged_bag"
main_args.write_bag = True
main_args.topic_file = "./tests/topic_list.txt"
# Call the function
main(main_args)
