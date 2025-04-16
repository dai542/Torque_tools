#!/bin/bash

# Show requested memory and actual used memory for finished jobs. 
# (Ignore vmem)

jobs=`qstat -H | cut -d ' ' -f1 | grep ^[0-9]`
for job in $jobs; do 
    echo "--- $job ---"
    qstat -fH $job | grep '\.mem' 
done
