
def callback(ch, method, props, body):
  raw_msg:str = body.decode('utf-8')
  try:
    msg_data = raw_msg.split("-")
    first_id = msg_data[1]
    data_len = int(msg_data[3])
    print(f"First Id: {first_id} - Data Length: {data_len}")
  except:
    print("Broken message detected!")