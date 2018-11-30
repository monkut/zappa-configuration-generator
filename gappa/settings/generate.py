"""
Uses ENVIRONMENT VARIABLES to build and populate the 'zappa_settings.json' file.

Environment Variables prefixed with 'ZAPPAPROJ_' will be added to the zappa_settings 'environment_variables'
with the prefix removed.
"""
import os
import hashlib
import boto3


DEFAULT_REGION = os.getenv('DEFAULT_REGION', 'ap-northeast-1')
DEFAULT_STAGE = 'prod'
AWS_PROFILE = os.getenv('AWS_PROFILE', None)

LAMBDA_EXECUTION_ROLENAME = os.getenv('LAMBDA_EXECUTION_ROLENAME', None)

# Expect values to be separated by a single, ','.
VPC_CONFIG_SUBNETIDS = os.getenv('VPC_CONFIG_SUBNETIDS', None)
if VPC_CONFIG_SUBNETIDS:
    VPC_CONFIG_SUBNETIDS = [i.strip() for i in VPC_CONFIG_SUBNETIDS.split(',')]

# Expect values to be separated by a single, ','.
VPC_CONFIG_SECURITYGROUPIDS = os.getenv('VPC_CONFIG_SECURITYGROUPIDS', None)
if VPC_CONFIG_SECURITYGROUPIDS:
    VPC_CONFIG_SECURITYGROUPIDS = [i.strip() for i in VPC_CONFIG_SECURITYGROUPIDS.split(',')]

USE_ZAPPA_SENTRY = os.getenv('USE_ZAPPA_SENTRY', False)

try:
    import zappa_sentry
    ZAPPA_SENTRY_INSTALLED = True
except ImportError:
    ZAPPA_SENTRY_INSTALLED = False


VALID_ZAPPA_STAGE_SETTINGS = (
 'api_key_required',
 'api_key',
 'apigateway_enabled',
 'apigateway_description',
 'assume_policy',
 'attach_policy',
 'async_source',
 'async_resources',
 'async_response_table',
 'async_response_table_read_capacity',
 'async_response_table_write_capacity',
 'aws_endpoint_urls',
 'aws_environment_variables',
 'aws_kms_key_arn',
 'aws_region',
 'binary_support',
 'callbacks',
 'cache_cluster_enabled',
 'cache_cluster_size',
 'cache_cluster_ttl',
 'cache_cluster_encrypted',
 'certificate',
 'certificate_key',
 'certificate_chain',
 'certificate_arn',
 'cloudwatch_log_level',
 'cloudwatch_data_trace',
 'cloudwatch_metrics_enabled',
 'cognito',
 'context_header_mappings',
 'cors',
 'dead_letter_arn',
 'debug',
 'delete_local_zip',
 'delete_s3_zip',
 'django_settings',
 'domain',
 'base_path',
 'environment_variables',
 'events',
 'exception_handler',
 'exclude',
 'extends',
 'extra_permissions',
 'iam_authorization',
 'include',
 'authorizer',
 'keep_warm',
 'keep_warm_expression',
 'lambda_description',
 'lambda_handler',
 'lets_encrypt_key',
 'log_level',
 'manage_roles',
 'memory_size',
 'num_retained_versions',
 'payload_compression',
 'payload_minimum_compression_size',
 'prebuild_script',
 'profile_name',
 'project_name',
 'remote_env',
 'role_name',
 'role_arn',
 'route53_enabled',
 'runtime',
 's3_bucket',
 'slim_handler',
 'settings_file',
 'tags',
 'timeout_seconds',
 'touch',
 'touch_path',
 'use_precompiled_packages',
 'vpc_config',
 'xray_tracing'
)


def _generate_project_bucket_name(project_name: str, salt: str):
    project_name = project_name.replace(' ', '_').replace('-', '_')

    # generate a hashcomponent to make the bucket globably unique for s3
    hash_component = hashlib.sha1(salt.encode('utf8')).hexdigest()[:8]
    return f'zappa-{project_name}-{hash_component}'


