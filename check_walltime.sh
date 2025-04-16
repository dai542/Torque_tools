#!/bin/bash

# Show requested walltime and actual used time for finished jobs. 

jobs=`qstat -H | cut -d ' ' -f1 | grep ^[0-9]`
for job in $jobs; do 
    echo "--- $job ---" 
    qstat -fH $job | grep walltime
done
