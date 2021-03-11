# -*- coding:UTF-8 -*-
# openpyxl needed 
# json needed
# target 39058662
import requests, re, traceback, json, pandas, logging, time
from pathlib import Path


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
# 创建log文件
log_path = Path(Path().cwd())
log_name = str(time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())) + ".log"
full_path = Path(log_path.joinpath(log_name))
full_path.open("w")
file_handler = logging.FileHandler(full_path, mode='w', encoding='UTF-8')
file_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
# 添加到Logger中
logger.addHandler(file_handler)

def get_html_text(url:str) -> str:
    try:
        headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'}
        r = requests.get(url,timeout=30,headers = headers)
        r.raise_for_status()
        r.encoding = r.apparent_encoding
        return r.text
    except Exception:
        print("\n")
        print(traceback.format_exc())
        return ''

def get_info() -> None:
    datas = []

    page = 1
    max_page = 3000

    while page <= max_page:
        html = get_html_text("https://api.bilibili.com/x/credit/blocked/list?pn=" + str(page))
        # print(html)
        dicts = json.loads(html)
        try:
            if(len(dicts['data']) == 0):
                print('\n已获取所有小黑屋信息,程序已结束')
                break
            data = dicts['data']
        except Exception:
            print('\n已获取所有小黑屋信息,程序已结束')
            break
        for i in data:
            i = ((str(i).replace("'",'"')).replace('True','true')).replace('False','false')
            re_h=re.compile('</?\w+[^>]*>')
            i=re_h.sub('',i)
            try:
                temp_dict = json.loads(i)
                data_id = temp_dict['data_id']
                uid = temp_dict['uid']
                name = temp_dict['uname']
                reason = temp_dict['punishTitle']
                if temp_dict['blockedDays'] == 0:
                    time_d = '永久'
                else:
                    time_d = temp_dict['blockedDays']
                evidence = temp_dict['originContentModify']

                lists = [data_id, uid, name, reason, time_d, evidence]
                datas.append(lists)
            except Exception:
                print("\n")
                print(traceback.format_exc())
                logger.info(str(i))
                print(i)
        
        # print('当前爬取页数：{}'.format(page))
        print("\r当前爬取页数：%d!" %page, end= " ")
        page += 1

    
    my_excle = pandas.DataFrame(datas, columns=['ID', 'UID', '用户名', '原因', '封禁时间', '证据'])
    output_name = str(time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())) + ".xlsx"
    writer = pandas.ExcelWriter(output_name)
    my_excle.to_excel(writer)
    writer.save()



if __name__=="__main__":
    print('************bilibili小黑屋爬虫************')
    print('****************************************')
    input('确认无误后，按任意键开始爬取')
    
    get_info()