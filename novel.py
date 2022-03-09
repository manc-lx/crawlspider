import requests
from bs4 import BeautifulSoup
import random

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
    for i in chapterurl:
        i=i['href']
        tureurl = 'https://www.xbiquge6.com' +i
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

def downloadnovel(url):
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
    print('这部小说一共有%d 章' % lenchapter)
    count = 1
    for url in chapterlist:
        text = get_content(url)
        with open('元尊.txt','a+',encoding='utf-8') as f:
            f.write(text + '\r\n\n\n\n')
        a = ((count / lenchapter) * 100)
        print('正在下载第%d章,进度%.2f%%' % (count, a)) # 这里是用来计算进度
        count += 1
        if count > 10:
            break
    print('下载完成！')
    with open('元尊.txt','a+',encoding='utf-8') as f:
        print(f.read())

if __name__=='__main__':
    url = 'https://www.xbiquge6.com/78_78513/'
    downloadnovel(url)
