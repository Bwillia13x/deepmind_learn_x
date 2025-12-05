# AB ESL AI - Terraform Infrastructure

This directory contains Terraform configurations for deploying the AB ESL AI application to AWS.

## Prerequisites

1. [Terraform](https://www.terraform.io/downloads) >= 1.0
2. [AWS CLI](https://aws.amazon.com/cli/) configured with credentials
3. An AWS account with appropriate permissions

## Architecture

The infrastructure includes:

- **VPC**: Private network with public/private subnets
- **ECS Fargate**: Containerized API, teacher portal, and student app
- **RDS PostgreSQL**: Managed database with pgvector extension
- **ElastiCache Redis**: Session and cache storage
- **S3**: Audio file storage
- **ALB**: Application Load Balancer for routing
- **CloudWatch**: Logging and monitoring

## Quick Start

```bash
# Initialize Terraform
terraform init

# Review the plan
terraform plan -var-file="environments/prod.tfvars"

# Apply the configuration
terraform apply -var-file="environments/prod.tfvars"
```

## Environment Variables

Create a `terraform.tfvars` file or use environment-specific files:

```hcl
environment     = "prod"
aws_region      = "ca-central-1"
db_password     = "your-secure-password"
jwt_secret_key  = "your-secure-jwt-secret"
```

## Outputs

After applying, you'll get:

- `api_url`: The API endpoint URL
- `teacher_portal_url`: Teacher portal URL
- `student_app_url`: Student app URL
- `db_endpoint`: RDS database endpoint

## Destroying

```bash
terraform destroy -var-file="environments/prod.tfvars"
```

## Cost Estimation

Approximate monthly costs (ca-central-1):

- ECS Fargate: ~$50-100
- RDS db.t3.small: ~$30
- ElastiCache cache.t3.micro: ~$15
- ALB: ~$20
- S3/CloudWatch: ~$10

Total: ~$125-175/month for dev/staging
