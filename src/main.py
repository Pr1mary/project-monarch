
import sys
import os
from dotenv import load_dotenv
load_dotenv()

from util.consumer import Consumer
from util.db import DbConn
from core.data_processor import DataProcessor

def main():
  dbconn = DbConn(host=os.getenv('db_host'),
                  port=os.getenv('db_port'),
                  user=os.getenv('db_user'),
                  password=os.getenv('db_password'),
                  database=os.getenv('db_name'))
  
  data_processor = DataProcessor(dbconn)

  consumer = Consumer(host=os.getenv('rabbitmq-host'),
                      vhost=os.getenv('rabbitmq-vhost'),
                      username=os.getenv('rabbitmq-username'),
                      password=os.getenv('rabbitmq-password'))
  consumer.listen("parse-email", data_processor.callback)

if __name__ == "__main__":
  try:
    main()
  except KeyboardInterrupt:
    print("User exit")
    try:
      sys.exit(0)
    except SystemExit:
      os._exit(0)
