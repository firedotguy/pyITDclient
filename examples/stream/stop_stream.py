"""
Пример остановки SSE потока из кода
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import threading
from itd import ITDClient, StreamConnect


def main():
    cookies = 'YOUR_COOKIES_HERE'

    if cookies == 'YOUR_COOKIES_HERE':
        print('! Укажите cookies в переменной cookies')
        return

    client = ITDClient(cookies=cookies)

    def listen():
        print('! Начинаем прослушивание...')
        try:
            for event in client.stream_notifications():
                if isinstance(event, StreamConnect):
                    print(f'-- Подключено! User ID: {event.user_id}')
                else:
                    print(f'🔔 {event.type.value}: {event.actor.username}')
        except Exception as e:
            print(f'! Ошибка: {e}')

    thread = threading.Thread(target=listen, daemon=True)
    thread.start()

    print('Прослушивание запущено. Нажмите Enter для остановки...')
    input()

    print('!! Останавливаем прослушивание...')
    client.stop_stream()

    thread.join(timeout=5)
    print('! Остановлено')


if __name__ == '__main__':
    main()
