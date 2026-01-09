
module "docker_image" {
  source = "terraform-aws-modules/lambda/aws//modules/docker-build"

  create_ecr_repo = true
  ecr_repo        = "ingest-class-scores-lambda"

  use_image_tag = true
  image_tag     = "1.35"

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
  # throttle lambda execution to not kill habon-ifcb api with requests
  reserved_concurrent_executions = 10
  ephemeral_storage_size         = 1024

  # container config
  image_uri     = module.docker_image.image_uri
  package_type  = "Image"
  architectures = ["x86_64"]

  # put lambda in VPC to connect to OS
  #vpc_subnet_ids         = [var.subnet_prv1]
  #vpc_security_group_ids = [aws_security_group.lambda_sg_new.id]
  #attach_network_policy  = true

  allowed_triggers = {
    AllowExecutionFromS3Bucket = {
      service    = "s3"
      source_arn = module.s3_bucket.s3_bucket_arn
    }
  }
  # cloudwatch
  cloudwatch_logs_retention_in_days = 7

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
      resources = ["arn:aws:es:us-east-1:139464377685:domain/habhub-production/*"]
    }

  }
}

resource "aws_security_group" "lambda_sg_new" {
  name        = "lambda_sg_new"
  description = "Allow TLS inbound traffic and all outbound traffic"
  vpc_id      = var.vpc
}

resource "aws_vpc_security_group_egress_rule" "allow_all_traffic_ipv4_new" {
  security_group_id = aws_security_group.lambda_sg_new.id
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "-1" # semantically equivalent to all ports
}

resource "aws_vpc_security_group_egress_rule" "allow_all_traffic_ipv6_new" {
  security_group_id = aws_security_group.lambda_sg_new.id
  cidr_ipv6         = "::/0"
  ip_protocol       = "-1" # semantically equivalent to all ports
}



