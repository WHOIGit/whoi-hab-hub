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
  image_tag     = "1.9"

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
  memory_size = 256
  timeout     = 300

  # container config
  image_uri     = module.docker_image.image_uri
  package_type  = "Image"
  architectures = ["x86_64"]

  vpc_subnet_ids         = ["subnet-08d09516ed3c309e5"]
  vpc_security_group_ids = [aws_security_group.lambda_sg.id]
  attach_network_policy  = true

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
    }
    OpenSearch = {
      effect    = "Allow",
      actions   = ["es:*"],
      resources = ["arn:aws:es:us-east-1:139464377685:domain/habhub-prod/*"]
    }

  }
}

resource "aws_security_group" "lambda_sg" {
  name        = "lambda_sg"
  description = "Allow TLS inbound traffic and all outbound traffic"
  vpc_id      = "vpc-0f786e98f5cdba188"
}

resource "aws_vpc_security_group_ingress_rule" "allow_tls_ipv4" {
  security_group_id = aws_security_group.lambda_sg.id
  cidr_ipv4         = "0.0.0.0/0"
  #from_port         = 443
  ip_protocol = "-1"
  #to_port           = 443
}

resource "aws_vpc_security_group_egress_rule" "allow_all_traffic_ipv4" {
  security_group_id = aws_security_group.lambda_sg.id
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "-1" # semantically equivalent to all ports
}

resource "aws_vpc_security_group_egress_rule" "allow_all_traffic_ipv6" {
  security_group_id = aws_security_group.lambda_sg.id
  cidr_ipv6         = "::/0"
  ip_protocol       = "-1" # semantically equivalent to all ports
}


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
