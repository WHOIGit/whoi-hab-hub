###################
# S3 bucket with notification
###################

module "s3_bucket" {
  source  = "terraform-aws-modules/s3-bucket/aws"
  version = "4.1.0"

  bucket        = "habhub.data-pipeline-files"
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

  sqs_notifications = {
    sqs1 = {
      queue_arn     = aws_sqs_queue.main.arn
      events        = ["s3:ObjectCreated:*"]
      filter_suffix = ".h5"

      #      queue_id =  aws_sqs_queue.main.id // optional
    }
  }
  /*
  lambda_notifications = {
    lambda1 = {
      function_arn  = module.lambda_function.lambda_function_arn
      function_name = module.lambda_function.lambda_function_name
      events        = ["s3:ObjectCreated:*"]
      //filter_prefix = "data/"
      filter_suffix = ".h5"
    }
    lambda2 = {
      function_arn  = module.lambda_function_metadata.lambda_function_arn
      function_name = module.lambda_function_metadata.lambda_function_name
      events        = ["s3:ObjectCreated:*"]
      //filter_prefix = "data/"
      filter_suffix = ".adc"
    }
    lambda3 = {
      function_arn  = module.lambda_function_metadata_2.lambda_function_arn
      function_name = module.lambda_function_metadata_2.lambda_function_name
      events        = ["s3:ObjectCreated:*"]
      //filter_prefix = "data/"
      filter_suffix = ".hdr"
    }
  }
  */
}


# IAM User for S3 access
resource "aws_iam_user" "prod_bucket" {
  name = "${var.project_name}-s3-bucket"
}

resource "aws_iam_user_policy" "prod_bucket" {
  user = aws_iam_user.prod_bucket.name
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "s3:*",
        ]
        Effect = "Allow"
        Resource = [
          "${module.s3_bucket.s3_bucket_arn}",
          "${module.s3_bucket.s3_bucket_arn}/*"
        ]
      },
    ]
  })
}

/*
resource "aws_iam_access_key" "prod_bucket" {
  user = aws_iam_user.prod_bucket.name
}
*/
