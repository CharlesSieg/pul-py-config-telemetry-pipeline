# iOS Telemetry Pipeline: Pulumi (Python)

Pulumi Python program for deploying a serverless iOS telemetry pipeline on AWS.

## Architecture

```
iOS App → Amazon Pinpoint → Kinesis Data Firehose → S3 → AWS Glue → Amazon Athena
```

## Resources Created

- **Amazon Pinpoint:** Application with event stream forwarding to Firehose
- **Kinesis Data Firehose:** Delivery stream with GZIP compression and Hive-style date partitioning
- **S3 Buckets:** Raw telemetry storage (with lifecycle policies) and Athena query results
- **AWS Glue:** Catalog database and scheduled crawler for schema discovery
- **Amazon Athena:** Workgroup with enforced configuration and cost controls
- **IAM Roles:** Least-privilege roles for Pinpoint, Firehose, and Glue

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Usage

```bash
pulumi stack init dev
pulumi config set project_name myapp
pulumi config set aws:region us-east-1
pulumi up
```

## Configuration

| Key | Default | Description |
|-----|---------|-------------|
| `project_name` | (required) | Project name used in resource naming |
| `environment` | `dev` | Environment (dev, staging, prod) |
| `firehose_buffer_size_mb` | `5` | Firehose buffer size in MB (1-128) |
| `firehose_buffer_interval_seconds` | `300` | Firehose buffer interval in seconds (60-900) |
| `s3_lifecycle_ia_days` | `30` | Days before transitioning to Infrequent Access |
| `s3_lifecycle_expiration_days` | `90` | Days before object expiration |
| `glue_crawler_schedule` | `cron(0 */6 * * ? *)` | Glue crawler schedule expression |

## Related

- [Terraform implementation](https://github.com/CharlesSieg/tf-config-telemetry-pipeline)
- [Architecture article](https://charlessieg.com/articles/ios-telemetry-pipeline-kinesis-glue-athena.html)
