

### Getting Started


```
pip3 install rosbag-merge
```

 OR

```
python3 -m pip install .
```

This package currently uses icecream as the logger in order to better identify the locations of bugs. Eventually the logging will happen through print.



# Usage

Basic elements for usage are an in path and out path for data being processed and created, respectively.

```--outbag_name```
* Define an outbag name using the flag.

```--input_paths``` 
* Define input paths for the data of interest. (csv or bags)

```--output_path```
* Define where to save newly created data (csv or bags)

```--topics```
* Topics which should be filtered. Use this to speed up all of the processing. To use all topics then simply omit the flag.

```--topic-file```
* Topics which should be filtered. Use this to speed up all of the processing. To use all topics then simply omit the flag. A file representing a list of topics. One topic per line.

> NOTE : More arguments are available if you want to use specific CSV's or Bag files. Run `rosbag-merge -h` for more information.

### Some environment variables

```
export IN_PATH=/path/to/data
export OUT_PATH=/path/to/data
export OUTBAG_NAME=new-bag-name
export INPUT_TOPICS='/topic/namespace_1 /topic/namespace_2 /topic/namespace_3'
```

### Merge Bag Files

Merge all the bag files from the current directory.
```
rosbag-merge --write_bag --outbag_name $OUTBAG_NAME
```

Make a merged bage with all topics.
```
rosbag-merge --input_paths $IN_PATH --output_path $OUT_PATH --outbag_name $OUTBAG_NAME --write_bag
```

To merge bag files with select topics, and make single topics csvs.
```
rosbag-merge --input_paths $IN_PATH --output_path $OUT_PATH --outbag_name $OUTBAG_NAME --topics $INPUT_TOPICS --write_bag 
```

To merge bag files with select topics, and make single topics csvs.
```
rosbag-merge --input_paths $IN_PATH --output_path $OUT_PATH --outbag_name $OUTBAG_NAME --write_bag --write_csvs 
```