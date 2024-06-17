
module "docker_image_metadata" {
  source = "terraform-aws-modules/lambda/aws//modules/docker-build"

  create_ecr_repo = true
  ecr_repo        = "ingest-metadata-adc-files-lambda"

  use_image_tag = true
  image_tag     = "1.8"

  source_path = "${path.module}/../lambdas/ingest-metadata-adc-files"

}

#############################################
# Lambda Function (from image)
#############################################

module "lambda_function_metadata" {
  source  = "terraform-aws-modules/lambda/aws"
  version = "7.2.1"

  function_name  = "ingest-metadata-adc-files-lambda"
  description    = "Ingest ml_analyzed metadata from ADC files"
  create_package = false
  publish        = true

  # architecture config
  memory_size = 256
  timeout     = 300

  # container config
  image_uri     = module.docker_image_metadata.image_uri
  package_type  = "Image"
  architectures = ["x86_64"]

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
      actions = ["s3:GetObject"],
      resources = [
        "${module.s3_bucket.s3_bucket_arn}",
        "${module.s3_bucket.s3_bucket_arn}/*"
      ]
    },

  }
}
