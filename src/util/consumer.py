
import pika
import logging

class Consumer:

  def __init__(self, host: str, vhost: str, username: str, password: str):
    creds = pika.PlainCredentials(username, password)
    self.connection = pika.BlockingConnection(
      pika.ConnectionParameters(host, credentials=creds, virtual_host=vhost)
      )

  def listen(self, queue: str, callback):
    channel = self.connection.channel()
    
    channel.queue_declare(queue, durable=True, arguments={'x-queue-type': 'classic'})
    
    channel.basic_consume(queue, auto_ack=True, on_message_callback=callback)
    
    logging.info(f"Starting '{queue}' consumer... ctrl+c to exit")
    channel.start_consuming()