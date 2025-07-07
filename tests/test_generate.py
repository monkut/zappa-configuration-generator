import pytest

from gappa.settings.generate import generate_zappa_settings, DEFAULT_RUNTIME


def test_generate_geneate_zappa_settings__required_parameters():
    with pytest.raises(ValueError) as e_info:
        result = generate_zappa_settings(
            stackname="mystack",
        )
    result = generate_zappa_settings(
        stackname="mystack",
        project_name='myproject'
    )
    assert result


def test_generate_generate_zappa_settings__defaults():
    result = generate_zappa_settings(
        stackname="mystack",
        project_name='myproject',
    )
    default_stage = 'prod'
    assert result
    assert len(result) == 1
    assert default_stage in result
    assert result[default_stage]['runtime'] == DEFAULT_RUNTIME


def test_generate_generate_zappa_settings__bool_hanlding():
    bool_field_parameters = (
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
        "cors",
    )
    stage = 'dev'
    for fieldname in bool_field_parameters:
        # check False
        result = generate_zappa_settings(
            stackname="mystack",
            additional_envars=None,
            additional_aws_envars=None,
            stage=stage,
            region='ap-northeast-1',
            project_name='myproject',
            **{fieldname: 'False'}
        )
        assert result[stage][fieldname] is False

        # check True
        result = generate_zappa_settings(
            stackname="mystack",
            additional_envars=None,
            additional_aws_envars=None,
            stage=stage,
            region='ap-northeast-1',
            project_name='myproject',
            **{fieldname: 'True'}
        )
        assert result[stage][fieldname] is True
