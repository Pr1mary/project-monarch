
from util.db import DbConn
from util.queue import Queue
from util.html_parser import HtmlParser
from model.raw_email import RawEmailModel

from dateutil import parser as date_parser
import traceback
import logging

class DataProcessor:

  def __init__(self, dbconn: DbConn, queue: Queue = None):
    self.dbconn = dbconn
    self.queue = queue
    self.system_id = "monarch-parser"

  # 4 params are needed for rabbitmq callback params
  def callback(self, ch, method, props, body):
    raw_msg:str = body.decode('utf-8')
    try:
      logging.info(f"Received message: {raw_msg}")
      msg_data = raw_msg.split("-")
      first_id = int(msg_data[1])
      data_len = int(msg_data[3])
      bill_acc_list = []
      logging.info(f"Email fetched length {data_len} starting at id {first_id}")

      raw_result_list = self.fetchRawEmail(first_id, data_len)

      parsed_result_list = [RawEmailModel(**raw_result) for raw_result in raw_result_list]

      bill_data_list = []
      for parsed_data in parsed_result_list:
        
        if parsed_data.subject == "Billing Payment Diterima":
          data = {
            "type": "bill_accept",
            "data": self.parseBillingPayment(parsed_data.body)
          }
        elif parsed_data.subject == "Billing Invoice Pelanggan MyRepublic" and "Billing Statement" in parsed_data.body:
          data = {
            "type": "bill_statement",
            "data": self.parseBillingStatement(parsed_data.body)
          }
        else:
          continue

        if data.get("data", {}).get("cust_id") not in bill_acc_list:
          bill_acc_list.append(data.get("data").get("cust_id"))

        bill_data_list.append(data)
      
      for bill_data in bill_data_list:
        if bill_data.get("type") == "bill_statement":
          self.insertBillingLog(bill_data.get("data"))
        else:
          self.insertPaymentLog(bill_data.get("data"))

      for bill_acc_id in bill_acc_list:
        self.createCalendarEvent(bill_acc_id)

      self.queue.ackMessage(method.delivery_tag)
      logging.info("Processing data finished!")
    except Exception as err:
      traceback.print_exc()
      logging.error(f"Broken messages detected!")

  def parseBillingStatement(self, content:str):
    doc = HtmlParser(content)
    
    cust_cels = doc.parseHtml("ID Langganan", "h4", "td", ".//h4")
    invoice_cells = doc.parseHtml("Jumlah Tagihan", "h4", "table", ".//td|.//th")

    result = {
      "cust_id": cust_cels[1],
      "invoice_date": date_parser.parse(invoice_cells[3]),
      "due_date": date_parser.parse(invoice_cells[4]),
      "total_amount": int(invoice_cells[5].replace(",00", "").replace(".","").replace("Rp ","")),
    }

    return result

  def parseBillingPayment(self, content:str):
    doc = HtmlParser(content)
    
    cust_cells = doc.parseHtml("ID Pelanggan", "p", "td", "p")
    period_cells = doc.parseHtml("Periode", "p", "tbody", ".//td|.//th")
    total_cells = doc.parseHtml("Jumlah Pembayaran", "p", "tbody", ".//td|.//th")
    date_cells = doc.parseHtml("Tanggal Pembayaran", "p", "tbody", ".//td|.//th")

    result = {
      "cust_id": cust_cells[0].split("\n")[1].strip().replace("ID Pelanggan", "").strip(),
      "payment_period": date_parser.parse(period_cells[1]),
      "total_amount": int(total_cells[1].replace(",00", "").replace(".","").replace("Rp ","")),
      "payment_date": date_parser.parse(date_cells[1]),
    }

    return result

  def fetchRawEmail(self, first_id, data_len):

    id_list = [i for i in range(first_id, first_id+data_len)]
    
    param_holder = ", ".join(["%s"] * data_len)
    qy_str = f'SELECT id, from_email, to_email, subject, body FROM raw_email WHERE id in ({param_holder}) ORDER BY id DESC'
    
    result_list = self.dbconn.query(qy_str, id_list)
    return result_list

  def fetchBillingAccount(self, cust_id):

    qy_check_acc = f'SELECT id, cust_id, created_at, created_by FROM myrep_cust_account WHERE cust_id = %s'
    check_acc_res = self.dbconn.query(qy_check_acc, (cust_id,))

    if check_acc_res in [None, [], ()]:
      cmd_create_acc = f'INSERT INTO myrep_cust_account(cust_id, created_by) VALUES (%s, %s)'
      create_acc_res = self.dbconn.query(cmd_create_acc, (cust_id, self.system_id))
      if create_acc_res == 0:
        logging.error("Failed creating customer data")
        return None
      
      check_acc_res = self.dbconn.query(qy_check_acc, (cust_id,))
    
    acc_id = check_acc_res[0].get("id")
    if acc_id in [None, ""]:
      logging.error("Problem with customer data")
      return None
    
    return acc_id

  def insertBillingLog(self, data):
    
    acc_id = self.fetchBillingAccount(data.get("cust_id"))

    qy_check_bill = f'''
    SELECT id, cust_acc_id, period_month, period_year, inv_date, due_date, total_amount
    FROM myrep_billing_log WHERE cust_acc_id = %s AND period_month = %s AND period_year = %s
    '''
    check_bill_res = self.dbconn.query(qy_check_bill, (acc_id, data.get("invoice_date").month, data.get("invoice_date").year))
    if check_bill_res:
      return
    
    cmd_create_bill = f'''
    INSERT INTO myrep_billing_log(cust_acc_id, period_month, period_year, inv_date, due_date, total_amount, created_by, updated_by)
    VALUES(%s, %s, %s, %s, %s, %s, %s, %s)
    '''
    create_bill_res = self.dbconn.query(cmd_create_bill, (
      acc_id,
      data.get("invoice_date").month,
      data.get("invoice_date").year,
      data.get("invoice_date"),
      data.get("due_date"),
      data.get("total_amount"),
      self.system_id,
      self.system_id
      ))
    
    if create_bill_res == 0:
      logging.error("Failed create billing data")
      return

  def insertPaymentLog(self, data):
    
    acc_id = self.fetchBillingAccount(data.get("cust_id"))

    qy_check_bill = f'''
    SELECT id, cust_acc_id, period_month, period_year, inv_date, due_date, total_amount
    FROM myrep_billing_log WHERE cust_acc_id = %s AND period_month = %s AND period_year = %s
    '''
    check_bill_res = self.dbconn.query(qy_check_bill, (acc_id, data.get("payment_period").month, data.get("payment_period").year))
    bill_log_id = None
    if check_bill_res:
      bill_log_id = check_bill_res[0].get("id")

    qy_check_payment = f'''
    SELECT id, cust_acc_id, period_month, period_year, payment_date, total_amount, bill_log_id
    FROM myrep_payment_log WHERE cust_acc_id = %s AND bill_log_id = %s
    '''
    check_payment_res = self.dbconn.query(qy_check_payment, (acc_id, bill_log_id))
    if check_payment_res:
      return
    
    cmd_create_payment = f'''
    INSERT INTO myrep_payment_log(cust_acc_id, period_month, period_year, payment_date, total_amount, bill_log_id, created_by)
    VALUES(%s, %s, %s, %s, %s, %s, %s)
    '''
    create_payment_res = self.dbconn.query(cmd_create_payment, (
      acc_id,
      data.get("payment_period").month,
      data.get("payment_period").year,
      data.get("payment_date"),
      data.get("total_amount"),
      bill_log_id,
      self.system_id
      ))
    
    if create_payment_res == 0:
      logging.error("Failed create payment data")
      return
    
  def createCalendarEvent(self, bill_acc_id:int):

    if bill_acc_id != None:
      event_msg = f"remind-{bill_acc_id}"
    else:
      logging.warning("Received account with None id...")
      event_msg = f"remind-{bill_acc_id}"

    self.queue.send("record-calendar", event_msg)
