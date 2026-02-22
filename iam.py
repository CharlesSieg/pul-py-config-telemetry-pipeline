import json

import pulumi_aws as aws


def get_account_id():
    """Get the current AWS account ID."""
    return aws.get_caller_identity().account_id


def create_firehose_s3_role(config, telemetry_bucket):
    """Create IAM role for Firehose to write to S3."""
    name_prefix = config["name_prefix"]
    account_id = get_account_id()

    role = aws.iam.Role(
        "firehose-s3-role",
        name=f"{name_prefix}-firehose-s3",
        assume_role_policy=json.dumps({
            "Version": "2012-10-17",
            "Statement": [{
                "Effect": "Allow",
                "Principal": {"Service": "firehose.amazonaws.com"},
                "Action": "sts:AssumeRole",
                "Condition": {
                    "StringEquals": {
                        "aws:SourceAccount": account_id,
                    },
                },
            }],
        }),
        tags=config["common_tags"],
    )

    aws.iam.RolePolicy(
        "firehose-s3-policy",
        name=f"{name_prefix}-firehose-s3",
        role=role.id,
        policy=telemetry_bucket.arn.apply(lambda arn: json.dumps({
            "Version": "2012-10-17",
            "Statement": [{
                "Effect": "Allow",
                "Action": [
                    "s3:AbortMultipartUpload",
                    "s3:GetBucketLocation",
                    "s3:GetObject",
                    "s3:ListBucket",
                    "s3:ListBucketMultipartUploads",
                    "s3:PutObject",
                ],
                "Resource": [arn, f"{arn}/*"],
            }],
        })),
    )

    return role


def create_pinpoint_firehose_role(config, firehose_stream):
    """Create IAM role for Pinpoint to write to Firehose."""
    name_prefix = config["name_prefix"]
    account_id = get_account_id()

    role = aws.iam.Role(
        "pinpoint-firehose-role",
        name=f"{name_prefix}-pinpoint-firehose",
        assume_role_policy=json.dumps({
            "Version": "2012-10-17",
            "Statement": [{
                "Effect": "Allow",
                "Principal": {"Service": "pinpoint.amazonaws.com"},
                "Action": "sts:AssumeRole",
                "Condition": {
                    "StringEquals": {
                        "aws:SourceAccount": account_id,
                    },
                },
            }],
        }),
        tags=config["common_tags"],
    )

    aws.iam.RolePolicy(
        "pinpoint-firehose-policy",
        name=f"{name_prefix}-pinpoint-firehose",
        role=role.id,
        policy=firehose_stream.arn.apply(lambda arn: json.dumps({
            "Version": "2012-10-17",
            "Statement": [{
                "Effect": "Allow",
                "Action": [
                    "firehose:PutRecord",
                    "firehose:PutRecordBatch",
                ],
                "Resource": arn,
            }],
        })),
    )

    return role


def create_glue_crawler_role(config, telemetry_bucket):
    """Create IAM role for the Glue crawler."""
    name_prefix = config["name_prefix"]

    role = aws.iam.Role(
        "glue-crawler-role",
        name=f"{name_prefix}-glue-crawler",
        assume_role_policy=json.dumps({
            "Version": "2012-10-17",
            "Statement": [{
                "Effect": "Allow",
                "Principal": {"Service": "glue.amazonaws.com"},
                "Action": "sts:AssumeRole",
            }],
        }),
        tags=config["common_tags"],
    )

    aws.iam.RolePolicyAttachment(
        "glue-service-policy",
        role=role.name,
        policy_arn="arn:aws:iam::aws:policy/service-role/AWSGlueServiceRole",
    )

    aws.iam.RolePolicy(
        "glue-s3-policy",
        name=f"{name_prefix}-glue-s3",
        role=role.id,
        policy=telemetry_bucket.arn.apply(lambda arn: json.dumps({
            "Version": "2012-10-17",
            "Statement": [{
                "Effect": "Allow",
                "Action": [
                    "s3:GetObject",
                    "s3:ListBucket",
                ],
                "Resource": [arn, f"{arn}/*"],
            }],
        })),
    )

    return role
