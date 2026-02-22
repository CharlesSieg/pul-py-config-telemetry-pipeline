import pulumi_aws as aws


def create_pinpoint(config, firehose_stream, pinpoint_firehose_role):
    """Create Pinpoint application with event stream to Firehose."""
    name_prefix = config["name_prefix"]
    tags = config["common_tags"]

    app = aws.pinpoint.App(
        "telemetry-app",
        name=f"{name_prefix}-telemetry",
        tags=tags,
    )

    aws.pinpoint.EventStream(
        "telemetry-event-stream",
        application_id=app.application_id,
        destination_stream_arn=firehose_stream.arn,
        role_arn=pinpoint_firehose_role.arn,
    )

    return app
