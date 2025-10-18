# SSM Parameters for API Keys
resource "aws_ssm_parameter" "astra_token" {
  name  = "/${var.app_name}/astra-token"
  type  = "SecureString"
  value = var.astra_db_token
  
  tags = {
    Environment = "production"
    Application = var.app_name
  }
}

resource "aws_ssm_parameter" "astra_endpoint" {
  name  = "/${var.app_name}/astra-endpoint"
  type  = "SecureString"
  value = var.astra_db_endpoint
  
  tags = {
    Environment = "production"
    Application = var.app_name
  }
}

resource "aws_ssm_parameter" "groq_key" {
  name  = "/${var.app_name}/groq-key"
  type  = "SecureString"
  value = var.groq_api_key
  
  tags = {
    Environment = "production"
    Application = var.app_name
  }
}

resource "aws_ssm_parameter" "serper_key" {
  count = var.serper_api_key != "" ? 1 : 0
  name  = "/${var.app_name}/serper-key"
  type  = "SecureString"
  value = var.serper_api_key
  
  tags = {
    Environment = "production"
    Application = var.app_name
  }
}