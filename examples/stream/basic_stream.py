"""
Базовый пример прослушивания SSE потока уведомлений
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from itd import ITDClient, StreamConnect


def main():
    cookies = 'YOUR_COOKIES_HERE'

    if cookies == 'YOUR_COOKIES_HERE':
        print('! Укажите cookies в переменной cookies')
        print('   См. examples/README.md для инструкций')
        return

    client = ITDClient(cookies=cookies)

    print('-- Подключение к SSE...')

    try:
        for event in client.stream_notifications():
            if isinstance(event, StreamConnect):
                print(f'-- Подключено! User ID: {event.user_id}')
                print('-- Ожидание уведомлений...\n')
            else:
                print(f'* {event.type.value}: {event.actor.username}')
                if event.preview:
                    preview = event.preview[:50] + '...' if len(event.preview) > 50 else event.preview
                    print(f'   {preview}')

    except KeyboardInterrupt:
        print(f'\n! Отключение...')


if __name__ == '__main__':
    main()
