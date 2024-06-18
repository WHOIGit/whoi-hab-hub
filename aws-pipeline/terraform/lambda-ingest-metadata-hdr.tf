
#############################################
# Lambda Function (from local files)
#############################################

module "lambda_function_metadata_2" {
  source  = "terraform-aws-modules/lambda/aws"
  version = "7.2.1"

  function_name  = "ingest-metadata-hdr-files-lambda"
  description    = "Ingest lat/long metadata from HDR files"
  handler        = "app.lambda_handler"
  runtime        = "python3.12"
  create_package = true
  publish        = true

  source_path = "../lambdas/ingest-metadata-hdr-files"

  # architecture config
  memory_size = 200
  timeout     = 300

  allowed_triggers = {
    AllowExecutionFromS3Bucket = {
      service    = "s3"
      source_arn = module.s3_bucket.s3_bucket_arn
    }
  }

  # role and policy config
  attach_policy_statements = true
  policy_statements = {
    DynamoItems = {
      effect    = "Allow",
      actions   = ["dynamodb:GetItem", "dynamodb:PutItem", "dynamodb:UpdateItem"],
      resources = [module.dynamodb_table.dynamodb_table_arn]
    },
    GetS3Objects = {
      effect  = "Allow",
      actions = ["s3:GetObject", "s3:DeleteObject"],
      resources = [
        "${module.s3_bucket.s3_bucket_arn}",
        "${module.s3_bucket.s3_bucket_arn}/*"
      ]
    },

  }
}
