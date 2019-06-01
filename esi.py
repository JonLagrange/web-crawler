import time
import requests
import json
import pymysql
from lxml import etree

# 根据xhr得到的服务器返回json数据的url，返回的json数据包含文献标题、文献id等信息
base_url = 'http://esi.clarivate.com/IndicatorsDataAction.action?_dc=xxx&type=documents&author=&researchField=&institution=&journal=&' \
           'territory=&article_UT=&researchFront=&articleTitle=&docType=Top&year=&page={page}&start={start}&limit={limit}&sort=%5B%7B' \
           '%22property%22%3A%22citations%22%2C%22direction%22%3A%22DESC%22%7D%5D'

# 每一篇web of science文献的目标url，后接文献id进行区分，目标网页包含每篇文献的详细信息
link = 'http://gateway.webofknowledge.com/gateway/Gateway.cgi?GWVersion=2&SrcAuth=TSMetrics&SrcApp=TSM_TEST&DestApp=WOS_CPL&DestLinkType=FullRecord&KeyUT={article_id}'

# 请求头，Referer：表示请求从哪个页面发过来的，User-Agent：它为服务器提供当前请求来自的客户端的信息，包
# 括系统类型、浏览器信息等，使用它来伪装我们的爬虫程序，如果不携带这个字段，服务器可能直接拒绝我们的请求
headers = {
    'Referer': 'http://esi.clarivate.com/IndicatorsAction.action',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.108 Safari/537.36',
}

# 请求url，得到response，第一次请求进入网站，保存sessionid，第二次从cookies获取sessionid，防止会话过期
def get_html(url):
    session = requests.Session()
    request = session.get(url, headers=headers)
    request = session.get(url, headers=headers, cookies=request.cookies)
    return request

# 根据page、start、limit生成url列表
def generate_url_list(pages, limit):
    esi_url_list = []
    for page in range(1, pages + 1):
        start = 10 * (page - 1)
        esi_url_list.append(
            base_url.format(page=page, start=start, limit=limit)
        )
    return esi_url_list

# 使用xpath方法解析目标网页的html信息,xpath方法返回一个list，所以用join方法转为str以便插入数据库
def web_of_science(url):
    response = get_html(url)
    tree = etree.HTML(response.content)
    title = ''.join(tree.xpath("//div[@class='title']/value/text()"))
    authors = ';'.join(tree.xpath("//a[@title='Find more records by this author']/text()"))
    journal = ''.join(tree.xpath("//span[@class='sourceTitle']/value/text()"))
    doi = ''.join(tree.xpath("//span[text()='DOI:']/following-sibling::value/text()"))
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
    return [title, authors, journal, doi, date, doc_type, abstract, author_keywords, keywords_plus, reprint_author, reprint_address,
            address, email, publisher, research_areas, wos_categories, language, pubmed_id, issn, eissn, ids_number, cited_ref, times_cited]

# 获取每篇文献的详细信息，并插入数据库
def main():
    index = 0
    # 遍历url，获取esi文献信息
    for url in generate_url_list(pages=100, limit=10):
        request_url = url.replace('xxx', str(round(time.time() * 1000)))
        # 提醒信息
        index += 1
        print('正在抓取esi第{}页的文献数据...'.format(index))
        html = get_html(request_url)
        esi_infos = json.loads(html.content)
        data = esi_infos['data']
        # 连接database
        conn = pymysql.connect(
            host='localhost',
            port=3306,
            user='root',
            passwd='root',
            db='webcrawler',
            charset='utf8'
        )
        # 使用cursor()方法获取操作游标
        cur = conn.cursor()
        for info in data:
            # 根据article_id检查要爬取的文献是否已在数据库中
            check = "select article_id from wos where article_id={}".format(info.get('articleId'))
            if cur.execute(check) == 0:
                # 文献目标网页
                target = link.format(article_id=info.get('articleId'))
                wos = web_of_science(target)
                data_json = [info.get('researchFieldName'), info.get('researchFieldCode'), info.get('countries'),
                             info.get('articleId'), target, info.get('hotpaper'), info.get('sourceOfBIB'), info.get('citations')]
                data_wos = wos[:-2]
                data_wos.extend(data_json)
                data_wos.extend(wos[-2:])
                #sql = "insert into esi values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                sql = "insert into wos values(0, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                # 执行sql语句
                cur.execute(sql, data_wos)
                # 提交到数据库执行
                conn.commit()

            else:
                print("文献已经存在")

        # 关闭数据库连接
        conn.close()
        time.sleep(5)

if __name__ == '__main__':
    main()