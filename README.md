# zappa-configuratoin-generator

This is a package that automatically generates the `zappa_settings.json` from options or ENVIRONMENT VARIABLES.

## Usage

This script is expected to be called from within your deployment environment with the necessary permissions.

> NOTE: 

### Create deployment bot user

### Create Deployment Role

## CI/CI Required ENVIRONMENT VARIABLES

For deployment from CircleCI  following "Environment Variables" need to be added to the CircleCI project Settings-> Environment Variables:

> These variables *must* be manually set and assigned in the circleci environment.


```
AWS_ACCESS_ROLE_ARN={Deployment Role ARN}
AWS_DEFAULT_REGION=ap-northeast-1
AWS_PROFILE={Profile for Deployment Role}
CIRCLECI_AWS_ACCESS_KEY_ID={circleci-bot User Key}
CIRCLECI_AWS_SECRET_ACCESS_KEY={circleci-bot User Secret}
LAMBDA_EXECUTION_ROLENAME=annotation-zappa-boto3-client-role
SENTRY_DSN={https://*key*:*pass*@sentry.io/*project*}

Project specifc variables 
> These will be parsed so that the `ZAPPAPROJ_` prefix will be removed and the remaining ENVIRONMENT VARIABLE will be available to your lambda function.
```
```
# Zappa Project Required ENVIRONMENT VARIABLES
ZAPPAPROJ_AWS_ACCESS_KEY_ID={AWS_ACCESS_KEY_ID for AnnotationTool Project S3 Bucket Access}
ZAPPAPROJ_AWS_SECRET_ACCESS_KEY={AWS_SECRET_ACCESS_KEY for AnnotationTool Project S3 Bucket Access}
ZAPPAPROJ_DB_USER={AnnotationTool Database User}
ZAPPAPROJ_DB_NAME={AnnotationTool Database Name}
ZAPPAPROJ_DB_PASSWORD={AnnotationToll Database Password}
ZAPPAPROJ_APPLICATION_HOST={Host address where backend application runs}
```

### VPC Required Environment Variables

The following variables are required when using zappa/lambda with a VPC (for RDS or Elasticache access):

- VPC_CONFIG_SECURITYGROUPIDS
- VPC_CONFIG_SUBNETIDS

Where:

The ids are given as comma separated values (no spaces).