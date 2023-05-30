from datetime import datetime

TIME = datetime.now().replace(microsecond=0).isoformat(sep=' ')

RESPONSE = {
    "response": None,
    "time": str(TIME),
    "alert": None,
    "from": 'Server',
    "contacts": None
}

PRESENCE = {
    "action": "presence",
    "time": str(TIME),
    "type": "status",
    "user": {
        "account_name": '',
        "status": "Отлично! Я присоединился"
    }
}

MESSAGE = {
    "action": "msg",
    "time": str(TIME),
    "to": None,
    "message": None
}

SERV_RESP = (
    ('200', 'Хорошо'),
    ('401', 'Не авторизован'),
    ('404', 'Не найден')
)
