"""

Helps stream bag data and apply bag writing capabilities.

"""

from argparse import Namespace
from tqdm import tqdm
import os
from rosbags.rosbag1 import Reader, Writer, ReaderError, WriterError
from rosbags.typesys import get_types_from_msg
from contextlib import ExitStack, contextmanager
import heapq

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


def read_messages(paths, topics=None, start_time=None, end_time=None, wipe_typesys=False):
    """Iterate chronologically raw BagMessage for topic from paths."""
    # pylint: disable=too-many-locals

    if wipe_typesys:
        backup = types.FIELDDEFS.copy()
        for key in list(types.FIELDDEFS.keys()):
            if key not in [
                'builtin_interfaces/msg/Time',
                'builtin_interfaces/msg/Duration',
                'std_msgs/msg/Header',
            ]:
                types.FIELDDEFS.pop(key)
        MSGDEFCACHE.clear()

    with ExitStack() as stack:
        if wipe_typesys:
            stack.callback(
                lambda:
                (types.FIELDDEFS.clear() or types.FIELDDEFS.update(backup) or MSGDEFCACHE.clear()),
            )
        bags = [stack.enter_context(open_rosbag1(path)) for path in paths]
        if wipe_typesys:
            typs = {}
            for bag in bags:
                for rconn in bag.connections:
                    typs.update(get_types_from_msg(rconn.msgdef, rconn.msgtype))
            register_types(typs)
        gens = [
            bag.messages(
                connections=[x for x in bag.connections if x.topic in topics],
                start=start_time,
                stop=end_time,
            ) for bag in bags
        ]
        prev_time = 0
        for connection, time, data in heapq.merge(*gens, key=lambda x: x[1]):
            assert time >= prev_time, (repr(time), repr(prev_time))
            yield connection, time, data
            prev_time = time

def main(input_bags : 'list[str]', topics : 'list[str]', output_path : str, outbag_name : str):
    try:
        full_bag_path = os.path.join(output_path,outbag_name+".bag")
        # open the output bag in an automatically closing context
        with Writer(full_bag_path) as output_bag:
            conn_map = {}
            # process messages across input bag(s)
            for connection, timestamp, rawdata in read_messages(input_bags, topics=topics):
                try:
                    # we're saving by topic, may cause an error if the md5sum changes
                    conn_map[connection.topic] = output_bag.add_connection(connection.topic, connection.msgtype, connection.msgdef, connection.md5sum, connection.ext.callerid, connection.ext.latching)
                except WriterError:
                     pass
            for connection, timestamp, rawdata in read_messages(input_bags, topics=topics):
                # write this message to the output bag
                output_bag.write(conn_map[connection.topic], timestamp, rawdata)    
    except KeyboardInterrupt:
        pass
    finally:
        print("Done.")
