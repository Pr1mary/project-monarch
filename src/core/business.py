
from util.db import DbConn

class Business:

  def __init__(self, dbconn: DbConn):
    self.dbconn = dbconn

  def callback(self, ch, method, props, body):
    raw_msg:str = body.decode('utf-8')
    try:
      msg_data = raw_msg.split("-")
      first_id = int(msg_data[1])
      data_len = int(msg_data[3])

      id_list = [i for i in range(first_id, first_id+data_len)]

      param_holder = ", ".join(["%s"] * data_len)
      qy_str = f'SELECT id, from_email, to_email, subject, body FROM raw_email WHERE id in ({param_holder})'
      raw_result = self.dbconn.query(qy_str, id_list)

      print(raw_result)
    except Exception as err:
      err.with_traceback()
      print(f"Broken message detected!: {err}")
