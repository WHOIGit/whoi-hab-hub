data "aws_ecr_authorization_token" "token" {}

provider "docker" {
  registry_auth {
    address  = var.ecr_root
    username = data.aws_ecr_authorization_token.token.user_name
    password = data.aws_ecr_authorization_token.token.password
  }
}

module "docker_image" {
  source = "terraform-aws-modules/lambda/aws//modules/docker-build"

  create_ecr_repo = true
  ecr_repo        = "ingest-class-scores-lambda"

  use_image_tag = true
  image_tag     = "1.3"

  source_path = "${path.module}/../lambdas/ingest-class-scores"

}

#############################################
# Lambda Function (from image)
#############################################

module "lambda_function" {
  source  = "terraform-aws-modules/lambda/aws"
  version = "7.2.1"

  function_name  = "ingest-class-scores-lambda"
  description    = "Ingest classifier scores from H5 files"
  create_package = false
  publish        = true

  # architecture config
  memory_size = 2000
  timeout     = 300

  # container config
  image_uri     = module.docker_image.image_uri
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
    GetS3Objects = {
      effect    = "Allow",
      actions   = ["s3:GetObject"],
      resources = ["*"]
    },

  }
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
