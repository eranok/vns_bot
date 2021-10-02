#!/usr/bin/bash

lynx_exist=$(which lynx)
if [[ -z "$lynx_exist" ]]; then
	echo "LYNX is not installed. Please install to proceed with convertation"
	echo "Debian based: sudo apt-get install lynx"
	exit -1
fi

mkdir -p tests
for file in ./tests_html/*.html; do
	echo "Running for $file"
	filename=$(echo "$file" | sed "s/.*\///")
	output=$(lynx -dump $file)
	echo "$output" >> ./tests/$filename.txt
done
