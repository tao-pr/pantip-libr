#!/bin/bash

echo Collecting libraries...

pip3 install htmldom
pip3 install couchdb
pip3 install multiprocessing
pip3 install finch

gem install thailang4r
gem install sinatra

echo "[Finished]"