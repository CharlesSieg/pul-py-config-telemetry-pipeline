import pulumi_aws as aws


def create_buckets(config):
    """Create S3 buckets for telemetry data and Athena query results."""
    name_prefix = config["name_prefix"]
    tags = config["common_tags"]

    # Raw telemetry bucket
    telemetry_bucket = aws.s3.BucketV2(
        "telemetry",
        bucket=f"{name_prefix}-telemetry",
        tags=tags,
    )

    aws.s3.BucketVersioningV2(
        "telemetry-versioning",
        bucket=telemetry_bucket.id,
        versioning_configuration={
            "status": "Enabled",
        },
    )

    aws.s3.BucketServerSideEncryptionConfigurationV2(
        "telemetry-encryption",
        bucket=telemetry_bucket.id,
        rules=[{
            "apply_server_side_encryption_by_default": {
                "sse_algorithm": "aws:kms",
            },
            "bucket_key_enabled": True,
        }],
    )

    aws.s3.BucketPublicAccessBlock(
        "telemetry-public-access-block",
        bucket=telemetry_bucket.id,
        block_public_acls=True,
        block_public_policy=True,
        ignore_public_acls=True,
        restrict_public_buckets=True,
    )

    aws.s3.BucketLifecycleConfigurationV2(
        "telemetry-lifecycle",
        bucket=telemetry_bucket.id,
        rules=[{
            "id": "telemetry-lifecycle",
            "status": "Enabled",
            "filter": {"prefix": "data/"},
            "transitions": [{
                "days": config["s3_lifecycle_ia_days"],
                "storage_class": "STANDARD_IA",
            }],
            "expiration": {
                "days": config["s3_lifecycle_expiration_days"],
            },
        }],
    )

    # Athena query results bucket
    athena_results_bucket = aws.s3.BucketV2(
        "athena-results",
        bucket=f"{name_prefix}-athena-results",
        tags=tags,
    )

    aws.s3.BucketServerSideEncryptionConfigurationV2(
        "athena-results-encryption",
        bucket=athena_results_bucket.id,
        rules=[{
            "apply_server_side_encryption_by_default": {
                "sse_algorithm": "aws:kms",
            },
            "bucket_key_enabled": True,
        }],
    )

    aws.s3.BucketPublicAccessBlock(
        "athena-results-public-access-block",
        bucket=athena_results_bucket.id,
        block_public_acls=True,
        block_public_policy=True,
        ignore_public_acls=True,
        restrict_public_buckets=True,
    )

    aws.s3.BucketLifecycleConfigurationV2(
        "athena-results-lifecycle",
        bucket=athena_results_bucket.id,
        rules=[{
            "id": "expire-query-results",
            "status": "Enabled",
            "filter": {"prefix": ""},
            "expiration": {
                "days": 7,
            },
        }],
    )

    return telemetry_bucket, athena_results_bucket