def collect_project_envars(project_prefix='ZAPPAPROJ_', project_aws_prefix='ZAPPAPROJAWS_'):
    envars = {}
    aws_envars = {}
    for key in os.environ:
        if key.startswith(project_prefix):
            clean_key = key.replace(project_prefix, '')
            envars[clean_key] = os.environ[key].strip()
        elif key.startswith(project_aws_prefix):
            clean_key = key.replace(project_aws_prefix, '')
            aws_envars[clean_key] = os.environ[key].strip()
    return envars, aws_envars


def generate_zappa_settings(stackname: str, additional_envars: dict=None, additional_aws_envars: dict=None, stage: str='prod', region: str=DEFAULT_REGION, **zappa_parameters) -> dict:

    required_parameters = (
        'project_name',
    )
    for p in required_parameters:
        if p not in zappa_parameters:
            raise ValueError(f'Required Parameter ({p}) not given: {zappa_parameters}')
    project_name = zappa_parameters['project_name']
    profile_name = zappa_parameters['profile_name']

    if 's3_bucket' not in zappa_parameters:
        project_bucket_name = _generate_project_bucket_name(project_name, stackname)
    else:
        project_bucket_name = zappa_parameters['s3_bucket']
    zappa_settings = {
        stage: {
            'aws_region': region,
            'project_name': project_name,
            'profile_name': profile_name,  # AWS (local) PROFILE
            "runtime": "python3.6",
            "memory_size": 2048,
            "timeout_seconds": 300,
            "s3_bucket": project_bucket_name,
        }
    }
    if LAMBDA_EXECUTION_ROLENAME:
        zappa_settings[stage]['manage_roles'] = False
        zappa_settings[stage]['role_name'] = LAMBDA_EXECUTION_ROLENAME  # Matches name in infrastructure/README.md

    # Add envars
    if additional_envars:
        zappa_settings[stage]['environment_variables'] = additional_envars

    # add aws envars
    if additional_aws_envars:
        zappa_settings[stage]['aws_environment_variables'] = additional_aws_envars

    # add parameters
    # -- Note if a
    for name, value in zappa_parameters.items():
        if name not in VALID_ZAPPA_STAGE_SETTINGS:
            raise ValueError(f'({name}) is not a valid ZAPPA STAGE parameter!')
        zappa_settings[stage][name] = value

    # add sentry exceptions handler if zappa_sentry is installed and the appropriate envar is provided
    if USE_ZAPPA_SENTRY and ZAPPA_SENTRY_INSTALLED and 'SENTRY_DSN' in additional_envars:
        zappa_settings[stage]['exception_handler'] = "zappa_sentry.unhandled_exceptions"

    # retrieve and add vpc_config
    if VPC_CONFIG_SECURITYGROUPIDS and VPC_CONFIG_SUBNETIDS:
        zappa_settings[stage]['vpc_config'] = {
            "SubnetIds": VPC_CONFIG_SUBNETIDS,
            "SecurityGroupIds": VPC_CONFIG_SECURITYGROUPIDS
        }

    return zappa_settings


def parse_parameters(value):
    return [i.strip() for i in value.split('=')]


if __name__ == '__main__':
    import argparse
    import json
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-s', '--stack-name',
                        dest='stackname',
                        required=True,
                        help='aws cloudformation *stack-name* used to prepare the deployment environment')
    parser.add_argument('-r', '--region',
                        default=DEFAULT_REGION,
                        help=f'AWS Region to deploy project to [DEFAULT={DEFAULT_REGION}]')
    parser.add_argument('--stage',
                        default=DEFAULT_STAGE,
                        help=f'Stage to generate settings for [DEFAULT={DEFAULT_STAGE}]')
    parser.add_argument('-z', '--zappa-parameters',
                        dest='zappa_parameters',
                        nargs='+',
                        type=parse_parameters,
                        help='ZAPPA stage parameters to add or override [Default=None]'
                        )
    args = parser.parse_args()
    project_additional_envars, project_additional_aws_envars = collect_project_envars()

    parsed_parameters = {}
    if args.zappa_parameters:
        parsed_parameters = dict(args.zappa_parameters)

    if AWS_PROFILE:
        parsed_parameters['profile_name'] = AWS_PROFILE

    settings = generate_zappa_settings(args.stackname,
                                       additional_envars=project_additional_envars,
                                       additional_aws_envars=project_additional_aws_envars,
                                       stage=args.stage,
                                       region=args.region,
                                       **parsed_parameters)
    print(json.dumps(settings, indent=4))
