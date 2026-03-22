import pika
import sys
import os
import uuid

def callback(ch, method, props, body):
  raw_msg = body.decode('utf-8')
  print(raw_msg)

def main():
  creds = pika.PlainCredentials(username='rabbitmq', password='^FYx3oo5ULfl*j*EoXi%D#9&')
  connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='192.168.1.64', credentials=creds, virtual_host='project-monarch')
    )
  channel = connection.channel()

  channel.queue_declare(queue="parse-email", durable=True, arguments={'x-queue-type': 'classic'})

  channel.basic_consume(queue="parse-email", auto_ack=True, on_message_callback=callback)

  print(f"Starting consumer... ctrl+c to exit")
  channel.start_consuming()

if __name__ == "__main__":
  try:
    main()
  except KeyboardInterrupt:
    print("User exit")
    try:
      sys.exit(0)
    except SystemExit:
      os._exit(0)