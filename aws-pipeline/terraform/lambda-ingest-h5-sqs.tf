data "aws_ecr_authorization_token" "token" {}

provider "docker" {
  registry_auth {
    address  = var.ecr_root
    username = data.aws_ecr_authorization_token.token.user_name
    password = data.aws_ecr_authorization_token.token.password
  }
}

module "docker_image_h5" {
  source = "terraform-aws-modules/lambda/aws//modules/docker-build"

  create_ecr_repo = true
  ecr_repo        = "ingest-class-scores-lambda-sqs"

  use_image_tag = true
  image_tag     = "1.5"

  source_path = "${path.module}/../lambdas/ingest-class-scores-sqs"

}

#############################################
# Lambda Function (from image)
#############################################

module "lambda_function_h5" {
  source  = "terraform-aws-modules/lambda/aws"
  version = "7.2.1"

  function_name  = "ingest-class-scores-sqs"
  description    = "Ingest classifier scores from H5 files with SQS"
  create_package = false
  publish        = true

  # architecture config
  memory_size = 200
  timeout     = 180
  # throttle lambda execution to not kill habon-ifcb api with requests
  reserved_concurrent_executions = 2
  ephemeral_storage_size         = 1024

  # container config
  image_uri     = module.docker_image_h5.image_uri
  package_type  = "Image"
  architectures = ["x86_64"]

  # put lambda in VPC to connect to OS
  #vpc_subnet_ids         = [var.subnet_prv1]
  #vpc_security_group_ids = [aws_security_group.lambda_sg_new.id]
  #attach_network_policy  = true

  allowed_triggers = {
    sqs = {
      principal  = "sqs.amazonaws.com"
      source_arn = aws_sqs_queue.main.arn
    }
  }

  create_current_version_allowed_triggers = false

  # cloudwatch
  cloudwatch_logs_retention_in_days = 7
  event_source_mapping = {
    sqs = {
      event_source_arn        = aws_sqs_queue.main.arn
      function_response_types = ["ReportBatchItemFailures"]
      scaling_config = {
        maximum_concurrency = 2

      }
      metrics_config = {
        metrics = ["EventCount"]
      }
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
      resources = ["arn:aws:es:us-east-1:139464377685:domain/habhub-production/*"]
    },
    # Allow failures to be sent to SQS queue
    SQSfailure = {
      effect    = "Allow",
      actions   = ["sqs:SendMessage"],
      resources = [aws_sqs_queue.failure.arn]
    },

  }

  attach_policies    = true
  number_of_policies = 1

  policies = [
    "arn:aws:iam::aws:policy/service-role/AWSLambdaSQSQueueExecutionRole"
  ]

}

# SQS
resource "aws_sqs_queue" "main" {
  name = "ingest-class-scores"
  # The redrive_policy connects the source queue to the DLQ
  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.dlq.arn
    maxReceiveCount     = 1 # Max retries before moving to DLQ
  })
}

resource "aws_sqs_queue" "failure" {
  name                      = "ingest-class-scores-failure"
  message_retention_seconds = 86400 # 1 day
}

resource "aws_sqs_queue" "dlq" {
  name = "ingest-class-scores-dlq"
  # Best practice: DLQ retention should be longer than the source queue
  message_retention_seconds = 172800 # 1 day
}
