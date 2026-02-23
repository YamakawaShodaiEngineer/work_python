# サイトのHTMLを取得(サイト側から拒否されることあり)
# from urllib.request import urlopen
# with urlopen('https://kesennuma.furusato-nozei.jp/') as file:
#     for line in file:
#         print(str(line, encoding='utf-8'), end='')

# サイトのHTMLを取得してローカルで操作(サイト側から拒否されることあり)
# from urllib.request import urlopen
# with urlopen('https://kesennuma.furusato-nozei.jp/') as web_file:
#     with open('download.html', 'wb') as local_file:
#         local_file.write(web_file.read())

# requestsを使ってサイトのHTMLを取得(サイト側から拒否されることあり)
# import requests
# headers = {
#     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
# }
# r = requests.get('https://kesennuma.furusato-nozei.jp/', headers=headers)
# print(r.text)

# requestsを使ってサイトのHTMLを取得してローカルで操作(サイト側から拒否されることあり)
# import requests
# headers = {
#     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
# }
# r = requests.get('https://kesennuma.furusato-nozei.jp/', headers=headers)
# with open('download2.html', 'wb') as file:
#     file.write(r.content)

# requestsと正規表現を使ってサイトのHTMLを取得して必要な情報だけ抜き取る(サイト側から拒否されることあり)
# import requests
# import re

# r = requests.get('https://www.python.org/downloads/')

# release = []
# for li in re.findall(r'<li>.+?</li>',
#                      r.text.replace('\n', '')):
#     if x := re.search(r'<span class="release-number">'
#                       r'<a href=".+?">(.+?)</a></span>', li):
#         if y := re.search(r'<span class="release-date">'
#                           r'(.+?)</span>', li):
#             release.append((x.group(1), y.group(1)))

# release.sort()
# for name, date in release:
#     print(f'{name:15}{date}')

import requests
from bs4 import BeautifulSoup

r = requests.get('https://www.python.org/downloads/')

release = []
soup = BeautifulSoup(r.text, 'html.parser')

for li in soup.find_all('li'):
    if x := li.find('span', class_='release-number'):
        if y := li.find('span', class_='release-date'):
            release.append((x.text.strip(), y.text.strip()))

release.sort()
for name, date in release:
    print(f'{name:15}{date}')