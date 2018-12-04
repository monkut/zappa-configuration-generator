# zappa-configuratoin-generator

This is a package that automatically generates the `zappa_settings.json` from options or ENVIRONMENT VARIABLES.

## Usage

This script is expected to be called from within your deployment environment using a role or user with the necessary AWS permissions.

Example `zappa_settings.json` file generation:

```
# Install this package (master)
pip install boto3 git+https://github.com/monkut/zappa-configuration-generator

# Execution package script to autogenerate 
# -- Assumes you have previously created or run `zappa init` and `zappa deploy` to create buckets and Execution Role
# -- {STACK NAME} = Stack name created on initial `zappa deploy` 
python3.6 -m gappa.settings.generate --stack-name {STACK NAME} --stage {STAGE NAME} --zappa-parameters project_name={PROJECT NAME} s3_bucket={S3 BUCKET NAME} > ./zappa_settings.json
```

### Create deployment bot user

> TODO

### Create Deployment Role

> TODO

## ENVIRONMENT VARIABLES

Environment variables are used for both deployment environment configuration and application configuration.


### CI/CD Environment Variables

For deployment from CircleCI  following "Environment Variables" need to be added to the CircleCI project Settings-> Environment Variables:


> These variables *must* be manually set and assigned in the circleci environment.

```
AWS_ACCESS_ROLE_ARN={Deployment Role ARN}
AWS_DEFAULT_REGION=ap-northeast-1
AWS_PROFILE={Profile for Deployment Role}
CIRCLECI_AWS_ACCESS_KEY_ID={circleci-bot User Key}
CIRCLECI_AWS_SECRET_ACCESS_KEY={circleci-bot User Secret}
LAMBDA_EXECUTION_ROLENAME=annotation-zappa-boto3-client-role
VPC_CONFIG_SECURITYGROUPIDS
VPC_CONFIG_SUBNETIDS
SENTRY_DSN={https://*key*:*pass*@sentry.io/*project*}
```

#### VPC Required Environment Variables

The following variables are required when using zappa/lambda with a VPC (for RDS or Elasticache access):

- VPC_CONFIG_SECURITYGROUPIDS
- VPC_CONFIG_SUBNETIDS

Where:

    The ids are given as comma separated values (no spaces).


Example:
```
VPC_CONFIG_SECURITYGROUPIDS=sg-xxxxx,sg-yyyyy
VPC_CONFIG_SUBNETIDS=subnet-zzzz,subnet-iiii
```

### Application Environment Variables 

Application Environment Variables are passed to your application (lambda).

ENVIRONMENT VARIABLES with the prefix, `ZAPPAPROJ_` or `ZAPPAPROJAWS_`, will be parsed such that the prefix (`ZAPPAPROJ_`, `ZAPPAPROJAWS_`) is removed and provided to the lambda function.

Where:

- `ZAPPAPROJAWS_` prefixed envars will populate the `zappa_settings[stage]['environment_variables']` zappa_settings.json fields.
- `ZAPPAPROJ_` prefixed envars will populate the `zappa_settings[stage]['aws_environment_variables']` zappa_settings.json fields.

Example:
```
# Zappa Project Required ENVIRONMENT VARIABLES
ZAPPAPROJ_AWS_ACCESS_KEY_ID={AWS_ACCESS_KEY_ID for AnnotationTool Project S3 Bucket Access}
ZAPPAPROJ_AWS_SECRET_ACCESS_KEY={AWS_SECRET_ACCESS_KEY for AnnotationTool Project S3 Bucket Access}
ZAPPAPROJ_DB_USER={AnnotationTool Database User}
ZAPPAPROJ_DB_NAME={AnnotationTool Database Name}
ZAPPAPROJ_DB_PASSWORD={AnnotationToll Database Password}
ZAPPAPROJ_APPLICATION_HOST={Host address where backend application runs}
```

