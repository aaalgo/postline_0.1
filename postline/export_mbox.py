#!/usr/bin/env python3

from sql_storage import SqlStorage, create_engine
import postline
import config

def main ():
    import argparse
    parser = argparse.ArgumentParser(description='Dump messages for an agent')
    parser.add_argument('address', help='Agent address')
    args = parser.parse_args()
    store = SqlStorage(create_engine(config.DB_URL))
    agent = postline.Agent(args.address, store)
    for entry in agent.journal:
        print()
        print('From', entry.message['From'])
        print(entry.message.as_string())

if __name__ == '__main__':
    main()
