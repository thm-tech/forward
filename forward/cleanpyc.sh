#!/bin/sh
find . -name '*pyc' -type f -print -exec rm -rf {} \;
rm ./log/data/*.log -rf
rm output_josn.txt -f
