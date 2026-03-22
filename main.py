
import sys
import os
from consumer import consumer

def main():

  consumer(host='192.168.1.64',
           vhost='project-monarch',
           queue="parse-email",
           username='rabbitmq',
           password='^FYx3oo5ULfl*j*EoXi%D#9&')

if __name__ == "__main__":
  try:
    main()
  except KeyboardInterrupt:
    print("User exit")
    try:
      sys.exit(0)
    except SystemExit:
      os._exit(0)