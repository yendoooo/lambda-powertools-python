from aws_lambda_powertools import Logger

logger: Logger = Logger()

@logger.inject_lambda_context(log_event=True)
def lambda_handler(event: dict, context) -> None:
    logger.info('Hello World!')
