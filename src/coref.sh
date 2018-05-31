#!/bin/sh

source ~/573/coref2/bin/activate

export CORE_NLP=stanford-corenlp-full-2018-02-27

python3 -m pynlp -t 600000 &

sleep 10s

python3 coref.py

wget "localhost:9000/shutdown?key=`cat /tmp/corenlp.shutdown`" -O -
