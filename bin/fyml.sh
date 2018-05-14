#/bin/bash

# fyml: flatten yml files to actionable env-vars.
# caller shoudl source this script:
# usage:
#     source $( bin/fyml config.yml )
#
# How it workds: src/fyml.py does the flattening
# which we redirect to a temp file.
# Then return that temp file name (via stdout) so
# the caller will end up sourcing it.

TMP_FILE=env.tmp
src/fyml.py -c "$1" > "$TMP_FILE"
echo "$0: fyml returning $TMP_FILE" >&2
echo "$TMP_FILE"

