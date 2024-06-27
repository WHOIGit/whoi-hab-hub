#/bin/bash
# filter by single file extension
aws s3 cp /opt/ifcbdb/ifcbdb/ifcb_data/products/cnn/v3/HABLAB_20240110_Tripos2  s3://habhub.data-pipeline-files/h5-files/HABLAB_20240110_Tripos2 --recursive  --exclude "*" --include "*.h5" --profile habhub-data-pipeline