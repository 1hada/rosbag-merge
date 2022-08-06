#!/usr/bin/env python3

from datetime import datetime
import io
import os
import yaml
import rospy
from icecream import ic

"""

Helps write ros msgs to csv

ATTENTION if a ros messages lists/tuple size is variable , then list values csv columns will not be aligned

"""

class __CsvStreams():
    def __init__(self):
        self.streamdict = dict()
        self.output_file_format = "%p%t%k.csv"
        self.flatten_data_containers = True
        self.verbose = False
        # if a message has a new line character, we retain csv readability by replacing '\n'
        self.replace_newline_char = True
        self.newline_char_replacement = '<-NEW-LINE->>,<<-NEW-LINE>' # using new line as csv but retaining history of new line existence

    def write_data(self, topic: str, msg: object, time: rospy.rostime.Time , input_bag_file : str, output_path: str,use_header: bool = True):
        """Write data to a csv file.

        :param topic: the topic name
        :param msg: the ros msg
        :param input_bag_file: The input bag file name which is used to construct the output csv name
        :param output_path: The global path to write the csv with.
        :param write_header: a bool to write a header or not.

        :return: None
        """
        stream = self.get_stream(topic,msg,input_bag_file, output_path, use_header)
        # DatetimeIndex format
        date_time_str = datetime.fromtimestamp(
                time.to_time()).strftime('%Y-%m %d %H:%M:%S.%f')
        stream.write(date_time_str)
        self.message_to_csv(stream, msg)
        stream.write('\n')

    def get_stream(self, topic: str, msg : object, input_bag_file : str, output_path: str, write_header: bool = True) -> io.TextIOWrapper:
        """Open/access a file stream, write a header in the file, and return it.

        :param topic: the topic name
        :param msg: the ros msg
        :param input_bag_file: The input bag file name which is used to construct the output csv name
        :param output_path: The global path to write the csv with.
        :param write_header: a bool to write a header or not.

        :return: A file ptr/stream which has been opened.
        """
        if topic in self.streamdict:
            stream = self.streamdict[topic]
        else:
            # the input bag name is used to write the outputted csv
            outpath_with_file = os.path.join(output_path, os.path.basename( input_bag_file ))
            stream = open(
                self.format_csv_filename(
                    self.output_file_format,
                    outpath_with_file,
                    topic),
                'w')
            self.streamdict[topic] = stream
            # header
            if write_header:
                # write time without topic header since tim eis assumed global and can be used as an index
                stream.write("time")
                connector = '_'
                csv_topic_header_prefix = topic.replace('/', connector).lstrip(connector)
                self.message_type_to_csv(stream
                                        ,msg
                                        ,parent_content_name=csv_topic_header_prefix)
                stream.write('\n')
        if( self.verbose ):
            ic(type(stream)) # type(stream): <class '_io.TextIOWrapper'>
            ic(type(msg)) # type(msg): <class 'tmpkk3h4l5a._sensor_msgs__NavSatFix'>
        return stream
        
    def close_streams(self):
        for s in self.streamdict.values():
            if(self.verbose):
                ic(s)
            s.close

    # inspired from : https://github.com/AtsushiSakai/rosbag_to_csv
    def message_to_csv(self, stream: io.TextIOWrapper, msg : any):
        """Writes the csv data with comma seperated values

        :param stream: StringIO or TextIOWrapper
        :param msg: a ros msg

        :return: None
        """
        is_list = type(msg) == list
        is_bytes = type(msg) == bytes
        is_some_pointcloud_msg = "PointCloud" in str( type(msg))
        if (self.verbose):
            ic(type(msg))
        try:
            # if type tuple then it's been seen to be array of type. not sur eif onlye numbers
            for s in type(msg).__slots__:
                val = msg.__getattribute__(s)
                if (self.verbose):
                  ic(type(msg).__slots__)
                  # ic(val)
                  ic(s)
                if( is_some_pointcloud_msg ):
                    # TODO, easier to process pointcloud data through other means
                    val = "N/A"
                self.message_to_csv(stream, val)
        except BaseException as e:
            # AttributeError : type object '<TYPE>' has no attribute '__slots__'
            msg_str = str(msg)
            is_potentially_yaml = (not is_bytes) and msg_str.find(":") != -1
            if ( is_potentially_yaml and not is_list ):
                try:
                    # assumption that data is in yaml format
                    msg_dict = yaml.safe_load(msg_str)
                    # dictionary keys may be unordered and thus require more overhead to make sure,
                    #  is  TODO to write the header correctly and then make sure the values are always inputted in that order
                    msg_str = str(msg_dict).replace(',',"<WAS-COMMA>")
                except (yaml.parser.ParserError, Exception) as e:
                    msg_str = "N/A"
                    if (self.verbose):
                        ic(e)
            if ((not is_bytes) and msg_str.find(",") != -1):
                if self.flatten_data_containers:
                    if type(msg) == tuple:
                        msg_str = msg_str.strip("(")
                        msg_str = msg_str.strip(")")
                        msg_str = msg_str.strip(" ")
                    elif type(msg) == list:
                        msg_str = msg_str.strip("[")
                        msg_str = msg_str.strip("]")
                        msg_str = msg_str.strip(" ")
                    elif type(msg) == dict:
                        # TODO
                        pass
                else:
                    msg_str = "\"" + msg_str + "\""
            if( (not is_bytes) and self.replace_newline_char):
                msg_str = msg_str.replace('\n',self.newline_char_replacement)
                if (self.verbose):
                    ic(e)
            stream.write("," + msg_str)
            if (self.verbose):
              ic(e)

    # inspired from : https://github.com/AtsushiSakai/rosbag_to_csv
    def message_type_to_csv(self, stream : io.TextIOWrapper, msg : any, parent_content_name : str =""):
        """Makes the header

        :param stream: StringIO or TextIOWrapper
        :param msg: a ros msg

        :return: a file name which is formatted to let users distinguish the csv files.
        """
        is_list = type(msg) == list
        is_bytes = type(msg) == bytes
        is_some_pointcloud_msg = "PointCloud" in str( type(msg))
        try:
            for s in type(msg).__slots__:
                val = msg.__getattribute__(s)
                if (self.verbose):
                  ic(type(msg).__slots__)
                  # ic(val)
                  ic(s)
                if( is_some_pointcloud_msg ):
                    # TODO, easier to process pointcloud data through other means
                    val = "N/A"
                self.message_type_to_csv(stream, val, ".".join(
                    [parent_content_name, s]))
        except BaseException as e:
            # AttributeError : type object '<TYPE>' has no attribute '__slots__'
            # check if there will be a message that needs to columns for it's comma separated iterable
            if self.flatten_data_containers:
                msg_str = str(msg)
                is_potentially_yaml = (not is_bytes) and msg_str.find(":") != -1
                if is_potentially_yaml and (not is_list):
                    try:
                        # assumption that data is in yaml format
                        msg_dict = yaml.safe_load(msg_str)
                        # dictionary keys may be unordered and thus require more overhead to make sure,
                        #  is  TODO to write the header correctly and then make sure the values are always inputted in that order
                        msg_str = str(msg_dict).replace(',',"<WAS-COMMA>")
                    except (yaml.parser.ParserError, Exception) as e:
                        msg_str = "N/A"
                        if (self.verbose):
                            ic(e,parent_content_name)
                if ((not is_bytes) and msg_str.find(",") != -1):
                    msg_str = msg_str.strip("([])")
                    msg_str = msg_str.strip(" ")
                    msg_li= msg_str.split(',')
                    for idx in range(len(msg_li)):
                        # make an array_idx key which can be searched for and used to parse+evaluate idx info
                        stream.write(f",{parent_content_name}.array_idx_{idx}")
                    return
            stream.write("," + parent_content_name)
            if (self.verbose):
              ic(e)

    # inspired from : https://github.com/AtsushiSakai/rosbag_to_csv
    def format_csv_filename(self, form, full_file_path, topic):
        """A helper to get a formmated filename.

        :param form: the format which defines the saved csv
        :param full_file_path: The global path to write the csv with.
        :param topic: the topic name

        :return: a file name which is formatted to let users distinguish the csv files.
        """
        # global seq
        if form is None:
            # path, topic, file_content_key
            form = "%p%t%k.csv"
            return "Convertedbag.csv"
        file_name_without_extension = os.path.splitext(full_file_path)[0]
        # input full file path
        form = form.replace("%p",file_name_without_extension)
        # input the topic name with hyphens
        form = form.replace("%t",topic.replace('/', '-'))
        # input a unique identifier for single topic csv's, and mark the end of a topic name 
        single_topic_statement = "-single-topic"
        formatted_name = form.replace('%k', single_topic_statement)
        return formatted_name


CsvStreams = __CsvStreams()
# explicitly define the outward facing API of this module
__all__ = [ CsvStreams ]
