#############################################
# Lambda Function (building package locally)
#############################################

module "lambda_function" {
  source  = "terraform-aws-modules/lambda/aws"
  version = "7.2.1"

  function_name                     = "ingest-class-scores-lambda"
  description                       = "Ingest classifier scores from H5 files"
  handler                           = "ingest_class_scores.lambda_handler"
  runtime                           = "python3.11"
  publish                           = true
  cloudwatch_logs_retention_in_days = 14
  architectures                     = ["x86_64"]
  build_in_docker                   = true

  source_path = "${path.module}/../lambdas/ingest-class-scores"

  allowed_triggers = {
    AllowExecutionFromS3Bucket = {
      service    = "s3"
      source_arn = module.s3_bucket.s3_bucket_arn
    }
  }

  layers = [
    "arn:aws:lambda:us-east-1:139464377685:layer:h5py-python-layer:1",
  ]
}

#############################################
# Lambda Layer (install Python dependencies)
#############################################

module "lambda_layer" {
  source  = "terraform-aws-modules/lambda/aws"
  version = "7.2.1"

  create_layer = true

  layer_name               = "python-h5py-numpy-layer"
  description              = "H5py and Numpy Python layer (pip install)"
  compatible_runtimes      = ["python3.11"]
  compatible_architectures = ["x86_64"]
  runtime                  = "python3.11" # Runtime is required for "pip install" to work
  build_in_docker          = true

  source_path = [
    {
      path             = "${path.module}/../lambdas/dependencies/h5py-numpy"
      pip_requirements = true     # Will run "pip install" with default "requirements.txt" from the path
      prefix_in_zip    = "python" # required to get the path correct
    }
  ]
}

###################
# S3 bucket with notification
###################

module "s3_bucket" {
  source  = "terraform-aws-modules/s3-bucket/aws"
  version = "4.1.0"

  bucket        = "habhub.cnn-classifier-files"
  force_destroy = true
  acl           = "private"

  control_object_ownership = true
  object_ownership         = "ObjectWriter"
}

module "s3_notification" {
  source  = "terraform-aws-modules/s3-bucket/aws//modules/notification"
  version = "4.1.0"

  bucket = module.s3_bucket.s3_bucket_id

  eventbridge = true

  lambda_notifications = {
    lambda1 = {
      function_arn  = module.lambda_function.lambda_function_arn
      function_name = module.lambda_function.lambda_function_name
      events        = ["s3:ObjectCreated:*"]
      //filter_prefix = "data/"
      //filter_suffix = ".json"
    }
  }
}
