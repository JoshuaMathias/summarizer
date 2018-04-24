#!/bin/bash

# helper script to run ROUGE for D2.
# Generates D2-specific rouge in "outputs/d2_roughe.xml" config file with src/create_config.py.
# Then runs the *.pl rouge logic.

set -u
# blow up on undefined env-vars

ROUGE_OUT=results/D2_rouge_scores.out
# used below in perl part

#set -x

# Python part, creates the rouge config file for perl.
MYDATA_DIR="outputs/D2"
MODELDATA_DIR="/dropbox/17-18/573/Data/models/devtest"
# for use with:
#    /dropbox/17-18/573/Data/Documents/devtest/GuidedSumm10_test_topics.xml
# See: bin/summarizer_patas
#ROUGE_CONFIG=rouge_run_ex.xml
ROUGE_CONFIG=outputs/d2_rouge.xml

src/create_config.py "$MYDATA_DIR" "$MODELDATA_DIR" "$ROUGE_CONFIG"
# from create_config.py:
#    p.add_argument('MYDATA_DIR',    help="The directory containing your system's outputs.")
#    p.add_argument('MODELDATA_DIR', help='The directory containing the model summaries.')
#    p.add_argument('CONFIG_OUT',    help='Output filename for the generated config.')

# Perl part... runs rouge logic.
ROUGE_HOME="/dropbox/17-18/573/code/ROUGE"
ROUGE_PROG=$ROUGE_HOME/ROUGE-1.5.5.pl 
ROUGE_DATA_DIR=$ROUGE_HOME/data
$ROUGE_PROG -e "$ROUGE_DATA_DIR" -a -n 4 -x -m -c 95 -r 1000 -f A -p 0.5 -t 0 -l 100 -s -d "$ROUGE_CONFIG" > "$ROUGE_OUT"

TABLE_OUT="${ROUGE_OUT}.csv"
src/rouge_tableize.py "$ROUGE_OUT" > "$TABLE_OUT"

echo "$0: wrote results to $ROUGE_OUT, see $TABLE_OUT for excel-friendly version."

