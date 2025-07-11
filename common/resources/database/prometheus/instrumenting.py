from prometheus_client import Summary, Enum

handler_latency = Summary(
    'handler_latency_seconds',
    'Кумулятивное время работы обработчика.',
    ['handler_name', ],
)
auth_state = Enum(
    'auth_states',
    'Стадии аутентификации.',
    states=['from_cache', 'from_db', 'update_cache', 'auth_organizations', ],
    labelnames=['where', ],
)

