import pulumi_aws as aws


def create_firehose(config, telemetry_bucket, firehose_s3_role):
    """Create Kinesis Firehose delivery stream with S3 destination."""
    name_prefix = config["name_prefix"]
    tags = config["common_tags"]

    log_group = aws.cloudwatch.LogGroup(
        "firehose-log-group",
        name=f"/aws/kinesisfirehose/{name_prefix}-telemetry",
        retention_in_days=14,
        tags=tags,
    )

    log_stream = aws.cloudwatch.LogStream(
        "firehose-log-stream",
        name="S3Delivery",
        log_group_name=log_group.name,
    )

    firehose = aws.kinesis.FirehoseDeliveryStream(
        "telemetry-firehose",
        name=f"{name_prefix}-telemetry",
        destination="extended_s3",
        extended_s3_configuration={
            "role_arn": firehose_s3_role.arn,
            "bucket_arn": telemetry_bucket.arn,
            "prefix": "data/year=!{timestamp:yyyy}/month=!{timestamp:MM}/day=!{timestamp:dd}/",
            "error_output_prefix": "errors/year=!{timestamp:yyyy}/month=!{timestamp:MM}/day=!{timestamp:dd}/!{firehose:error-output-type}/",
            "buffering_size": config["firehose_buffer_size_mb"],
            "buffering_interval": config["firehose_buffer_interval_seconds"],
            "compression_format": "GZIP",
            "cloudwatch_logging_options": {
                "enabled": True,
                "log_group_name": log_group.name,
                "log_stream_name": log_stream.name,
            },
        },
        tags=tags,
    )

    return firehose
