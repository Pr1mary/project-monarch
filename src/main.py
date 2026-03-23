
import sys
import os

from util.consumer import Consumer
from util.db import DbConn
from core.business import Business

def main():
  dbconn = DbConn(host='192.168.1.101',
                  port=3306,
                  user='n8n_monarch',
                  password='YhOqrJhPpVectSUD@aTVTkc2',
                  database='project_monarch')
  
  business = Business(dbconn)

  consumer = Consumer(host='192.168.1.64',
                      vhost='project-monarch',
                      username='rabbitmq',
                      password='^FYx3oo5ULfl*j*EoXi%D#9&')
  consumer.listen("parse-email", business.callback)

if __name__ == "__main__":
  try:
    main()
  except KeyboardInterrupt:
    print("User exit")
    try:
      sys.exit(0)
    except SystemExit:
      os._exit(0)
