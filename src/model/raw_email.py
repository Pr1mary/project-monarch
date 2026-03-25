
class RawEmailModel:

  def __init__(self, id = None, from_email = None, to_email = None, subject = None, body = None):
    self.id = id
    self.from_email = from_email
    self.to_email = to_email
    self.subject = subject
    self.body = body