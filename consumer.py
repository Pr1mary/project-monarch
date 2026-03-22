
import pika
from business import callback

def consumer(host, vhost, queue, username, password):
  creds = pika.PlainCredentials(username, password)
  connection = pika.BlockingConnection(
    pika.ConnectionParameters(host, credentials=creds, virtual_host=vhost)
    )
  channel = connection.channel()

  channel.queue_declare(queue, durable=True, arguments={'x-queue-type': 'classic'})

  channel.basic_consume(queue, auto_ack=True, on_message_callback=callback)

  print(f"Starting consumer... ctrl+c to exit")
  channel.start_consuming()