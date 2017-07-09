import string
import random
from fer.ferutil import logger

log = logger.get_logger()

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
  return ''.join(random.choice(chars) for _ in range(size))