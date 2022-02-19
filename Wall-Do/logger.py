# Create a master logger
import logging

logging.basicConfig(level=logging.DEBUG, datefmt='%d/%m/%Y %I:%M:%S %p',
                    format='%(asctime)s - %(name)s - %(levelname)s - %(lineno)d - %(message)s',
                    filename='wall-do.log', filemode='w',
)

#logging.disable(logging.CRITICAL)

# disable the connection library logger from urllib module
logging.getLogger('urllib3.connectionpool').disabled = True
# disable logging from Pillow module
logging.getLogger('PIL.TiffImagePlugin').disabled = True
logging.getLogger('PIL.PngImagePlugin').disabled = True

mainlogger = logging.getLogger('main')

