"""
Пример фильтрации уведомлений по типу
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from itd import ITDClient, StreamConnect
from itd.enums import NotificationType


def main():
    cookies = 'YOUR_COOKIES_HERE'

    if cookies == 'YOUR_COOKIES_HERE':
        print('! Укажите cookies в переменной cookies')
        print('   См. examples/README.md для инструкций')
        return

    client = ITDClient(cookies=cookies)

    SHOW_TYPES = {NotificationType.LIKE, NotificationType.FOLLOW, NotificationType.COMMENT}

    print('-- Подключение к SSE...')
    print(f'-- Фильтр: {", ".join(t.value for t in SHOW_TYPES)}\n')

    try:
        for event in client.stream_notifications():
            if isinstance(event, StreamConnect):
                print(f'✅ Подключено! User ID: {event.user_id}\n')
                continue

            if event.type not in SHOW_TYPES:
                continue

            # Обработка разных типов
            if event.type == NotificationType.LIKE:
                print(f'❤️  {event.actor.display_name} лайкнул ваш пост')

            elif event.type == NotificationType.FOLLOW:
                print(f'👤 {event.actor.display_name} подписался на вас')

            elif event.type == NotificationType.COMMENT:
                print(f'💬 {event.actor.display_name}: {event.preview}')

    except KeyboardInterrupt:
        print(f'\n! Отключение...')


if __name__ == '__main__':
    main()
