#!/usr/bin/env bash

dnf update -y 
dnf install -y python3-dnf git python3-pip cpio git

# clone source and install splitter
git clone https://gitee.com/openeuler/splitter.git
cd splitter
pip install -r requirements.txt
python3 setup.py install