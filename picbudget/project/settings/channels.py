import os
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [(os.getenv('CHANNELS_LAYERS_HOST', 'localhost'), 6379)],
        },
    },
}
