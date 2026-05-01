terraform {
  required_version = ">= 1.6"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.40"
    }
    helm = {
      source  = "hashicorp/helm"
      version = ">= 2.13"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = ">= 2.30"
    }
  }
}

provider "aws" {
  region = var.region
  default_tags {
    tags = {
      Project     = "alphaforge"
      Environment = var.environment
      ManagedBy   = "terraform"
    }
  }
}

module "vpc" {
  source              = "./modules/vpc"
  name                = "alphaforge-${var.environment}"
  cidr                = var.vpc_cidr
  azs                 = var.azs
  public_subnet_cidrs = var.public_subnet_cidrs
  private_subnet_cidrs = var.private_subnet_cidrs
}

module "eks" {
  source             = "./modules/eks"
  cluster_name       = "alphaforge-${var.environment}"
  kubernetes_version = var.kubernetes_version
  vpc_id             = module.vpc.vpc_id
  subnet_ids         = module.vpc.private_subnet_ids
  node_instance_types = var.node_instance_types
  desired_size       = var.node_desired_size
  min_size           = var.node_min_size
  max_size           = var.node_max_size
}

module "rds" {
  source            = "./modules/rds"
  identifier        = "alphaforge-${var.environment}"
  vpc_id            = module.vpc.vpc_id
  subnet_ids        = module.vpc.private_subnet_ids
  username          = "alphaforge"
  password          = var.db_password
  instance_class    = var.db_instance_class
  allocated_storage = var.db_allocated_storage
}

module "redis" {
  source       = "./modules/elasticache_redis"
  name         = "alphaforge-${var.environment}"
  vpc_id       = module.vpc.vpc_id
  subnet_ids   = module.vpc.private_subnet_ids
  node_type    = var.redis_node_type
  num_nodes    = var.redis_num_nodes
}

module "s3" {
  source = "./modules/s3"
  bucket = "alphaforge-${var.environment}-artifacts"
}
