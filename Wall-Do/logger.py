# Create a master logger
import logging

logging.basicConfig(level=logging.DEBUG, datefmt='%d/%m/%Y %I:%M:%S %p',
                    format='%(asctime)s - %(name)s - %(levelname)s - %(lineno)d - %(message)s',
                    filename='wall-do.log', filemode='w',
)

#logging.disable(logging.CRITICAL)

mainlogger = logging.getLogger('main')

