terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.0.0, < 6.0.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes",
      version = ">=2.38.0"
    }
    helm = {
      source  = "hashicorp/helm"
      version = ">=3.0.2"
    }
  }

  backend "s3" {
    bucket = "emcq-terraform-state"
    key    = "emcq_kubernetes_v2/terraform.tfstate"
    region = "us-east-1"

  }
}