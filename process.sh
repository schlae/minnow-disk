#!/bin/bash
for i in {0..31}
do
	python minnow_raw.py track$i.csv > track_data_$i.txt
done
