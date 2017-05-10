from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from io import StringIO
from bs4 import BeautifulSoup
from django.core.files import File
import requests
import code
import pprint
import os
import json
import re
import io


def get_url(url):
    user_agent_header = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) ' \
                        'AppleWebKit/537.36 (KHTML, like Gecko) ' \
                        'Chrome/34.0.1847.131 Safari/537.36'
    session = requests.session()
    session.headers['User-Agent'] = user_agent_header
    web_request = session.get(url, allow_redirects=False)
    return web_request


def get_soup(url):
    web_request = get_url(url)
    data = web_request.text
    soup = BeautifulSoup(data, "html.parser")
    return soup


def get_wl_yeasts(url):
    soup = get_soup(url)
    yeasts = soup.find_all('div', {'class': 'yeast-details'})
    return yeasts


def get_wy_yeasts(url):
    soup = get_soup(url)
    yeasts = soup.find_all('div', {'class': 'box node-type-yeast-strain'})
    return yeasts

def get_lall_yeasts(url):
    soup = get_soup(url)
    div_class = 'col-md-7 col-sm-8 col-xs-8 pull-right'
    yeasts = soup.find_all('div', {'class': div_class})
    return yeasts


def get_wl_desc(url):
    soup = get_soup(url)
    desc = soup.find('div', {'class': 'field-item even'}).p.get_text()
    return desc


def get_wy_yeast_specs(url):
    soup = get_soup(url)
    desc_div = soup.find('div', {'id': 'yeast-description'})
    desc_div_class = 'clearfix text-formatted field field--name-body ' \
                     'field--type-text-with-summary field--label-hidden ' \
                     'field__item'
    data = {}
    data['desc'] = desc_div.find('div', {'class': desc_div_class}).p.get_text()
    specs = soup.find('div', {'id': 'yeast-specs'})
    data['floc'] = specs.find('div', {'id': 'flocculation'}).div.get_text()
    data['atten'] = specs.find('div', {'id': 'attenuation'}).div.get_text()
    data['temp'] = specs.find('div', {'id': 'temperature'}).div.get_text()
    data['abv'] = specs.find('div', {'id': 'abv'}).div.get_text()
    return data

def lall_yeast_specs(url):
    soup = get_soup(url)
    desc = soup.find('div', {'class': 'product-quick-fact'}).get_text().strip()
    pdf_url = soup.find('a', {'class': 'lnk-download'}).get('href')
    data = get_url(pdf_url).content
    io_data = io.BytesIO(data)
    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    password = ""
    maxpages = 1
    caching = True
    pagenos=set()

    for page in PDFPage.get_pages(io_data, pagenos, maxpages=maxpages,
                                  password=password, caching=caching,
                                  check_extractable=True):
        interpreter.process_page(page)

    pdf_content = retstr.getvalue()
    device.close()
    retstr.close()

    temp_regex = r"(\d+ - \d+°F)"
    atten_regex = r"AT ?TENUAT ?I ?ON\n(.*)\n"
    floc_regex = r"FLOCCUL ?ATION\n(.*)\n"
    alco_regex = r"ALCOHOL TOLER ?ANCE\n(.*) ABV\n"
    name_regex = r"Typical Analysis of (.*) [Yy]east"

    specs = {}

    # The CBC-1 PDF file doesn't have the same info
    if url == 'http://www.lallemandbrewing.com/product-details/301/':
        specs['name'] = 'CBC-1'
        specs['temp'] = '72°F'
        specs['atten'] = 'N\A'
        specs['floc'] = 'N\A'
        specs['abv'] = '12 - 14%'
        specs['url'] = pdf_url
        specs['desc'] = desc
        return specs

    specs['name'] = re.search(name_regex, pdf_content).group(1)
    specs['temp'] = re.search(temp_regex, pdf_content).group(1)
    specs['atten'] = re.search(atten_regex, pdf_content).group(1)
    specs['floc'] = re.search(floc_regex, pdf_content).group(1)
    specs['abv'] = re.search(alco_regex, pdf_content).group(1)
    specs['url'] = pdf_url
    specs['desc'] = desc

    return specs


