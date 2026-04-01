
import pika
from pika.adapters.blocking_connection import BlockingChannel
import logging

class Queue:

  def __init__(self, host: str, vhost: str, username: str, password: str):
    creds = pika.PlainCredentials(username, password)
    self.connection = pika.BlockingConnection(
      pika.ConnectionParameters(host, credentials=creds, virtual_host=vhost)
      )
    self.subs_channel:BlockingChannel = None
    self.pubs_channel:BlockingChannel = None

  def listen(self, queue: str, callback):
    if self.subs_channel == None:
      self.subs_channel = self.connection.channel()
    
    channel = self.subs_channel
    
    channel.queue_declare(queue, durable=True, arguments={'x-queue-type': 'classic'})
    
    channel.basic_consume(queue, auto_ack=False, on_message_callback=callback)
    
    logging.info(f"Starting '{queue}' consumer... ctrl+c to exit")
    channel.start_consuming()

  def ackMessage(self, delivery_tag):
    if self.subs_channel == None:
      return
    
    self.subs_channel.basic_ack(delivery_tag)

  def send(self, queue: str, msg: str):
    if self.pubs_channel == None:
      self.pubs_channel = self.connection.channel()
    
    channel = self.pubs_channel
    
    channel.queue_declare(queue, durable=True, arguments={'x-queue-type': 'classic'})

    channel.basic_publish(exchange='',
                          routing_key=queue,
                          body=msg)
    logging.info(f"Message sent - {str(msg)}")

  def shutdown(self):
    self.connection.close()