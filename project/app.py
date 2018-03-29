import requests
from urllib.parse import urlparse
import xml.etree.ElementTree as elTree
from bs4 import BeautifulSoup
import functools
import re

links_file_path = './links.xml'
html_files_path = './documents/'
res_file_path = './results.xml'
headers = {
    'User-Agent':
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:45.0) Gecko/20100101 Firefox/45.0'
}
visitedList = []
includingLevel = 10
root = elTree.Element('data')


def indent(elem, level=0):
    i = "\n" + level * "  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level + 1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i


def compose(*functions):
    return functools.reduce(
        lambda f, g: lambda x: f(g(x)), functions, lambda x: x
    )


def trim(string):
    return string.strip()


def save_response(file_link, result):
    name = urlparse(file_link)
    open(
        html_files_path + '{}.html'.format(name[1] + name[2].replace('/', '-')), 'w'
    ).write(result)


def get_html(file_link):
    try:
        response = requests.get(file_link, headers=headers)
        html = str(response.text)
        # save_response(file_link, html)
        return html
    except requests.exceptions.RequestException as err:
        # save_response(file_link, str(err))
        return str(err)


def parse(html):
    results = []
    urls_list = []

    soup = BeautifulSoup(html, 'html.parser')

    def validate_email(email):
        if len(email) > 7:
            if re.match("^.+@([?)[a-zA-Z0-9-.]+.([a-zA-Z]{2,3}|[0-9]{1,3})(]?)$)", email) or re.match("[a-zA-Z0-9-.].+\(at\)([?)[a-zA-Z0-9-.]+.([a-zA-Z]{2,3}|[0-9]{1,3})(]?)$)", email):
                return email

    def validate_url(url):
        if re.match('https?://(?:www)?(?:[\w-]{2,255}(?:\.\w{2,6}){1,2})(?:/[\w&%?#-]{1,300})?', url):
            return url

    def deep(parent):
        for el in parent.find_all('a'):
            if el:
                if el.string is not None:
                    if validate_email(el.string) is not None:
                        results.append(el.string)
                    if validate_url(str(el.get('href'))) is not None:
                        urls_list.append(validate_url(el.get('href')))

        for el in parent.find_all('p'):
            if el:
                if el.string is not None:
                    for myStr in el.string.split():
                        if len(myStr) > 5:
                            if myStr[len(myStr) - 1] == '.':
                                if validate_email(myStr[:-1]) is not None:
                                    results.append(myStr[:-1])
                            else:
                                if validate_email(myStr) is not None:
                                    results.append(myStr)
                else:
                    text = el.get_text()
                    if len(text) != 0:
                        for myStr in text.split():
                            if len(myStr) > 5:
                                if validate_email(myStr[:-1]) is not None:
                                    results.append(myStr[:-1])
                                else:
                                    if validate_email(myStr) is not None:
                                        results.append(myStr)

    deep(soup)
    for i in urls_list:
        if not (i in visitedList) and len(visitedList) < includingLevel:
            visitedList.append(i)
            print(i, len(visitedList))
            compose(parse, get_html, trim)(i)
    for i in results:
        elTree.SubElement(res, 'email').text = str(i)
    return results


tree = elTree.parse(links_file_path).getroot()
for link in tree.findall('url'):
    res = elTree.SubElement(root, 'result')
    elTree.SubElement(res, 'url').text = link.text
    print(link.text)
    visitedList.clear()
    compose(parse, get_html, trim)(link.text)

indent(root)
resTree = elTree.ElementTree(root)
resTree.write(res_file_path)
