# -*- coding: utf-8 -*-

import requests
import os
import time
import threading
import random
import sys
import logging
from pathlib import Path
from bs4 import BeautifulSoup

v = 2

gitHubToken = 'username:pwd'
anthCode = b64encode(gitHubToken.encode('utf8')).decode('utf8')
authstr = 'Basic ' + anthCode

logging.basicConfig(filename=Path(__file__).with_suffix('.log'),
                    level=logging.DEBUG,
                    format='%(asctime)s *%(levelname)s* %(message)s')
# logging.debug('This message should go to the log file')
logging.info('So should this %s' % authstr)
# logging.warning('And this, too')
# logging.error('This message should go to the log file')
# logging.critical('So should this')

def download_page(url):
    headers_chrome = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip,deflate,br',
        'accept-language': 'en-US,en;q=0.9',
        'upgrade-insecure-requests': '1',
        'sec-fetch-site': 'none',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-user': '?1',
        'sec-fetch-dest': 'document',
        'dnt': '1',
        'Authorization': authstr
    }
    headers_edge = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36 Edg/83.0.478.64',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip,deflate,br',
        'accept-language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7,en-GB;q=0.6',
        'upgrade-insecure-requests': '1',
        'sec-fetch-site': 'none',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-user': '?1',
        'sec-fetch-dest': 'document',
        'cache-control': 'max-age=0',
        'dnt': '1',
        'Authorization': authstr
    }
    headers_firefox = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:78.0) Gecko/20100101 Firefox/78.0',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'accept-encoding': 'gzip,deflate,br',
        'accept-language': 'en-US,en;q=0.5',
        'upgrade-insecure-requests': '1',
        'dnt': '1',
        'Authorization': authstr
    }

    headers = random.choice([headers_chrome, headers_edge, headers_firefox])
    ret = requests.get(url, headers=headers)
    # r.encoding = 'gb2312'
    # r.encoding = 'utf-8'
    return ret.text

def get_topic_list(topics_url):
    topic_to_link = {}
    topic_to_description = {}
    for ti in range(1,7):
        page = "{}?page={}".format(topics_url, ti)
        if v >= 1:
            print('Processing {}/7, {}'.format(ti, page))
        html = download_page(page)
        soup = BeautifulSoup(html, 'html.parser')
        topic_list = soup.find_all('li', class_='py-4 border-bottom')  # find each topic link section
        if v >= 1:
            print('Got {} topics'.format(len(topic_list)))
        if len(topic_list) == 0:
            print("Get topic list failed for page: {}".format(page))
            sys.exit(2)
        for t in topic_list:
            a_tag = t.find('a')
            link = a_tag.get('href')
            t_tag = t.find('p', class_='f3 lh-condensed mb-0 mt-1 link-gray-dark')
            text = t_tag.get_text()
            d_tag = t.find('p', class_='f5 text-gray mb-0 mt-1')
            description = d_tag.get_text()
            topic_to_link[text.strip(' \t\n\r')] = link.strip(' \t\n\r')
            topic_to_description[text.strip(' \t\n\r')] = description.strip(' \t\n\r')
    return topic_to_link, topic_to_description

def get_repo_list(topic_url):
    repo_to_link = {}
    for ri in range(1,4):
        page = "{}?page={}".format(topic_url, ri)
        if v >= 1:
            print('Processing {}/7, {}'.format(ri, page))
        html = download_page(page)
        soup = BeautifulSoup(html, 'html.parser')
        repo_list = soup.find_all('h1', class_="f3 text-gray text-normal lh-condensed")  # find each repository link section
        if v >= 1:
            print('Got {} repositories'.format(len(repo_list)))
        if len(repo_list) == 0:
            print("Get repository list failed for page: {}".format(page))
            sys.exit(2)
        for r in repo_list:
            a_tag = r.find_all('a')
            link = a_tag[1].get('href')
            text = a_tag[1].get_text()
            repo_to_link[text.strip(' \t\n\r')] = link.strip(' \t\n\r')
    return repo_to_link

def get_repo(repo_url):
    html = download_page(repo_url)
    soup = BeautifulSoup(html, 'html.parser')
    d_list = soup.find_all('div', class_="flex-shrink-0 col-12 col-md-3")  # find "About" section
    if len(d_list) == 0:
        print("Get 'About' section failed for repository: {}".format(repo_url))
        sys.exit(2)
    for d in d_list:
        p_tag = d.find('p', class_='f4 mt-3')
        if p_tag != None:
            if v>=2:
                print('Got description')
            return p_tag.get_text().strip(' \t\n\r')
    return ''

def execute(topic,url,desc):
    if v >= 1:
        print('Thread {} is processing topic {}\r\n'.format(threading.current_thread().name, topic))
    repo_list = get_repo_list(url)
    rpl = [i for i,j in repo_list.items()]
    random.shuffle(rpl)
    repo_to_description = {}
    for rname in rpl:
        rurl = repo_list[rname]
        url = 'https://github.com{}'.format(rurl)
        if v>=1:
            print('Repository - {}'.format(rname))
        description = get_repo(url)
        repo_to_description[rname] = description if description != '' else url
        time.sleep(1)   # treat the site nicely, to avoid being blocked, 0.1 got blocked
    if v>=1:
        print('Writing topic {} into file'.format(topic))
    with open(r'd:\github\{}.txt'.format(topic), 'a', encoding='utf-8') as f:
        f.write(desc)
        for repo in repo_list.keys():
            f.write('\r\n{}:        {}'.format(repo, repo_to_description[repo]))

def main():
    dir = r"d:\github"
    if not os.path.exists(dir):
        os.makedirs(dir)

    if v >= 1:
        print('Getting topic list...')
    topic_list,topic_desc = get_topic_list('https://github.com/topics')

    #topic_urls = [j for i,j in topic_list.items()]
    topics = [i for i,j in topic_list.items()]
    random.shuffle(topics)

    max_thread = 1   # max thread count
    if v >= 1:
        print('Creating thread to process the topic list, max thread count: {}...'.format(max_thread))

    threads = []
    while len(topics) > 0:
        for thread in threads:
            if not thread.is_alive():
                threads.remove(thread)
        while len(threads) < max_thread and len(topics) > 0:
            cur_topic = topics.pop(0)
            cur_page = topic_list[cur_topic]
            cur_desc = topic_desc[cur_topic]
            url = 'https://github.com{}'.format(cur_page)
            thread = threading.Thread(name=cur_topic, target=execute, args=(cur_topic,url,cur_desc,))
            thread.setDaemon(True)
            thread.start()
            threads.append(thread)
            #execute(cur_topic,url)

    if v>=1:
        print('Done')

if __name__ == '__main__':
    main()
