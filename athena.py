import pulumi_aws as aws


def create_athena(config, athena_results_bucket, glue_database):
    """Create Athena workgroup with enforced configuration and named queries."""
    name_prefix = config["name_prefix"]
    tags = config["common_tags"]

    workgroup = aws.athena.Workgroup(
        "telemetry-workgroup",
        name=f"{name_prefix}-telemetry",
        configuration={
            "enforce_workgroup_configuration": True,
            "publish_cloudwatch_metrics_enabled": True,
            "bytes_scanned_cutoff_per_query": 1073741824,  # 1 GB
            "result_configuration": {
                "output_location": athena_results_bucket.id.apply(
                    lambda id: f"s3://{id}/results/"
                ),
                "encryption_configuration": {
                    "encryption_option": "SSE_KMS",
                },
            },
        },
        tags=tags,
    )

    aws.athena.NamedQuery(
        "events-by-day",
        name=f"{name_prefix}-events-by-day",
        workgroup=workgroup.id,
        database=glue_database.name,
        query=glue_database.name.apply(lambda db: (
            f"SELECT year, month, day, COUNT(*) as event_count "
            f"FROM {db}.data "
            f"GROUP BY year, month, day "
            f"ORDER BY year DESC, month DESC, day DESC "
            f"LIMIT 30;"
        )),
    )

    aws.athena.NamedQuery(
        "top-event-types",
        name=f"{name_prefix}-top-event-types",
        workgroup=workgroup.id,
        database=glue_database.name,
        query=glue_database.name.apply(lambda db: (
            f"SELECT event_type, COUNT(*) as event_count "
            f"FROM {db}.data "
            f"GROUP BY event_type "
            f"ORDER BY event_count DESC "
            f"LIMIT 20;"
        )),
    )

    return workgroup
