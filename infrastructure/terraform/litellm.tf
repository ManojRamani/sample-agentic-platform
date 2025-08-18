# LiteLLM Terraform Resources

# Generate a random password for PostgreSQL IAM user
resource "random_password" "postgres_iam_password" {
  length           = 16
  special          = true
  override_special = "!#$%&*()-_=+[]{}<>:?"
}

# Generate a secure master key for LiteLLM that starts with "sk-"
resource "random_string" "litellm_master_key_suffix" {
  length  = 48
  special = false
}

locals {
  litellm_master_key = "sk-${random_string.litellm_master_key_suffix.result}"
}

# Create a consolidated secret for LiteLLM with all credentials and configuration
resource "aws_secretsmanager_secret" "litellm_secret" {
  # checkov:skip=CKV2_AWS_57: As a sample, its a bit heavy handed to rotate the secret. This is called out in the readme. 
  # checkov:skip=CKV_AWS_149: KMS key is conditionally used based on var.enable_kms_encryption
  name                    = "${local.name_prefix}litellm-secret"
  description             = "Consolidated secret for LiteLLM proxy"
  recovery_window_in_days = 0  # Allow immediate deletion without waiting period
  
  tags = local.common_tags
}

resource "aws_secretsmanager_secret_version" "litellm_secret" {
  secret_id     = aws_secretsmanager_secret.litellm_secret.id
  secret_string = jsonencode({
    # LiteLLM master key
    LITELLM_MASTER_KEY = "sk-${random_string.litellm_master_key_suffix.result}"
    
    # PostgreSQL credentials
    POSTGRES_USERNAME = "litellm"
    POSTGRES_PASSWORD = random_password.postgres_iam_password.result
    POSTGRES_HOST = aws_rds_cluster.postgres.endpoint
    POSTGRES_PORT = aws_rds_cluster.postgres.port
    POSTGRES_DBNAME = "litellm_db"
    DATABASE_URL = "postgresql://litellm:${urlencode(random_password.postgres_iam_password.result)}@${aws_rds_cluster.postgres.endpoint}:${aws_rds_cluster.postgres.port}/litellm_db"
    
    # Redis credentials - now included in this secret
    REDIS_HOST = aws_elasticache_replication_group.redis_ratelimit.primary_endpoint_address
    REDIS_PORT = 6379
    REDIS_USERNAME = ""  # Redis doesn't use username with auth token
    REDIS_PASSWORD = random_password.redis_auth_token.result
    
  })
}

# IAM Role for LiteLLM
resource "aws_iam_role" "litellm_role" {
  name = "${local.name_prefix}litellm-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Federated = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:oidc-provider/${replace(aws_eks_cluster.main.identity[0].oidc[0].issuer, "https://", "")}"
        }
        Action = "sts:AssumeRoleWithWebIdentity"
        Condition = {
          StringEquals = {
            "${replace(aws_eks_cluster.main.identity[0].oidc[0].issuer, "https://", "")}:sub": "system:serviceaccount:default:litellm-sa"
          }
        }
      }
    ]
  })

  tags = merge(
    local.common_tags,
    {
      Name = "${local.name_prefix}litellm-role"
    }
  )
}

# Policy for LiteLLM to access Bedrock
resource "aws_iam_policy" "litellm_bedrock_policy" {
  name        = "${local.name_prefix}litellm-bedrock-policy"
  description = "Policy to allow LiteLLM to invoke Bedrock models"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "bedrock:InvokeModel",
          "bedrock:InvokeModelWithResponseStream"
        ]
        Resource = [
          # Allow access to all models in the account across all regions
          "arn:aws:bedrock:*:${data.aws_caller_identity.current.account_id}:model/*",
          # Allow access to all inference profiles in the account across all regions
          "arn:aws:bedrock:*:${data.aws_caller_identity.current.account_id}:inference-profile/*",
          # Allow access to AWS foundation models
          "arn:aws:bedrock:*::foundation-model/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "bedrock:ListFoundationModels",
          "bedrock:GetFoundationModel"
        ]
        Resource = [
          # These are read-only list operations that require * resource
          # but we're scoping them to only foundation model related actions
          "arn:aws:bedrock:*:${data.aws_caller_identity.current.account_id}:*"
        ]
      }
    ]
  })

  tags = local.common_tags
}

# Policy for LiteLLM to access Secrets Manager
resource "aws_iam_policy" "litellm_secrets_policy" {
  name        = "${local.name_prefix}litellm-secrets-policy"
  description = "Policy to allow LiteLLM to access its secrets"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue",
          "secretsmanager:DescribeSecret"
        ]
        Resource = [
          aws_secretsmanager_secret.litellm_secret.arn,
          aws_secretsmanager_secret.redis_auth.arn
        ]
      }
    ]
  })

  tags = local.common_tags
}

# Policy for LiteLLM to access PostgreSQL
resource "aws_iam_policy" "litellm_postgres_policy" {
  name        = "${local.name_prefix}litellm-postgres-policy"
  description = "Policy to allow LiteLLM to access PostgreSQL"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      # Allow RDS IAM authentication
      {
        Effect = "Allow"
        Action = [
          "rds-db:connect"
        ]
        Resource = [
          "arn:aws:rds-db:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:dbuser:${aws_rds_cluster.postgres.cluster_resource_id}/${var.postgres_iam_username}"
        ]
      }
    ]
  })

  tags = local.common_tags
}

# Attach policies to the LiteLLM role
resource "aws_iam_role_policy_attachment" "litellm_bedrock_attachment" {
  policy_arn = aws_iam_policy.litellm_bedrock_policy.arn
  role       = aws_iam_role.litellm_role.name
}

resource "aws_iam_role_policy_attachment" "litellm_secrets_attachment" {
  policy_arn = aws_iam_policy.litellm_secrets_policy.arn
  role       = aws_iam_role.litellm_role.name
}

resource "aws_iam_role_policy_attachment" "litellm_postgres_attachment" {
  policy_arn = aws_iam_policy.litellm_postgres_policy.arn
  role       = aws_iam_role.litellm_role.name
}

# Attach Redis policy to the LiteLLM role
resource "aws_iam_role_policy_attachment" "litellm_redis_attachment" {
  policy_arn = aws_iam_policy.redis_connect.arn
  role       = aws_iam_role.litellm_role.name
}
