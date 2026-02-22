import pulumi


def get_config():
    """Read Pulumi configuration with sensible defaults."""
    cfg = pulumi.Config()
    aws_cfg = pulumi.Config("aws")

    project_name = cfg.require("project_name")
    environment = cfg.get("environment") or "dev"
    region = aws_cfg.get("region") or "us-east-1"

    name_prefix = f"{project_name}-{environment}"

    return {
        "project_name": project_name,
        "environment": environment,
        "region": region,
        "name_prefix": name_prefix,
        "firehose_buffer_size_mb": cfg.get_int("firehose_buffer_size_mb") or 5,
        "firehose_buffer_interval_seconds": cfg.get_int("firehose_buffer_interval_seconds") or 300,
        "s3_lifecycle_ia_days": cfg.get_int("s3_lifecycle_ia_days") or 30,
        "s3_lifecycle_expiration_days": cfg.get_int("s3_lifecycle_expiration_days") or 90,
        "glue_crawler_schedule": cfg.get("glue_crawler_schedule") or "cron(0 */6 * * ? *)",
        "common_tags": {
            "Project": project_name,
            "Environment": environment,
            "ManagedBy": "pulumi",
        },
    }
