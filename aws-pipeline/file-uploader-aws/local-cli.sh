#/bin/bash

aws s3 cp /Volumes/brosnahan/primary/cell_imaging/ifcb/ak/ s3://habhub.data-pipeline-files/ak/ --recursive  --exclude "*" --include "*.adc"