from sys import argv

from itd.core.captcha import get_turnstile


def main():
    if argv[-1] == 'captcha':
        print(get_turnstile())

    else:
        print('unknown command')
