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
main_args.input_paths = [os.path.join(os.getcwd(),"tests","data","raw")]
main_args.output_path = os.path.join(os.getcwd(),"tests","data")
main_args.outbag_name = "merged_bag"
main_args.topic_file = os.path.join(os.getcwd(),"tests","topic_list.txt")
# remove previous bag
try:
    os.remove(os.path.join(main_args.output_path,"merged_bag.bag"))
    print("% s removed successfully" % path)
except OSError as error:
    print(error)
    print("File path can not be removed")
# Call the function
main(main_args)
