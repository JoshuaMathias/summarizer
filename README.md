<!--
#D3 "README" file

##LING 573 Summarization Group Project  
##summarizer.py v. 2.0 by team #e2jkplusplus  

updated for D3 (jgreve Mon May 14 15:27:25 PDT 2018)
-----------------------------------------------------------

note: the D3 requirements specify a "README" file, so here it is.
We didn't want to assume "README.md" and miss the requirements.
-->

# Summarization System: Deliverable 3

John Greve, Eric Lindberg, Joshua Mathias, and Kekoa Riggin

## Overview

Instructions for running the summarizer code on pandas.
The two examples below show how to run via condor and the command line.

### Change for D3

The rouge score generation has been included with the summarizer
logic so no extra rouge step is required.

This is followed by an overview of the call sequence and a summary
of the configuration details in case you want to run the system on
a different topic set.

## System Prereqs

To run the system your current working directory
needs to be in the project root.

The project root will include directories of .../bin  .../src .../outputs.
In our github source tree it is the summarizer folder.
     https://github.com/JoshuaMathias/summarizer.git

While we recommend invoking .../bin/summarizer_patas directly,
you can invoke various standalone components directly as described
in Optional below.  

Most values are parameterized via config.yml.
The summarizer .../bin/ commands pay attention to the
current config&ast;.yml, which is set in "bin/summarizer_patas"
on line 10:
    export E2JK_CONFIG=bin/config_patas_D3.yml

## Optional Run Methods

This only matters if you want to run the .../bin/summarizer
or .../bin/rouge.sh scripts directly.

For example, to run stand alone rouge scores you will need
to set E2JK_CONFIG to a suitable config&ast;.yml.

For example:

```
$ export E2JK_CONFIG=bin/config_patas_D3.yml
$ bin/summarizer
$ bin/rouge.sh
```

Actually it will base the file name on the $E2JK_CONFIG
release_title, which is just "D3" in .../config_patas_D3.yml
which would write the rouge scores to .../results/D3_rouge_scores.out

The summarizer script uses a legacy -c option from D2 because of
a dependency in its underlying python program.

```
$ export E2JK_CONFIG=bin/config_patas_D3.yml
$ bin/summarizer -c $E2JK_CONFIG
```

## Implementation Details

The .../scripts use e2jk.env to establish the environment variables.
e2jk.env uses the config.yml file specified in the env-var E2JK_CONFIG
to define a family of E2JK_ variables.

e2jk.env uses bin/fyml.sh uses (src/fyml.py) for details.

## Run the D2 Summarizer:

To run via condor:

```
$ cd summarizer
$ condor_submit D3.cmd
$ bin/condor_status.sh
```

The last step is optional (but convenient), hit `^C` to exit the status loop.

Recommended way to run via command line (on patas or dryas):

```
$ cd summarizer
$ bin/summarizer_patas > run.dat
```

Despite the name of the script it will work on patas or dryas.
Status messages are written to STDERR.

The actually summaries are written to STDOUT as well as the
individual docset outputs/D2 files.  "run.dat" is just a
convenience to gather operational data.

## Additional Information

### Software Architecture
There are three main components to the software, the Topic Loader, the Summarizer, and the Summary output. These correspond to the Model, Controller, and View in the system, with the Summarizer invoking the Topic Loader to create the Document and Article data, which is then presented as the Summaries.

### Call Sequence

```
-------------------------------------
  (i)   bin/summarizer_patas
 (ii)   bin/summarizer bin/config_patas_d3.yml
(iii)   src/summarizer.py -c bin/config_patas.yml

(i) is just a stub shell that has a suitable D3 config file hardwired into it.
(ii) passes the config file from (i) into (iii).
     NOTE: (ii) will also clear the outputs/D3 directory.
```

## Configuration Information

We're using &ast;.yml (yml) files to say which paths to use.

If you want to point at a different topic index you can change
the value on the aquaint_topic_index property.

So far we have only tested with `devtest/GuidedSumm10_test_topics.xml`
so we don't know if other topic.xml files will cause issues.

### sample config file (used for D3)

```
+--- begin config_patas_D3.yml ---
| project:
|     team_id: 9
|     release_title: D3
| aquaint:
|     aquaint1_directory: /dropbox/17-18/573/AQUAINT
|     aquaint2_directory: /dropbox/17-18/573/AQUAINT-2
| 
|     aquaint_doc_dir: 
|     aquaint_topic_index: /dropbox/17-18/573/Data/Documents/devtest/GuidedSumm10_test_topics.xml
| 
| output:
|     summary_dir: outputs/D3
|     #results_dir: outputs/results   (jgreve: not supposed to be child of outputs)
|     results_dir: results
|     max_words: 100
| 
| # Test configuration to read one article file only
| # one_config:
| #    article_file: aquaint_test1/nyt/1999/19990330_NYT
+--- end config_patas_D3.yml ---
```

## Logging note

Logging is configured with standard python logging and a .../logging.yaml file
in the project folder.

The default log level is INFO.

Python logging messages will be written to "err.log" (levels >= WARNING)
and "info.log" (all active levels).
