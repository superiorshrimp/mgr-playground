import pika
from pika.adapters.blocking_connection import BlockingChannel


def main():
    connection_params = pika.ConnectionParameters("127.0.0.1", 5672)
    connection = pika.BlockingConnection(connection_params)
    channel = connection.channel()

if __name__ == '__main__':
    main()