"""
Пример логирования уведомлений в файл
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from itd import ITDClient, StreamConnect
from datetime import datetime
import json


def main():
    cookies = 'YOUR_COOKIES_HERE'

    if cookies == 'YOUR_COOKIES_HERE':
        print('! Укажите cookies в переменной cookies')
        print('   См. examples/README.md для инструкций')
        return

    client = ITDClient(cookies=cookies)
    log_file = f'notifications_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'

    print(f'-- Подключение к SSE...')
    print(f'-- Логирование в: {log_file}\n')

    try:
        with open(log_file, 'w', encoding='utf-8') as f:
            for event in client.stream_notifications():
                timestamp = datetime.now().isoformat()

                if isinstance(event, StreamConnect):
                    log_entry = {'timestamp': timestamp, 'type': 'connect', 'user_id': str(event.user_id)}
                    print(f'-- Подключено! User ID: {event.user_id}')
                else:
                    log_entry = {
                        'timestamp': timestamp,
                        'type': event.type.value,
                        'id': str(event.id),
                        'actor': {'username': event.actor.username, 'display_name': event.actor.display_name},
                        'preview': event.preview,
                        'target_type': event.target_type.value if event.target_type else None,
                        'target_id': str(event.target_id) if event.target_id else None
                    }
                    print(f'* {event.type.value}: {event.actor.username}')

                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
                f.flush()

    except KeyboardInterrupt:
        print(f'\n! Отключение... Лог сохранен в {log_file}')


if __name__ == '__main__':
    main()
