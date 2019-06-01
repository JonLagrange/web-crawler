import requests
from lxml import etree

headers = {
    'Referer': 'http://esi.clarivate.com/IndicatorsAction.action',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.108 Safari/537.36',
}

def get_html(url):
    session = requests.Session()
    request = session.get(url, headers=headers)
    request = session.get(url, headers=headers, cookies = request.cookies)
    return request


url = "http://gateway.webofknowledge.com/gateway/Gateway.cgi?GWVersion=2&SrcAuth=TSMetrics&SrcApp=TSM_TEST&DestApp=WOS_CPL&DestLinkType=FullRecord&KeyUT=000253408300009"
html = get_html(url)
tree = etree.HTML(html.content)
title = ''.join(tree.xpath("//div[@class='title']/value/text()"))
authors = ';'.join(tree.xpath("//a[@title='Find more records by this author']/text()"))
journal = ''.join(tree.xpath("//span[@class='sourceTitle']/value/text()"))
doi =  ''.join(tree.xpath("//span[text()='DOI:']/following-sibling::value/text()"))
date = ''.join(tree.xpath("//span[text()='Published:']/following-sibling::value/text()"))
doc_type = ''.join(tree.xpath("//span[text()='Document Type:']/following-sibling::text()"))
abstract = ''.join(tree.xpath("//div[text()='Abstract']/following-sibling::p/text()"))
author_keywords = ';'.join(tree.xpath("//span[text()='Author Keywords:']/following-sibling::a/text()"))
keywords_plus = ';'.join(tree.xpath("//span[text()='KeyWords Plus:']/following-sibling::a/text()"))
reprint_author = ''.join(tree.xpath("//div[text()='Author Information']/following-sibling::p/text()")).strip()
reprint_author = reprint_author[:reprint_author.find('(')]
reprint_address = ''.join(tree.xpath("//div[text()='Author Information']/following-sibling::table//td[@class='fr_address_row2']/text()"))
address = ';'.join(tree.xpath("//td[@class='fr_address_row2']/a/text()"))
email = ''.join(tree.xpath("//span[text()='E-mail Addresses:']/following-sibling::a/text()"))
publisher = ''.join(tree.xpath("//div[text()='Publisher']/following-sibling::p/value/text()"))
research_areas = ''.join(tree.xpath("//span[text()='Research Areas:']/following-sibling::text()"))
wos_categories = ''.join(tree.xpath("//span[text()='Web of Science Categories:']/following-sibling::text()"))
language = ''.join(tree.xpath("//span[text()='Language:']/following-sibling::text()"))
pubmed_id = ''.join(tree.xpath("//span[text()='PubMed ID:']/following-sibling::value/text()"))
issn = ''.join(tree.xpath("//span[text()='ISSN:']/following-sibling::value/text()"))
eissn = ''.join(tree.xpath("//span[text()='eISSN:']/following-sibling::value/text()"))
ids_number = ''.join(tree.xpath("//span[text()='IDS Number:']/following-sibling::value/text()"))
cited_ref = ''.join(tree.xpath("//a[@class='snowplow-cited-references-within-see-more-data-fields']/b/text()")).replace(',', '')
times_cited = ''.join(tree.xpath("//a[@class='snowplow-times-cited-within-see-more-data-fields']/b/text()")).replace(',', '')
print(times_cited)