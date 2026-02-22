"""iOS Telemetry Pipeline — Pulumi Python Program.

Deploys a serverless telemetry pipeline:
Pinpoint → Kinesis Firehose → S3 → Glue → Athena
"""

import pulumi

from config import get_config
from s3 import create_buckets
from iam import create_firehose_s3_role, create_pinpoint_firehose_role, create_glue_crawler_role
from kinesis import create_firehose
from pinpoint import create_pinpoint
from glue import create_glue
from athena import create_athena

# Load configuration
config = get_config()

# S3 buckets (no dependencies)
telemetry_bucket, athena_results_bucket = create_buckets(config)

# Firehose → S3 role (needs S3 bucket ARN for policy)
firehose_s3_role = create_firehose_s3_role(config, telemetry_bucket)

# Kinesis Firehose (needs S3 bucket and Firehose role)
firehose = create_firehose(config, telemetry_bucket, firehose_s3_role)

# Pinpoint → Firehose role (needs Firehose ARN for policy)
pinpoint_firehose_role = create_pinpoint_firehose_role(config, firehose)

# Pinpoint app and event stream (needs Firehose and Pinpoint role)
pinpoint_app = create_pinpoint(config, firehose, pinpoint_firehose_role)

# Glue crawler role (needs S3 bucket ARN for policy)
glue_crawler_role = create_glue_crawler_role(config, telemetry_bucket)

# Glue database and crawler (needs S3 bucket and Glue role)
glue_database, glue_crawler = create_glue(config, telemetry_bucket, glue_crawler_role)

# Athena workgroup and named queries (needs results bucket and Glue database)
athena_workgroup = create_athena(config, athena_results_bucket, glue_database)

# Exports
pulumi.export("pinpoint_application_id", pinpoint_app.application_id)
pulumi.export("telemetry_bucket_name", telemetry_bucket.id)
pulumi.export("telemetry_bucket_arn", telemetry_bucket.arn)
pulumi.export("athena_results_bucket_name", athena_results_bucket.id)
pulumi.export("firehose_delivery_stream_arn", firehose.arn)
pulumi.export("glue_database_name", glue_database.name)
pulumi.export("athena_workgroup_name", athena_workgroup.name)
