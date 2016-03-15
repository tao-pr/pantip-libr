#!/bin/bash

echo Collecting libraries...

pip3 install argparse
pip3 install htmldom
pip3 install couchdb
pip3 install multiprocessing
pip3 install pika

gem install thailang4r
gem install sinatra

mkdir -p data/hasher/
mkdir -p data/cluster/

echo "export PANTIPLIBR=$(pwd)"

echo "[Finished]"