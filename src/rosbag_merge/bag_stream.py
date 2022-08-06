
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
def stream(input_bag: Bag, topics: list = ["*"], output_bag: Bag=None, input_bag_filename: str=None, write_csvs : bool=False, output_path : str="") -> None:
    """Stream data from an input bag to an output bag.

    :param input_bag: the input bag to stream from
    :param topics: a list of the topics to include
    :param output_bag: the output bag to write data to
    :param input_bag_filename: used to write the csv name
    :param write_csvs: bool to determine whether to write csvs.
    :param topics: a list of the topics to include
    :param output_path: The global path to write the csv with.

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
            if (write_csvs):
                # write this message to the output csv
                CSVS.write_data(topic,msg,time,input_bag_filename,output_path)
            # increment the counter of included messages
            msg_count += 1
            if ( 0 == msg_count % prog_bar_update_interval):
                # update the progress bar with a single iteration
                prog.update(100)
                # update the progress bar post fix text with statistics
                prog.set_postfix(msg_count=msg_count, prog_bar_update_interval=prog_bar_update_interval)
    prog.close()

def stream_iter(input_bags : 'list[str]', topics : 'list[str]'=["*"], output_bag: Bag=None, write_csvs : bool=False, output_path : str=False) -> None:
    """Iterate over the input files

    :param input_bags: a list of bag names to write data to.
    :param topics: a list of the topics to include
    :param output_bag: the output bag to write data to
    :param write_csvs: bool to determine whether to write csvs.
    :param output_path: The global path to write the csv with.

    :return: None
    """
    for filename in tqdm(input_bags, unit='bag'):
        # open the input bag with an automatically closing context
        with Bag(filename, 'r') as input_bag:
            # stream the input bag to the output bag
            stream(input_bag, topics=topics, output_bag=output_bag, input_bag_filename=filename, write_csvs=write_csvs, output_path=output_path)

def main(input_bags : 'list[str]', topics : 'list[str]', write_bag : bool, write_csvs : bool, output_path : str, outbag_name : str):
    try:
        if(write_bag):
            full_bag_path = os.path.join(output_path,outbag_name+".bag")
            # open the output bag in an automatically closing context
            with Bag(full_bag_path, 'w') as output_bag:
                stream_iter(input_bags, topics = topics, output_bag = output_bag, write_csvs=write_csvs, output_path=output_path)
        else:
            stream_iter(input_bags=input_bags, topics = topics, write_csvs=write_csvs, output_path=output_path)
    except KeyboardInterrupt:
        pass
    finally:
        if(write_csvs):
            CSVS.close_streams()
