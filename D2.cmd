#-------------------------------------
# Run bin/summarizer_patas
# Sun Apr 22 20:32:23 PDT 2018
# note: that the sumarizer_patas value is set up to 
# use the dropbox / acquate files on patas.
#-------------------------------------
universe        = vanilla
executable      = bin/summarizer_patas
getenv          = true
output          = d2.out
error           = d2.err
log             = d2.log
arguments       = ""
transfer_executable = false
queue
