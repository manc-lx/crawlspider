#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import requests
from bs4 import BeautifulSoup
import random
import threading
import time

def open_url(url):

    header = [
        'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.76 Mobile Safari/537.36',
      'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
        'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0)',
        'Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1',
        'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; 360SE)'
    ]

    header={'User-Agent':str(header[random.randint(0,4)])}
    request = requests.get(url=url,headers=header)
    response = request.content
    response_decode = response.decode('utf-8')
    return response_decode

def chapter_url(url):
    html = open_url(url)
    soup = BeautifulSoup(html,'html.parser')
    chapterurllist = []
    chapterurl = soup.find('div',id="list").find_all('a')
    prefix = url[:url.index(".com")+len(".com")]
    for i in chapterurl:
        i=i['href']
        tureurl = prefix +i
        chapterurllist.append(tureurl)
    return chapterurllist

def get_content(url):
    pagehtml = open_url(url)
    soup = BeautifulSoup(pagehtml,'html.parser')
    chaptername = soup.h1.string
    chaptercontent = soup.find_all('div',id="content")[0].text
    chaptercontent = ' '.join(chaptercontent.split())
    content = chaptercontent.replace(' ','\r\n\n')
    finallcontent = chaptername + '\r\n\n\n' + content
    return finallcontent

def execute(chapterIdx, cur_url, chapterIdx_to_content):
    print('Thread {} is processing chapter {}th \n'.format(threading.current_thread().name, chapterIdx+1))
    text = get_content(cur_url)
    garbage = text.find('网页版章节内容慢')
    if garbage > 0:
        text = text[:garbage]
    chapterIdx_to_content[chapterIdx] = text

def downloadnovel(url, rangeStr, writeToFile = False):
    start = time.time()
    pagehtml = open_url(url)
    soup = BeautifulSoup(pagehtml, 'html.parser')
    novelname = soup.h1.string
    auther = soup.p.string
    other = soup.find('div',id="info").find_all('p')
    print(novelname) # 名称
    print(auther) #作者
    print(other[1].text) #状态
    print(other[-1].text) #最新章节
    print(other[-2].text) #最后更新
    print('开始下载小说')
    chapterlist = chapter_url(url) #传入小说首页，获取所有章节的链接
    lenchapter = len(chapterlist)
    lrangeStr = rangeStr.strip().replace('[','').replace(']','').split(':')
    min = 0
    max = lenchapter  # index max is excluded, so no need minus 1
    if len(lrangeStr) > 1:
        mins = lrangeStr[0].strip()
        neg = mins.startswith('-')
        if neg: mins = mins.lstrip('-')
        if mins.isdigit():
            min = int(mins)
            if neg: min = lenchapter - min
        maxs = lrangeStr[1].strip()
        neg = maxs.startswith('-')
        if neg: maxs = maxs.lstrip('-')
        if maxs.isdigit():
            max = int(maxs)
            if neg: max = lenchapter - max
    chapterlist = chapterlist[min:max]
    dllenchapter = max - min  # index max is excluded
    print('这部小说一共有%d 章，需要下载第%d 到第%d 章' % (lenchapter, min+1, max))
    count = 1

    # multiple threads
    max_thread = 10   # max thread count
    print('Creating thread to process the novel, max thread count: {}...'.format(max_thread))
    threads = []
    chapterlist.reverse() # pop(0) is too slow O(n), reverse the list and use pop() is much faster O(1)
    chapterIdx = -1
    chapterIdx_to_content = {}
    write_file_thread = threading.Thread(name='write to file', target=writeToFileExec, args=(chapterIdx_to_content, len(chapterlist), writeToFile, novelname+'.txt'))
    write_file_thread.setDaemon(True)
    write_file_thread.start()
    while len(chapterlist) > 0:
        for thread in threads:
            if not thread.is_alive():
                threads.remove(thread)
        while len(threads) < max_thread and len(chapterlist) > 0:
            cur_url = chapterlist.pop()
            chapterIdx = chapterIdx + 1
            thread = threading.Thread(name=str(chapterIdx), target=execute, args=(chapterIdx, cur_url, chapterIdx_to_content))
            thread.setDaemon(True)
            thread.start()
            threads.append(thread)

    write_file_thread.join()
    # if writeToFile:
    #     with open(novelname+'.txt','a+',encoding='utf-8') as f:
    #         for url in chapterlist:
    #             text = get_content(url)
    #             f.write(text + '\n\n\n\n')
    #             a = ((count / dllenchapter) * 100)
    #             print('正在下载第%d章,进度%d/%d=%.2f%%' % (min+count, count, dllenchapter, a)) # 这里是用来计算进度
    #             count += 1
    # else:
    #     for url in chapterlist:
    #         text = get_content(url)
    #         print(text)
    #         a = ((count / dllenchapter) * 100)
    #         print('正在下载第%d章,进度%d/%d=%.2f%%' % (min+count, count, dllenchapter, a)) # 这里是用来计算进度
    #         count += 1
    end = time.time()
    print('下载完成！用时：{:.2f} 分钟'.format((end-start)/60))

def writeToFileExec(chapterIdx_to_content, size, writeToFile, fileName):
    if writeToFile:
        with open(fileName, 'a+', encoding='utf-8') as f:
            i = 0
            while i < size:
                content = chapterIdx_to_content.get(i, None)
                if content:
                    f.write(content + '\n\n\n\n')
                    i = i + 1
                else:
                    time.sleep(0.3)
    else:
        i = 0
        while i < size:
            content = chapterIdx_to_content.get(i, None)
            if content:
                print(content + '\n\n\n\n')
                i = i + 1
            else:
                sleep(1)

if __name__=='__main__':
    args = sys.argv[1:]
    url = args[0]
    print('url: {}'.format(url))
    args = args[1:]
    writeToFile = False
    if "-f" in args:
        writeToFile = True
        args.remove("-f")
    print('write to file: {}'.format(writeToFile))
    rangeStr = ""
    if len(args) >= 1:
        rangeStr = args[0]
    print('rangeStr: {}'.format(rangeStr))
    downloadnovel(url, rangeStr, writeToFile)
