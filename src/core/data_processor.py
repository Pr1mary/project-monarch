
from util.db import DbConn
from model.raw_email import RawEmailModel
import traceback

from lxml import html

class DataProcessor:

  def __init__(self, dbconn: DbConn):
    self.dbconn = dbconn

  # 4 params are needed for rabbitmq callback params
  def callback(self, ch, method, props, body):
    raw_msg:str = body.decode('utf-8')
    try:
      msg_data = raw_msg.split("-")
      first_id = int(msg_data[1])
      data_len = int(msg_data[3])
      print(f"Email fetched length {data_len} starting at id {first_id}")

      id_list = [i for i in range(first_id, first_id+data_len)]

      param_holder = ", ".join(["%s"] * data_len)
      qy_str = f'SELECT id, from_email, to_email, subject, body FROM raw_email WHERE id in ({param_holder})'
      raw_result_list = self.dbconn.query(qy_str, id_list)

      parsed_result_list = [RawEmailModel(**raw_result) for raw_result in raw_result_list]

      for parsed_data in parsed_result_list:
        
        if parsed_data.subject == "Billing Payment Diterima":
          extr_data = None
        if parsed_data.subject == "Billing Invoice Pelanggan MyRepublic" and "Billing Statement" in parsed_data.body:
          extr_data = self.parseBillingStatement(parsed_data.body)
        else:
          extr_data = None
        
        print(extr_data)

    except Exception as err:
      traceback.print_exc()
      print(f"ERROR - Broken message detected!")

  def parseBillingStatement(self, content:str):
    doc = html.fromstring(content)
    
    cust_cels = self.parseHtml(doc, "ID Langganan", "h4", "td", ".//h4")
    payment_cells = self.parseHtml(doc, "Jumlah Tagihan", "h4", "table", ".//td|.//th")

    result = {
      "cust_id": cust_cels[1],
      "invoice_date": payment_cells[3],
      "due_date": payment_cells[4],
      "total_charges": payment_cells[5],
    }

    return result

  def parseHtml(self, doc, label, search_tag, root_tag, target_tag_xpath):
    node = doc.xpath(f"//{search_tag}[contains(normalize-space(), '{label}')]")
    if not node:
      return None
    
    node = node[0]
    while node is not None and node.tag.lower() != root_tag:
      node = node.getparent()
    
    cells = [c.text_content().strip() for c in node.xpath(target_tag_xpath)]
    return cells
