from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities import parameters
from aws_lambda_powertools.utilities.typing import LambdaContext

logger: Logger = Logger()

@logger.inject_lambda_context(log_event=True)
def lambda_handler(event: dict, context: LambdaContext) -> None:
    logger.info(f'{context.get_remaining_time_in_millis()=}')
    try:
        param: str = parameters.get_parameter('/lambda-powertools/sample')
        logger.info(f'{param=}')
    except parameters.exceptions.GetParameterError as e:
        logger.exception(e)
