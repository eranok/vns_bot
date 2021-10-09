#!/usr/bin/bash

lynx_exist=$(which lynx)
if [[ -z "$lynx_exist" ]]; then
	echo "LYNX is not installed. Please install to proceed with convertation"
	echo "  Debian based: sudo apt install lynx"
	echo "  Arch based:   sudo pacman -Syu lynx"
	exit -1
fi

mkdir -p tests
for file in ./tests_html/*.html; do
	echo "Running for $file"
	filename=$(echo "$file" | sed "s/.*\///")
	output=$(lynx -dump $file)
	output=$(echo "$output" | sed 's/Правильна відповідь:.*/& asdfghjkl/g')
	output=$(echo "$output" | sed '/Текст питання/!d;s//&\n/;s/.*\n//;:a;/ asdfghjkl/bb;$!{n;ba};:b;s//\n&/;P;D')
	output=$(echo "$output" | sed -r 's/\[.[0-9]{1,10}\]//g')
	output=$(echo "$output" | perl -ne 'print unless /\(\*\)/ ... /Коментар/')
	echo "$output" > ./tests/$filename.txt
done
