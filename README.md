# summarizer
LING 573 Summarization Group Project

## How to run

Our project can be run with condor using `condor_submit D2.cmd`.  

On patas one can run `bin/summarizer_patas`, which will use a patas specific configuration file (bin/config_patas.yml).  

Configuration files specify file locations and max_words. See src/config.yml for an example.  
A config file for use from the main project directory is config_un.yml.  

To call directly using Python:  `python3 src/summarizer`

usage: summarizer.py [-h] [-c CONFIG]  

summarizer.py v. 2.0 by team #e2jkplusplus  

optional arguments:  
  -h, --help            show this help message and exit  
  -c CONFIG, --config CONFIG  
                        Config File(s)  

## Overview

Instructions for running the D2 summarizer code on pandas.
The two examples below show how to run via condor and the command line.
See "Post-run" for how to run rouge scores.

This is followed by an overview of the call sequence and a summary
of the configuration details in case you want to run the system on
a different topic set.


## Prereqs

To run the system your current working directory needs to be in the project root.
Typically we extract into a summarizer folder.


## Post-run

To get D2 rouge scores you need to run
+---------------------
|    $ bin/rouge.sh
+---------------------

This will write the rouge scores to .../results/D2_rouge_scores.out


## Run the D2 Summarizer

To run via condor:
+---------------------
|  $ cd summarizer
|  $ condor_submit D2.cmd
|  $ bin/condor_status.sh
+---------------------
The last step is optional (but convenient), hit ^C to exit the status loop.


Recommended way to run via command line (on patas or dryas):
+---------------------
|  $ cd summarizer
|  $ bin/summarizer_patas > run.dat
+---------------------
Despite the name of the script it will work on patas or dryas.
Status messages are written to STDERR.
The actually summaries are written to STDOUT as well as the
individual docset outputs/D2 files.  "run.dat" is just a
convenience to gather operational data.

## Additional Information

    Call Sequence
-------------------------------------
  (i)   bin/summarizer_patas
 (ii)   bin/summarizer bin/config_patas.yaml
(iii)   src/summarizer.py -c bin/config_patas.yaml

(i) is just a stub shell that has a suitable D2 config file hardwired into it.
(ii) passes the config file from (i) into (iii).
     NOTE: (ii) will also clear the outputs/D2 directory.


## Configuration Information

We're using \*.yml (yaml) files to say which paths to use.
If you want to point at a different topic index you can change
the value on the aquaint_topic_index property.
So far we have only tested with "devtest/GuidedSumm10_test_topics.xml"
so we don't know if other topic.xml files will cause issues.


sample config file (used for D2)
+--- begin config_patas.yml ---
| project:
|     team_id: 9
|     release_title: D2
| aquaint:
|     aquaint1_directory: /dropbox/17-18/573/AQUAINT
|     aquaint2_directory: /dropbox/17-18/573/AQUAINT-2
| 
|     aquaint_doc_dir: 
|     aquaint_topic_index: /dropbox/17-18/573/Data/Documents/devtest/GuidedSumm10_test_topics.xml
| 
| output:
|     summary_dir: output/D2
|     results_dir: output/results
|     max_words: 100
| 
| # Test configuration to read one article file only
| # one_config:
| #    article_file: aquaint_test1/nyt/1999/19990330_NYT
+--- end config_patas.yml ---

--- end README ---
