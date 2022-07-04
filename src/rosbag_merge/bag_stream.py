
#!/usr/bin/env python3
"""

Helps stream bag data and apply csv and bag writing capabilities.

"""

from argparse import Namespace
from rosbag import Bag
from tqdm import tqdm
import os

from . import rosbag_to_csv
from . import merge_bags

CSVS = rosbag_to_csv.CsvStreams

# inspired from : https://github.com/Kautenja/rosbag-tools/blob/master/merge.py , which has no LICENSE information and is not maintained
def stream(input_bag: Bag, output_bag: Bag, topics: list = ["*"], args: Namespace = None, input_bag_filename: str = None) -> None:
    """Stream data from an input bag to an output bag.

    :param input_bag: the input bag to stream from
    :param output_bag: the output bag to write data to
    :param topics: a list of the topics to include

    :return: None
    """
    prog_bar_update_interval = 100
    msg_count = 0
    # create a progress bar for iterating over the messages in the bag
    with tqdm(total=input_bag.get_message_count(topic_filters=topics), unit='message') as prog:
        # iterate over the messages in this input bag
        for topic, msg, time in input_bag.read_messages(topics=topics):
            if (output_bag):
                # write this message to the output bag
                merge_bags.write_to_bag(output_bag, topic, msg, time)
            if (args.write_csvs):
                # write this message to the output csv
                CSVS.write_data(topic,msg,time,input_bag_filename,args.global_output_path)
            # increment the counter of included messages
            msg_count += 1
            if ( 0 == msg_count % prog_bar_update_interval):
                # update the progress bar with a single iteration
                prog.update(100)
                # update the progress bar post fix text with statistics
                prog.set_postfix(msg_count=msg_count, prog_bar_update_interval=prog_bar_update_interval)
    prog.close()

def stream_iter(args : Namespace , output_bag: Bag=None) -> None:
    """Iterate over the input files

    :param args: args which are used for path data.
    :param output_bag: the output bag to write data to

    :return: None
    """
    for filename in tqdm(args.input_bags, unit='bag'):
        # open the input bag with an automatically closing context
        with Bag(filename, 'r') as input_bag:
            # stream the input bag to the output bag
            stream(input_bag, output_bag = output_bag, topics=args.topics, args=args, input_bag_filename=filename)

def main(args : Namespace ):
    try:
        if(args.write_bag):
            full_bag_path = os.path.join(args.global_output_path,args.outbag_name+".bag")
            # open the output bag in an automatically closing context
            with Bag(full_bag_path, 'w') as output_bag:
                stream_iter(args, output_bag)
        else:
            stream_iter(args)
    except KeyboardInterrupt:
        pass
    finally:
        if(args.write_csvs):
            CSVS.close_streams()