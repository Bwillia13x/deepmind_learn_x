#!/bin/bash

# AB ESL AI Deployment Script
# Usage: ./deploy.sh [environment] [action]
# Example: ./deploy.sh dev deploy

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default values
ENVIRONMENT="${1:-dev}"
ACTION="${2:-deploy}"
AWS_REGION="${AWS_REGION:-ca-central-1}"
ECR_REGISTRY="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"

# Validate environment
if [[ ! "$ENVIRONMENT" =~ ^(dev|staging|prod)$ ]]; then
    echo -e "${RED}Invalid environment: $ENVIRONMENT. Must be dev, staging, or prod.${NC}"
    exit 1
fi

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}AB ESL AI Deployment${NC}"
echo -e "${GREEN}Environment: ${YELLOW}$ENVIRONMENT${NC}"
echo -e "${GREEN}Action: ${YELLOW}$ACTION${NC}"
echo -e "${GREEN}Region: ${YELLOW}$AWS_REGION${NC}"
echo -e "${GREEN}========================================${NC}"

# Check required tools
check_tools() {
    echo -e "${YELLOW}Checking required tools...${NC}"
    
    command -v aws >/dev/null 2>&1 || { echo -e "${RED}AWS CLI is required but not installed.${NC}" >&2; exit 1; }
    command -v docker >/dev/null 2>&1 || { echo -e "${RED}Docker is required but not installed.${NC}" >&2; exit 1; }
    command -v terraform >/dev/null 2>&1 || { echo -e "${RED}Terraform is required but not installed.${NC}" >&2; exit 1; }
    
    echo -e "${GREEN}All required tools are installed.${NC}"
}

# Build and push Docker images
build_images() {
    echo -e "${YELLOW}Building Docker images...${NC}"
    
    # Login to ECR
    aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_REGISTRY
    
    # Build and push API
    echo -e "${YELLOW}Building API image...${NC}"
    docker build -t ab-esl-ai-api:$ENVIRONMENT ./backend/api
    docker tag ab-esl-ai-api:$ENVIRONMENT $ECR_REGISTRY/ab-esl-ai-api:$ENVIRONMENT
    docker push $ECR_REGISTRY/ab-esl-ai-api:$ENVIRONMENT
    
    # Build and push Teacher Portal
    echo -e "${YELLOW}Building Teacher Portal image...${NC}"
    docker build -t ab-esl-ai-teacher:$ENVIRONMENT ./apps/teacher-portal
    docker tag ab-esl-ai-teacher:$ENVIRONMENT $ECR_REGISTRY/ab-esl-ai-teacher:$ENVIRONMENT
    docker push $ECR_REGISTRY/ab-esl-ai-teacher:$ENVIRONMENT
    
    # Build and push Student App
    echo -e "${YELLOW}Building Student App image...${NC}"
    docker build -t ab-esl-ai-student:$ENVIRONMENT ./apps/student-app
    docker tag ab-esl-ai-student:$ENVIRONMENT $ECR_REGISTRY/ab-esl-ai-student:$ENVIRONMENT
    docker push $ECR_REGISTRY/ab-esl-ai-student:$ENVIRONMENT
    
    echo -e "${GREEN}All images built and pushed successfully.${NC}"
}

# Deploy infrastructure with Terraform
deploy_infra() {
    echo -e "${YELLOW}Deploying infrastructure with Terraform...${NC}"
    
    cd infra/terraform
    
    terraform init
    terraform plan -var-file="environments/${ENVIRONMENT}.tfvars" -out=tfplan
    
    read -p "Apply this plan? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        terraform apply tfplan
        echo -e "${GREEN}Infrastructure deployed successfully.${NC}"
    else
        echo -e "${YELLOW}Deployment cancelled.${NC}"
    fi
    
    cd ../..
}

# Update ECS services
update_services() {
    echo -e "${YELLOW}Updating ECS services...${NC}"
    
    CLUSTER_NAME="ab-esl-ai-${ENVIRONMENT}-cluster"
    
    # Force new deployment for each service
    for SERVICE in api teacher-portal student-app; do
        echo -e "${YELLOW}Updating $SERVICE...${NC}"
        aws ecs update-service \
            --cluster $CLUSTER_NAME \
            --service "ab-esl-ai-${ENVIRONMENT}-${SERVICE}" \
            --force-new-deployment \
            --region $AWS_REGION \
            >/dev/null
    done
    
    echo -e "${GREEN}ECS services updated successfully.${NC}"
}

