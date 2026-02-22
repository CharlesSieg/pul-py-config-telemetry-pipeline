import json

import pulumi_aws as aws


def create_glue(config, telemetry_bucket, glue_crawler_role):
    """Create Glue catalog database and crawler."""
    name_prefix = config["name_prefix"]
    tags = config["common_tags"]

    database = aws.glue.CatalogDatabase(
        "telemetry-database",
        name=name_prefix.replace("-", "_") + "_telemetry",
        tags=tags,
    )

    crawler = aws.glue.Crawler(
        "telemetry-crawler",
        database_name=database.name,
        name=f"{name_prefix}-telemetry",
        role=glue_crawler_role.arn,
        schedule=config["glue_crawler_schedule"],
        s3_targets=[{
            "path": telemetry_bucket.id.apply(lambda id: f"s3://{id}/data/"),
        }],
        schema_change_policy={
            "delete_behavior": "LOG",
            "update_behavior": "UPDATE_IN_DATABASE",
        },
        recrawl_policy={
            "recrawl_behavior": "CRAWL_NEW_FOLDERS_ONLY",
        },
        configuration=json.dumps({
            "Version": 1.0,
            "Grouping": {
                "TableGroupingPolicy": "CombineCompatibleSchemas",
            },
        }),
        tags=tags,
    )

    return database, crawler
