"""

Helps stream bag data and apply bag writing capabilities.

"""

import heapq
import os
from argparse import Namespace
from contextlib import ExitStack, contextmanager

from rosbags.rosbag1 import Reader, ReaderError, Writer, WriterError
from rosbags.typesys import get_types_from_msg
from tqdm import tqdm

"""
Copyright open_rosbag1 and read_messages comes from marv_robotics
https://gitlab.com/ternaris/marv-robotics/-/blob/master/code/marv-robotics/marv_robotics/bag.py#L360
# Copyright 2016 - 2018  Ternaris.
# SPDX-License-Identifier: AGPL-3.0-only
"""


@contextmanager
def open_rosbag1(path):
    try:
        with Reader(path) as bag:
            yield bag
    except ReaderError:
        raise ReaderError(
            (
                f'Unindexed bag file: {path}\n'
                '  File was not copied in full or recording did not finish properly\n'
                '  Use `rosbag reindex` to index what is there.'
            ),
        ) from None


def read_messages(paths, topics=None, start_time=None, end_time=None):
    """Iterate chronologically raw BagMessage for topic from paths."""
    # pylint: disable=too-many-locals
    with ExitStack() as stack:
        bags = [stack.enter_context(open_rosbag1(path)) for path in paths]
        gens = []
        for bag in bags:
            valid_connections = []
            if (topics is None):
                # connect to all topics
                valid_connections = [x for x in bag.connections]
            else:
                valid_connections = [
                    x for x in bag.connections if x.topic in topics]
            gens.append(
                bag.messages(
                    connections=valid_connections,
                    start=start_time,
                    stop=end_time,
                )
            )
        prev_time = 0
        for connection, time, data in heapq.merge(*gens, key=lambda x: x[1]):
            assert time >= prev_time, (repr(time), repr(prev_time))
            yield connection, time, data
            prev_time = time


def main(input_bags: 'list[str]', topics: 'list[str]', output_path: str, outbag_name: str, exists_ok: bool):
    try:
        full_bag_path = os.path.join(output_path, outbag_name+".bag")
        # clean up the preexisting bag when the exists_okay flag is present
        if (exists_ok and os.path.exists(full_bag_path)):
            os.remove(full_bag_path)
            for bag_name in input_bags:
                if (os.path.basename(bag_name) == outbag_name+".bag"):
                    input_bags.remove(bag_name)

        # open the output bag in an automatically closing context
        with Writer(full_bag_path) as output_bag:
            conn_map = {}
            # process messages across input bag(s)
            for connection, timestamp, rawdata in read_messages(input_bags, topics=topics):
                try:
                    # we're saving by topic, may cause an error if the md5sum changes
                    conn_map[connection.topic] = output_bag.add_connection(
                        connection.topic, connection.msgtype, connection.msgdef, connection.md5sum, connection.ext.callerid, connection.ext.latching)
                except WriterError:
                    pass
            for connection, timestamp, rawdata in read_messages(input_bags, topics=topics):
                # write this message to the output bag
                output_bag.write(
                    conn_map[connection.topic], timestamp, rawdata)
    except KeyboardInterrupt:
        pass
    finally:
        print("Done.")
