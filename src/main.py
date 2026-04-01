
import sys
import signal
import os
import logging
from dotenv import load_dotenv
load_dotenv()

from util.queue import Queue
from util.db import DbConn
from core.data_processor import DataProcessor

queue = None

def shutdownHandler(signum, frame):
  logging.info("Shutting down worker...")
  if queue:
    queue.shutdown()
  sys.exit(0)

def main():
  global queue

  log_mode = logging.INFO

  if os.getenv("worker_mode") == "DEV":
    log_mode = logging.DEBUG
  logging.basicConfig(level=log_mode)
  
  dbconn = DbConn(host=os.getenv('db_host'),
                  port=int(os.getenv('db_port')),
                  user=os.getenv('db_user'),
                  password=os.getenv('db_password'),
                  database=os.getenv('db_name'))

  queue = Queue(host=os.getenv('rabbitmq_host'),
                      vhost=os.getenv('rabbitmq_vhost'),
                      username=os.getenv('rabbitmq_username'),
                      password=os.getenv('rabbitmq_password'))
    
  data_processor = DataProcessor(dbconn, queue)
  queue.listen("parse-email", data_processor.callback)

if __name__ == "__main__":
  signal.signal(signal.SIGINT, shutdownHandler)
  signal.signal(signal.SIGTERM, shutdownHandler)
  try:
    main()
  except Exception as err:
    print(err)
