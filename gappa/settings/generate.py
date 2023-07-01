"""
Uses ENVIRONMENT VARIABLES to build and populate the 'zappa_settings.json' file.

Environment Variables prefixed with 'ZAPPAPROJ_' will be added to the zappa_settings 'environment_variables'
with the prefix removed.
"""
import os
import hashlib
from pathlib import Path
from distutils.util import strtobool
from typing import Tuple, Optional, Union

DEFAULT_PROFILE_NAME = 'default'
DEFAULT_STAGE = 'prod'
DEFAULT_REGION = os.getenv('DEFAULT_REGION', 'ap-northeast-1')
DEFAULT_RUNTIME = 'python3.7'
DEFAULT_MEMORY_SIZE = '2048'
DEFAULT_TIMEOUT_SECONDS = '300'  # 5 minutes
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
    import zappa_sentry  # noqa
    ZAPPA_SENTRY_INSTALLED = True
except ImportError:
    ZAPPA_SENTRY_INSTALLED = False


VALID_ZAPPA_STAGE_SETTINGS = (
    'app_function',
    'api_key_required',
    'api_key',
    'apigateway_enabled',
    'apigateway_description',
    'alb_enabled',
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
ZAPPA_STAGE_SETTINGS_INT_TYPES = (
    'async_response_table_write_capacity',
    'async_response_table_read_capacity',
    'cache_cluster_ttl',
    'memory_size',
    'timeout_seconds',
)
ZAPPA_STAGE_SETTINGS_BOOL_TYPES = (
    "alb_enabled",
    "api_key_required",
    "apigateway_enabled",
    "async_resources",
    "binary_support",
    "cache_cluster_enabled",
    "cache_cluster_encrypted",
    "cloudwatch_data_trace",
    "cloudwatch_metrics_enabled",
    "debug",
    "delete_local_zip",
    "delete_s3_zip",
    "iam_authorization",
    "keep_warm",
    "manage_roles",
    "payload_compression",
    "route53_enabled",
    "slim_handler",
    "touch",
    "use_precompiled_packages",
    "xray_tracing",
)
ZAPPA_STAGE_SETTINGS_DUAL_BOOLDICT_TYPES = (
    "cors",
)


def _generate_project_bucket_name(project_name: str, salt: str):
    project_name = project_name.replace(' ', '_').replace('-', '_')

    # generate a hash component to make the bucket globably unique for s3
    hash_component = hashlib.sha1(salt.encode('utf8')).hexdigest()[:8]
    return f'zappa-{project_name}-{hash_component}'


def collect_project_envars(project_prefix: str = 'ZAPPAPROJ_', project_aws_prefix: str = 'ZAPPAPROJAWS_') -> Tuple[dict, dict]:
    """
    Collect ALL configuration related environment variables.
    For all collected variables, the prefix is removed and the resulting key/value stored in the appropriate container.

    'project_prefix' -> envars
    'project_aws_prefix' -> aws_envars
    """
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


def _cast_value_type(name: str, value: str) -> Union[int, bool, dict]:
    """Convert a zappa_parameter to the appropriate type"""
    if name not in VALID_ZAPPA_STAGE_SETTINGS:
        raise ValueError(f'({name}) is not a valid ZAPPA STAGE parameter!')
    if name in ZAPPA_STAGE_SETTINGS_INT_TYPES:
        value = int(value)
    elif name in ZAPPA_STAGE_SETTINGS_DUAL_BOOLDICT_TYPES:
        if not isinstance(value, dict):
            value = bool(strtobool(value))
    elif name in ZAPPA_STAGE_SETTINGS_BOOL_TYPES:
        value = bool(strtobool(value))
    return value


def generate_zappa_settings(
        stackname: str,
        additional_envars: Optional[dict] = None,
        additional_aws_envars: Optional[dict] = None,
        stage: str = 'prod',
        region: str = DEFAULT_REGION,
        runtime: str = DEFAULT_RUNTIME,
        use_exclude_defaults: bool = True,
        events: Optional[Path] = None,
        use_slimhandler: bool = False,
        **zappa_parameters) -> dict:
    """
    Generate the zappa_settings dictionary from given variables
    :param stackname: Stack name of zappa project stack
    :param additional_envars: mapping of envar key/values
    :param additional_aws_envars: mappiing of aws envar key/values
    :param stage: zappa stage definition
    :param region: aws region
    :param runtime: Lambda python runtime to use
    :param use_exclude_defaults: Ignore DEFAULT excludes patterns
    :param events: zappa events definition
    :param use_slimhandler: include 'slim_handler = true' in resulting zappa_settings.json
    :param zappa_parameters:
    """
    required_parameters = (
        'project_name',
    )
    for p in required_parameters:
        if p not in zappa_parameters:
            raise ValueError(f'Required Parameter ({p}) not given: {zappa_parameters}')
    project_name = zappa_parameters['project_name']
    profile_name = zappa_parameters.get('profile_name', DEFAULT_PROFILE_NAME)

    if 's3_bucket' not in zappa_parameters:
        project_bucket_name = _generate_project_bucket_name(project_name, stackname)
    else:
        project_bucket_name = zappa_parameters['s3_bucket']
    zappa_settings = {
        stage: {
            'aws_region': region,
            'project_name': project_name,
            'profile_name': profile_name,  # AWS (local) PROFILE
            "runtime": runtime,
            "memory_size": int(zappa_parameters.get('memory_size', DEFAULT_MEMORY_SIZE)),
            "timeout_seconds": int(zappa_parameters.get('timeout_seconds', DEFAULT_TIMEOUT_SECONDS)),
            "s3_bucket": project_bucket_name,
            "additional_text_mimetypes": ["application/vnd.oai.openapi", ]
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

    if use_exclude_defaults:
        zappa_settings[stage]['exclude'] = [
            "*.rar",
            "test_*",
            ".circleci",
            ".pytest_cache",
            ".pylintrc",
            ".gitignore",
            ".isort.cfg",
            ".pre-commit-config.yaml",
            "fixtures",
            "tests"
        ]

    # add parameters
    # -- Convert to appropriate type if needed
    for name, value in zappa_parameters.items():
        value = _cast_value_type(name, value)
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

    # define events
    if events:
        assert events.exists()
        with events.open('r', encoding='utf8') as events_in:
            loaded_events = json.loads(events_in.read())
            zappa_settings[stage]['events'] = loaded_events

    if use_slimhandler:
        zappa_settings[stage]["slim_handler"] = True

    return zappa_settings


def parse_parameters(value: str) -> list:
    """Parse command-line name=value pairs into a list"""
    return [i.strip() for i in value.split('=')]


def filepath(value: str) -> Path:
    """Convert given value to a Path object"""
    p = Path(value).absolute()
    if not p.exists():
        raise Exception(f'Given file path does not exist: {value}')
    return p


if __name__ == '__main__':
    import argparse
    import json
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-s', '--stack-name',
                        dest='stackname',
                        required=True,
                        help='aws cloudformation *stack-name* used to prepare the deployment environment')
    parser.add_argument('-e', '--events',
                        default=None,
                        type=filepath,
                        help='Specify file path to the JSON file describing events to schedule in zappa')
    parser.add_argument('--stage',
                        default=DEFAULT_STAGE,
                        help=f'Stage to generate settings for [DEFAULT={DEFAULT_STAGE}]')
    parser.add_argument('-r', '--region',
                        default=DEFAULT_REGION,
                        help=f'AWS Region to deploy project to [DEFAULT={DEFAULT_REGION}]')
    parser.add_argument('-t', '--runtime',
                        default=DEFAULT_RUNTIME,
                        help='Lambda runtime to use (python3.7|python3.8|python3.9|python3.10)')
    parser.add_argument('--ignore-default-excludes',
                        dest="ignore_default_excludes",
                        action="store_true",
                        default=False,
                        help="Ignore DEFAULT excludes patterns")
    parser.add_argument('--use-slimhandler',
                        dest="use_slimhandler",
                        action="store_true",
                        default=False,
                        help="use slimhandler in package")
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
        try:
            parsed_parameters = dict([parameter for parameter in args.zappa_parameters if len(parameter) == 2])
        except ValueError:
            print(args.zappa_parameters)
            raise

    if AWS_PROFILE:
        parsed_parameters['profile_name'] = AWS_PROFILE

    use_exclude_defaults = not args.ignore_default_excludes
    settings = generate_zappa_settings(args.stackname,
                                       additional_envars=project_additional_envars,
                                       additional_aws_envars=project_additional_aws_envars,
                                       stage=args.stage,
                                       region=args.region,
                                       runtime=args.runtime,
                                       use_exclude_defaults=use_exclude_defaults,
                                       events=args.events,
                                       use_slimhandler=args.use_slimhandler,
                                       **parsed_parameters)
    print(json.dumps(settings, indent=4))
