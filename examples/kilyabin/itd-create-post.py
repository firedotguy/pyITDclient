#!/usr/bin/env python3
from uuid import UUID
from argparse import ArgumentParser
from os import getenv
from os.path import isfile, basename

from itd import ITDClient


def main():
    parser = ArgumentParser(description='Create a post on ITD via CLI')

    parser.add_argument('--token', default=getenv('ITD_TOKEN'), help='Refresh token (or set ITD_TOKEN environment variable)')

    parser.add_argument('--text', required=True, help='Text content of the post')

    parser.add_argument('--file', help='Optional file to attach to the post')

    parser.add_argument('--filename', help='Filename on server (if --file is used, default: local filename)')

    args = parser.parse_args()

    if not args.token:
        print('❌ Token not provided (--token or ITD_TOKEN)')
        quit()

    try:
        client = ITDClient(None, args.token)

        file_id = None
        if args.file:
            if not isfile(args.file):
                print(f'❌ File not found: {args.file}')
                quit()

            server_name = args.filename or basename(args.file)
            with open(args.file, 'rb') as f:
                response = client.upload_file(server_name, f)

            file_id = str(getattr(response, 'id', None))
            if not file_id:
                print('❌ Failed to get file ID')
                quit()
            print(f'✅ File uploaded: {response.filename} (id={file_id})')

        # Создаём пост с правильным аргументом 'content'
        if file_id:
            post_resp = client.create_post(content=args.text, attach_ids=[UUID(file_id)])
        else:
            post_resp = client.create_post(content=args.text)

        print('✅ Post created successfully!')
        print(f'  id: {post_resp.id}')
        print(f'  text: {args.text}')
        if file_id:
            print(f'  attached file id: {file_id}')

    except Exception as e:
        print('❌ Error:', e)
        quit()


if __name__ == '__main__':
    main()
