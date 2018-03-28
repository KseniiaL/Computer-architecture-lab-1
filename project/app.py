import requests
from urllib.parse import urlparse
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import functools
import re

links_file_path = './links.xml'
html_files_path = './documents/'
res_file_path = './results.xml'
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:45.0) Gecko/20100101 Firefox/45.0'
}
root = ET.Element('data')

def indent(elem, level=0):
  i = "\n" + level*"  "
  if len(elem):
    if not elem.text or not elem.text.strip():
      elem.text = i + "  "
    if not elem.tail or not elem.tail.strip():
      elem.tail = i
    for elem in elem:
      indent(elem, level+1)
    if not elem.tail or not elem.tail.strip():
      elem.tail = i
  else:
    if level and (not elem.tail or not elem.tail.strip()):
      elem.tail = i

def compose(*functions):
    return functools.reduce(lambda f, g: lambda x: f(g(x)), functions, lambda x: x)

def trim(string):
    return string.strip()

def save_response(link, res):
    name = urlparse(link)
    open(html_files_path + '{}.html'.format(name[1] + name[2].replace('/', '-')), 'w').write(res)

def get_html(link):
    try:
        response = requests.get(link, headers=headers)
        html = str(response.text)
        # save_response(link, html)
        return html
    except requests.exceptions.RequestException as err:
        # save_response(link, str(err))
        return str(err)

def parse(html):
    results = []

    soup = BeautifulSoup(html, 'html.parser')

    def validateEmail(email):
        if len(email) > 7:
            if re.match("^.+@([?)[a-zA-Z0-9-.]+.([a-zA-Z]{2,3}|[0-9]{1,3})(]?)$)", email) != None:
                return email

    def deep(parent):
        for el in parent.find_all('a'):
            if el:
                if (el.string != None):
                    if (validateEmail(el.string) != None):
                        results.append(el.string)

    deep(soup)
    for i in results:
        ET.SubElement(res, 'email').text = str(i)
    return results

tree = ET.parse(links_file_path).getroot()
for link in tree.findall('url'):
        res = ET.SubElement(root, 'result')
        ET.SubElement(res, 'url').text = link.text
        # print (link.text)
        compose(parse, get_html, trim)(link.text)

indent(root)
resTree = ET.ElementTree(root)
resTree.write(res_file_path)