from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities import parameters

logger: Logger = Logger()

@logger.inject_lambda_context(log_event=True)
def lambda_handler(event: dict, context) -> None:
    try:
        param: str = parameters.get_parameter('/lambda-powertools/sample', max_age=60)
        logger.info(f'{param=}')
    except parameters.exceptions.GetParameterError as e:
        logger.exception(e)
