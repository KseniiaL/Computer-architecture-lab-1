import requests
from urllib.parse import urlparse
import xml.etree.ElementTree as ET

links_file_path = './links.xml'
html_files_path = './documents/'
res_file_path = './results.xml'
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:45.0) Gecko/20100101 Firefox/45.0'
}
root = ET.Element('data')

def save_response(link, res):
    name = urlparse(link)
    open(html_files_path + '{}.html'.format(name[1] + name[2].replace('/', '-')), 'w').write(res)

def get_html(link):
    try:
        response = requests.get(link, headers=headers)
        html = str(response.text)
        save_response(link, html)
        return html
    except requests.exceptions.RequestException as err:
        save_response(link, str(err))
        return str(err)

tree = ET.parse(links_file_path).getroot()
for link in tree.findall('url'):
        res = ET.SubElement(root, 'result')
        ET.SubElement(res, 'url').text = link.text
        # print (link.text)
        get_html(link.text)

resTree = ET.ElementTree(root)
resTree.write(res_file_path)