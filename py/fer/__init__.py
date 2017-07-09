from fer.ferutil import env, logger

EV_LOGLEVEL = "LOGLEVEL"
env.vars.register(EV_LOGLEVEL, "ERROR", logger.get_level)