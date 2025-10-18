variable "app_name" {
  description = "Application name"
  type        = string
  default     = "enterprise-assistant"
}

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-2"
}

variable "astra_db_token" {
  description = "AstraDB application token"
  type        = string
  sensitive   = true
}

variable "astra_db_endpoint" {
  description = "AstraDB API endpoint"
  type        = string
  sensitive   = true
}

variable "groq_api_key" {
  description = "Groq API key"
  type        = string
  sensitive   = true
}

variable "serper_api_key" {
  description = "Serper API key (optional)"
  type        = string
  default     = ""
  sensitive   = true
}