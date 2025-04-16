#!/bin/bash

jobs=`qstat -H | cut -d ' ' -f1 | grep ^[0-9]`
for job in $jobs; do
    echo "--- $job ---"
    qstat -fH $job | grep -E 'resources_used.ncpus|Resource_List.ncpus'
done
