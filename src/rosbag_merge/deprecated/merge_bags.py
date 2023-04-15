#!/usr/bin/env python3
"""

This module has been reduced to aiding in merging bags by writing to an outputfile.
TODO, consolidate the module in bag_stream OR think of way to separate stream from
the looping logic to allow bag merging from this module.

"""
from . import main
import rospy
from rosbag import Bag
from tqdm import tqdm
from icecream import ic
ic.configureOutput(includeContext=True)

def write_to_bag(output_file : Bag, topic : str, msg : any, time :rospy.rostime.Time):
  output_file.write(topic, msg, time)

if __name__ == "__main__":
  main.main(sys.argv[1:])

# explicitly define the outward facing API of this module
__all__ = [write_to_bag.__name__]