def parse_whitelabs():
    base_url = 'http://www.whitelabs.com/'
    yeast_url = base_url + 'yeast-bank?show=yeasts&type=ale&yeast_type=7'
    yeasts = get_wl_yeasts(yeast_url)
    parsed_yeasts = {}

    for item in yeasts:
        parsed_h2 = item.h2.get_text().split(' ', 1)
        attr = item.find_all('div', {'class': 'value'})
        yeast_id = parsed_h2[0]
        parsed_yeasts[yeast_id] = {}
        parsed_yeasts[yeast_id]['lab'] = 'White Labs'
        parsed_yeasts[yeast_id]['name'] = parsed_h2[1]
        parsed_yeasts[yeast_id]['attenuation'] = attr[0].get_text()
        parsed_yeasts[yeast_id]['flocculation'] = attr[1].get_text()
        parsed_yeasts[yeast_id]['alcohol_tolerance'] = attr[2].get_text()
        parsed_yeasts[yeast_id]['temperature'] = attr[3].get_text()
        href = item.find('a').get('href')
        parsed_yeasts[yeast_id]['description'] = get_wl_desc(base_url + href)
        parsed_yeasts[yeast_id]['url'] = base_url + href
#        code.interact(local=locals())

    return parsed_yeasts


def parse_wyeastlabs():
    base_url = 'https://www.wyeastlab.com/'
    yeast_url = base_url + 'beer-strains/'
    yeasts = get_wy_yeasts(yeast_url)
    field_id = 'field field--name-field-strain-code field--type-string ' \
               'field--label-hidden field__item'
    field_name = 'clearfix text-formatted field ' \
                 'field--name-field-admin-title field--type-text ' \
                 'field--label-hidden field__item'
    parsed_yeasts = {}

    for item in yeasts:
        yeast_id = 'WY' + item.find('div', {'class': field_id}).get_text()
        yeast_name = item.find('div', {'class': field_name}).get_text()
        parsed_yeasts[yeast_id] = {}
        parsed_yeasts[yeast_id]['lab'] = 'Wyeast Labs'
        parsed_yeasts[yeast_id]['name'] = yeast_name
        href = item.find('a').get('href')[1:]
        yeast_specs = get_wy_yeast_specs(base_url + href)
        parsed_yeasts[yeast_id]['attenuation'] = yeast_specs['atten'] + '%'
        parsed_yeasts[yeast_id]['flocculation'] = yeast_specs['floc']
        parsed_yeasts[yeast_id]['alcohol_tolerance'] = yeast_specs['abv'] + '%'
        parsed_yeasts[yeast_id]['temperature'] = yeast_specs['temp'] + \
            '\u00b0F'
        parsed_yeasts[yeast_id]['description'] = yeast_specs['desc']
        parsed_yeasts[yeast_id]['url'] = base_url + href

    return parsed_yeasts


def parse_lallemandlabs():
    url = 'http://www.lallemandbrewing.com/products/brewing-yeast/'
    yeasts = get_lall_yeasts(url)

    parsed_yeasts = {}

    for item in yeasts:
        yeast_url = item.a.get('href')
        yeast_specs = lall_yeast_specs(yeast_url)
        yeast_id = yeast_specs['name']
        parsed_yeasts[yeast_id] = {}
        parsed_yeasts[yeast_id]['lab'] = 'Lallemand Labs'
        parsed_yeasts[yeast_id]['name'] = yeast_id
        parsed_yeasts[yeast_id]['attenuation'] = yeast_specs['atten']
        parsed_yeasts[yeast_id]['flocculation'] = yeast_specs['floc']
        parsed_yeasts[yeast_id]['alcohol_tolerance'] = yeast_specs['abv']
        parsed_yeasts[yeast_id]['temperature'] = yeast_specs['temp']
        parsed_yeasts[yeast_id]['description'] = yeast_specs['desc']
        parsed_yeasts[yeast_id]['url'] = yeast_specs['url']
    
    return parsed_yeasts


def parse_labs():
    whitelabs = parse_whitelabs()
    wyeastlabs = parse_wyeastlabs()
    lallemandlabs = parse_lallemandlabs()

    yeasts = whitelabs.copy()
    yeasts.update(wyeastlabs)
    yeasts.update(lallemandlabs)

    current_dir = os.path.dirname(__file__)
    data_file = os.path.join(current_dir, '../data/cache.json')
    with open(data_file, 'w') as json_cache:
        myfile = File(json_cache)
        myfile.write(json.dumps(yeasts))
    myfile.closed
    json_cache.closed


if __name__ == '__main__':
    parse_labs()
