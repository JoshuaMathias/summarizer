#-------------------------------------
# Run bin/summarizer_patas
# Sun Apr 22 20:32:23 PDT 2018
# note: that the summarizer_patas value is set up to 
# use the dropbox / acquaint files on patas.
#-------------------------------------
universe        = vanilla
executable      = bin/summarizer_patas_dev
getenv          = true
output          = d4.out
error           = d4.err
log             = d4.log
arguments       = ""
transfer_executable = false
queue
