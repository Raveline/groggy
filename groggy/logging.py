LOG_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'groggy': {
            'format': '%(asctime)s %(levelname)s [%(name)s: %(lineno)s] -- %(message)s',
            'datefmt': '%m-%d-%Y %H:%M:%S'
        }
    },
    'handlers': {
        'groggyHandler': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'groggy'
        }
    },
    'loggers': {
        'groggy': {
            'handlers': ['groggyHandler'],
            'level': 'INFO',
            'propagate': True,
        },
    }
}
