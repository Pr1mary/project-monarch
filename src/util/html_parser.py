
from lxml import html

class HtmlParser:

  def __init__(self, raw_html):
    self.doc = html.fromstring(raw_html)

  def parseHtml(self, label, search_tag, root_tag, target_tag_xpath):
    node = self.doc.xpath(f"//{search_tag}[contains(normalize-space(), '{label}')]")
    if not node:
      return None
    
    node = node[0]
    while node is not None and node.tag.lower() != root_tag:
      node = node.getparent()
    
    cells = [c.text_content().strip() for c in node.xpath(target_tag_xpath)]
    return cells