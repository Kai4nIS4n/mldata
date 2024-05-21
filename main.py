import requests
from bs4 import BeautifulSoup
import json
import re


def process_text(text,quote):
    # 找到所有的 quote的位置
    quotes = [m.start() for m in re.finditer(quote, text)]

    if len(quotes) >= 2:
        # 如果至少有两个quote，提取两者之间的内容
        return text[quotes[0] + 1 : quotes[1]]
    elif len(quotes) == 1:
        # 如果只有一个 quote，删除它及其后面的所有内容
        return text[:quotes[0]]
    else:
        # 如果没有 quote，返回原始文本
        return text

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'DNT': '1',  # Do Not Track Request Header
    'Connection': 'keep-alive'
}

proxies = {
    'http': 'http://127.0.0.1:7890',
    'https': 'http://127.0.0.1:7890'
}

num=0
id = -1
data = []
while num<206:
    print(num)
    url = "http://huggingface.co/datasets/AdaptLLM/finance-tasks/viewer/Headline/test?p="+str(num)
    try:
        response = requests.get(url, headers=headers,proxies=proxies)
    except Exception as e:
        print(str(num)+"error")
        continue
    soup = BeautifulSoup(response.text, 'html.parser')
    divs = soup.find_all('div', class_='')
    for div in divs:
        if 'headline' in div.text or 'Headline' in div.text:
            try:
                item_txts=div.text.split("\n\n")
                for item_txt in item_txts:
                    item = {}
                    id=id+1
                    item['id']=id
                    Headline=item_txt.split("Does")[0]
                    Headline=Headline.replace("Headline",'')
                    Headline=Headline.replace("headline", '')
                    Headline=Headline.replace(":", '')
                    Headline=re.sub(r'^[^a-zA-Z]*', '', Headline)
                    Headline=process_text(Headline,'\\\"')
                    Headline = process_text(Headline, '\\\n')
                    item['Headline']=Headline
                    item['Question'] = re.findall(r'\bDoes\b[^?]*\?', item_txt)[0]
                    Answer=item_txt.split('?')[-1].replace(" ", '')
                    if Answer=="\\nOptions:\\n-Yes\\n-No":
                        Answer=""
                    if Answer!='':
                        if Answer[-1]=='o':
                            Answer="No"
                        elif Answer[-1]=='s':
                            Answer='Yes'
                        else:
                            Answer=''
                    item['Answer'] = Answer
                    data.append(item)
            except Exception as e:
                print(str(num)+"有错误!")
    print(str(num)+"已经完成！")
    num=num+1

with open('result.json', 'w') as f:
    print("文件写入中")
    json.dump(data, f,indent=4)

