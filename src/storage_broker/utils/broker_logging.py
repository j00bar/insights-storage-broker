import os
import sys
import logging

import watchtower

from logstash_formatter import LogstashFormatterV1
from boto3.session import Session

from storage_broker.utils import config


def config_cloudwatch(logger):
    CW_SESSION = Session(
        aws_access_key_id=config.CW_AWS_ACCESS_KEY_ID,
        aws_secret_access_key=config.CW_AWS_SECRET_ACCESS_KEY,
        region_name=config.AWS_REGION,
    )
    cw_handler = watchtower.CloudWatchLogHandler(
        boto3_session=CW_SESSION,
        log_group=config.LOG_GROUP,
        stream_name=config.NAMESPACE,
        create_log_group=False,
    )
    cw_handler.setFormatter(LogstashFormatterV1())
    logger.addHandler(cw_handler)


def initialize_logging():
    kafkalogger = logging.getLogger("kafka")
    kafkalogger.setLevel("ERROR")
    if any("OPENSHIFT" in k for k in os.environ):
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(LogstashFormatterV1())
        logging.root.setLevel(os.getenv("LOG_LEVEL", "INFO"))
        logging.root.addHandler(handler)
    else:
        logging.basicConfig(
            level=config.LOG_LEVEL,
            format="%(threadName)s %(levelname)s %(name)s - %(message)s",
        )

    logger = logging.getLogger(config.APP_NAME)

    if config.CW_AWS_ACCESS_KEY_ID and config.CW_AWS_SECRET_ACCESS_KEY:
        config_cloudwatch(logger)
        logger.info("Cloudwatch Logging Enabled")
    else:
        logger.info("Cloudwatch Logging Disabled")

    return logger
