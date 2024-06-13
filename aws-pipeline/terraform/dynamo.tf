module "dynamodb_table" {
  source = "terraform-aws-modules/dynamodb-table/aws"

  name                        = "habhub-bins-metadata"
  hash_key                    = "pid"
  deletion_protection_enabled = false
  table_class                 = "STANDARD"

  attributes = [
    {
      name = "pid"
      type = "S"
    }
  ]

  tags = {
    Project = var.project_name
  }
}
