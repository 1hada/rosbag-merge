"""
Example script that calls the main function directly

From the cloned rosbag-merge directory :

  python3 -m pip install .
  python3 examples/main_direct.py

TODO automate tests via workflow or via toml. 
Avoiding setup.py since it is to be considered deprecated.
"""

from rosbag_merge.main import main
import argparse
import os

main_args = argparse.Namespace()
main_args.input_paths = [f"{os.getcwd()}/tests/data/raw"]
main_args.output_path = f"{os.getcwd()}/tests/data"
main_args.outbag_name = "merged_bag"
main_args.write_bag = True
main_args.topic_file = f"{os.getcwd()}/tests/topic_list.txt"
# Call the function
main(main_args)