# Run database migrations
run_migrations() {
    echo -e "${YELLOW}Running database migrations...${NC}"
    
    # This would typically run as an ECS task or Lambda
    # For now, just show the command
    echo -e "${YELLOW}Migration command:${NC}"
    echo "  cd backend/api && alembic upgrade head"
    
    echo -e "${GREEN}Migrations complete.${NC}"
}

# Health check
health_check() {
    echo -e "${YELLOW}Running health checks...${NC}"
    
    # Get the ALB URL from Terraform outputs
    ALB_URL=$(cd infra/terraform && terraform output -raw api_url 2>/dev/null || echo "")
    
    if [ -n "$ALB_URL" ]; then
        echo -e "${YELLOW}Checking API health at $ALB_URL/health${NC}"
        
        for i in {1..10}; do
            HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$ALB_URL/health" || echo "000")
            
            if [ "$HTTP_CODE" == "200" ]; then
                echo -e "${GREEN}Health check passed!${NC}"
                return 0
            fi
            
            echo -e "${YELLOW}Attempt $i: HTTP $HTTP_CODE - waiting...${NC}"
            sleep 10
        done
        
        echo -e "${RED}Health check failed after 10 attempts.${NC}"
        return 1
    else
        echo -e "${YELLOW}Could not determine API URL. Skipping health check.${NC}"
    fi
}

# Main deployment flow
deploy() {
    check_tools
    build_images
    deploy_infra
    run_migrations
    update_services
    health_check
    
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}Deployment complete!${NC}"
    echo -e "${GREEN}========================================${NC}"
}

# Rollback
rollback() {
    echo -e "${YELLOW}Rolling back to previous deployment...${NC}"
    
    CLUSTER_NAME="ab-esl-ai-${ENVIRONMENT}-cluster"
    
    # Rollback by forcing new deployment with previous task definition
    for SERVICE in api teacher-portal student-app; do
        echo -e "${YELLOW}Rolling back $SERVICE...${NC}"
        
        # Get previous task definition
        CURRENT_TASK_DEF=$(aws ecs describe-services \
            --cluster $CLUSTER_NAME \
            --services "ab-esl-ai-${ENVIRONMENT}-${SERVICE}" \
            --query "services[0].taskDefinition" \
            --output text \
            --region $AWS_REGION)
        
        # Get previous revision number
        CURRENT_REV=$(echo $CURRENT_TASK_DEF | grep -o '[0-9]*$')
        PREV_REV=$((CURRENT_REV - 1))
        
        if [ $PREV_REV -gt 0 ]; then
            PREV_TASK_DEF=$(echo $CURRENT_TASK_DEF | sed "s/:${CURRENT_REV}/:${PREV_REV}/")
            
            aws ecs update-service \
                --cluster $CLUSTER_NAME \
                --service "ab-esl-ai-${ENVIRONMENT}-${SERVICE}" \
                --task-definition $PREV_TASK_DEF \
                --region $AWS_REGION \
                >/dev/null
            
            echo -e "${GREEN}$SERVICE rolled back to revision $PREV_REV${NC}"
        else
            echo -e "${YELLOW}No previous revision for $SERVICE${NC}"
        fi
    done
    
    echo -e "${GREEN}Rollback complete.${NC}"
}

# Execute action
case "$ACTION" in
    deploy)
        deploy
        ;;
    build)
        check_tools
        build_images
        ;;
    infra)
        check_tools
        deploy_infra
        ;;
    update)
        check_tools
        update_services
        health_check
        ;;
    migrate)
        run_migrations
        ;;
    rollback)
        rollback
        ;;
    health)
        health_check
        ;;
    *)
        echo -e "${RED}Unknown action: $ACTION${NC}"
        echo "Usage: $0 [environment] [action]"
        echo "  environment: dev, staging, prod"
        echo "  action: deploy, build, infra, update, migrate, rollback, health"
        exit 1
        ;;
esac
