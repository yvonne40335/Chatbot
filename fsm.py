from transitions.extensions import GraphMachine

import string
import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater,CommandHandler,CallbackQueryHandler

import requests
from bs4 import BeautifulSoup
import re

page = requests.get("http://www.conan.url.tw/character.html")
soup = BeautifulSoup(page.content,'html.parser')
page2 = requests.get("http://www.conan.url.tw/movie.html")
soup2 = BeautifulSoup(page2.content,'html.parser')
page3 = requests.get("http://www.conan.url.tw/lovelist.html")
soup3 = BeautifulSoup(page3.content,'html.parser')
paget = requests.get("https://www.bilibili.com/video/av8754531/?from=search&seid=15982325499947658271")
soupt = BeautifulSoup(paget.content,'html.parser')

my_list=[]
name_list=[]
count=0
searchName=""
movieNum=0
loveNum=0

class switch(object):
    def __init__(self, value):
        self.value = value
        self.fall = False
 
    def __iter__(self):
        """Return the match method once, then stop"""
        yield self.match
        raise StopIteration
     
    def match(self, *args):
        """Indicate whether or not to enter a case suite"""
        if self.fall or not args:
            return True
        elif self.value in args: # changed for v1.5, see below
            self.fall = True
            return True
        else:
            return False


class TocMachine(GraphMachine):
    def __init__(self, **machine_configs):
        self.machine = GraphMachine(
            model = self,
            **machine_configs
        )

    def button(self,update):
        query = update.callback_query
        print("here")
        update.edit_message.text(text="%s" % query.data,chat_id=query.message.chat_id,message_id=query.message.message_id)

    def is_going_to_state1(self, update):
        text = update.message.text
        return text.lower() == '認識角色'

    def is_going_to_state2(self, update):
        text = update.message.text
        return text.lower() == '劇場版介紹'

    def is_going_to_state3(self, update):
        text = update.message.text
        return text.lower() == '愛情支線查詢'

    def is_going_to_category(self, update): 
        text = update.message.text
        global count
        if count!=0:
            print(count)
            return text.lower() == '主線相關角色' or text.lower() =='黑暗組織' or text.lower() =='警察' or text.lower() == 'fbi&cia' or text.lower() == '返回'
        count+=1

    def is_going_to_character(self, update):
        text = update.message.text
        global count
        global searchName
        if any(text in s for s in name_list) and count!=0:
            match=[s for s in name_list if text in s]
            searchName = match[0]
            return True
        else:
            print(count)
            if count!=0:
                update.message.reply_text('找不到此角色 請重新輸入名稱')
            count += 1

    def is_going_to_final1(self,update):
        text = update.message.text
        if any(text in s for s in name_list) and count!=0:
            text=text
        elif count!=0 and text.lower()!='ok' and text!='返回':
            update.message.reply_text('你可以輸入ok 結束搜尋\n否則......')
        return text.lower() == 'ok'

    def is_going_to_movie(self, update):
        text = update.message.text
        global movieNum
        global count
        if text.isdigit() and count!=0:
            if int(text)>0 and int(text)<22:
                movieNum=int(text)
                return True
            else:
                update.message.reply_text('找不到此劇場版 請重新輸入編號')
        elif text=='返回' and count!=0:
            return True
        count+=1
    
    def is_going_to_description(self, update):
        text = update.message.text
        global count
        print(count)
        if count==0:
            count=count
        elif text!='1' and text!='2' and text!='返回' and count!=0 and text.lower()!='ok':
            update.message.reply_text('代號輸入錯誤\n想觀看預告 請輸入1\n想觀看簡介 請輸入2\n\n返回')
        elif text=='1' or text=='2' or text=='返回':
            return True
        count += 1

    def is_going_to_final2(self,update):
        text = update.message.text
        print(count)
        if count!=0 and text.lower()!='ok' and text!='返回' and text!='1' and text!='2':
            update.message.reply_text('你可以輸入ok 結束搜尋\n否則......')
        return text.lower() == 'ok'

    def is_going_to_loveline(self, update):
        text = update.message.text       
        global count
        global loveNum
        if text.isdigit() and count!=0:
            if int(text)>0 and int(text)<10:
                loveNum=int(text)
                return True
            else:
                update.message.reply_text('找不到愛情支線 請重新輸入編號')
        elif text=='返回' and count!=0:
            return True
        elif count!=0:
            update.message.reply_text('找不到愛情支線 請重新輸入編號')
        count+=1

    def is_going_to_final3(self,update):
        text = update.message.text
        if text.isdigit() and count!=0:
            if int(text)<1 and int(text)>9:
                update.message.reply_text('你可以輸入ok 結束搜尋\n否則......')
        elif text.lower()!='ok' and text!='返回' and count!=0:
            update.message.reply_text('你可以輸入ok 結束搜尋\n否則......')
        elif text.lower()=='ok':
            return True
        #if count!=0 and text.lower()!='ok' and text!='返回' and int(text)<1 and int(text)>9:
         #   update.message.reply_text('你可以輸入ok 結束搜尋\n否則......')
        #return text.lower() == 'ok'

    def is_going_to_garbage(self, update):
        text = update.message.text
        return text.lower() != '認識角色' and text.lower() != '劇場版介紹' and text.lower() != '愛情支線查詢'

    def on_enter_state1(self, update):
        custom_keyboard = [['主線相關角色','黑暗組織'],['警察','FBI&CIA'],['返回']]
        reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
        update.message.reply_text("請輸入想認識的角色類別\n主線相關角色\n黑暗組織\n警察\nFBI&CIA\n返回\n",reply_markup=reply_markup)
        self.advance(update)

    def on_exit_state1(self, update):
        print('Leaving state1')

    def on_enter_state2(self, update):
        custom_keyboard = [['1','2','3','4','5','6','7'],['8','9','10','11','12','13','14'],['15','16','17','18','19','20','21'],['返回']]
        reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
        update.message.reply_text("請輸入想觀看的劇場版編號 1～21",reply_markup=reply_markup)
        self.advance(update)

    def on_exit_state2(self, update):
        print('Leaving state2')

    def on_enter_state3(self, update):
        custom_keyboard = [['1','2','3'],['4','5','6'],['7','8','9'],['返回']]
        reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
        update.message.reply_text("請輸入想查詢的愛情支線編號",reply_markup=reply_markup)
        divs = soup3.find_all('div',attrs={'class':'CollapsiblePanel'})
        global count
        love_list = []
        count = 0
        love=1
        for spans in divs:
            span = spans.find('div',attrs={'align':'center'})
            if not (span is None):
                string=""
                string=str(love)+"."
                string+=span.contents[0]
                string+=(" ❤ ")
                string+=span.contents[2]
                love_list.append(string)
                love+=1
        love_list.append("\n返回")
        update.message.reply_text('\n'.join(love_list))
        self.advance(update)

    def on_exit_state3(self, update):
        print('Leaving state3')

    def on_enter_category(self, update):
        global count 
        if update.message.text.lower()=='返回' and count!=0:
            self.go_back(update)
        else:
            reply_markup = telegram.ReplyKeyboardRemove()
            update.message.reply_text('從下面選擇一個名字',reply_markup=reply_markup)
            for case in switch(update.message.text.lower()):
                if case('主線相關角色'):
                    divs = soup.find_all('div',attrs={'id':['CollapsiblePanel1','CollapsiblePanel2','CollapsiblePanel9']})
                    break
                if case('黑暗組織'):
                    divs = soup.find_all('div',attrs={'id':['CollapsiblePanel10','CollapsiblePanel11','CollapsiblePanel12']})
                    break
                if case('警察'):
                    divs = soup.find_all('div',attrs={'id':['CollapsiblePanel3','CollapsiblePanel4','CollapsiblePanel5','CollapsiblePanel6']})
                    break
                if case('fbi&cia'):
                    divs = soup.find_all('div',attrs={'id':['CollapsiblePanel7','CollapsiblePanel8']})
                    break
                if case():
                    break
            global my_list
            global name_list
            my_list = []
            name_list = []
            count = 0
            for tr in divs:
                trs = tr.find_all('tr')
                for spans in trs:
                    span = spans.find_all('span',attrs={'class':'eeeee'})
                    nameMore=""                
                    countName = 0
                    for name in span:          
                        if not (name.string is None):
                            print(name.string)
                            name_list.append(name.string)
                            if countName==0:
                                nameMore += name.string
                            else:
                                nameMore += '('
                                nameMore += name.string
                                nameMore += ')'
                            countName += 1
                    my_list.append(nameMore)
            my_list.append("\n返回")
            name_list.append("返回")
            update.message.reply_text('\n'.join(my_list))
            self.advance(update)

    def on_exit_category(self, update):
        print('Leaving category')

    def on_enter_character(self, update): 
        global count
        count = 0        
        if update.message.text.lower()=='返回':
            self.go_back(update)
        else:
            global searchName
            print(searchName)
            result = soup.find(text=searchName)
            content = result.findParent('td').find_all('p')[1]
            link = result.findParent('td').find_all('p')
            if len(link)<3:
                update.message.reply_text(searchName)
            else:        
                link = result.findParent('td').find_all('p')[2].contents[1] 
                update.message.reply_text(text=str(link),parse_mode=telegram.ParseMode.HTML)
            if len(content)==1: 
                update.message.reply_text(content.contents[0])
            else:
                if not (content.contents[0] is None): 
                    update.message.reply_text(content.contents[0])
                else:
                    update.message.reply_text(content.contents[1].text)
            #update.message.reply_text(content.contents[1].text)    
            img = "http://www.conan.url.tw/"
            url = result.findParent('td').findParent('tr').find('img')
            if not (url is None):
                img += url["src"]
                update.message.reply_photo(photo=img)
            self.advance(update)
            

    def on_exit_character(self, update):
        print('Leaving character')

    def on_enter_final1(self, update):
        custom_keyboard = [['認識角色'],['劇場版介紹'],['愛情支線查詢']]
        reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
        update.message.reply_text("我不是兇手\n但你可以選擇以下功能\n",reply_markup=reply_markup)
        self.go_back(update)

    def on_exit_final1(self, update):
        print('Leaving final1')

    def on_enter_movie(self, update):
        global count       
        if update.message.text.lower()=='返回' and count!=0:
            self.go_back(update)
        else:
            custom_keyboard = [['1'],['2'],['返回']]
            reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
            update.message.reply_text("想觀看預告 請輸入1\n想觀看簡介 請輸入2\n\n返回",reply_markup=reply_markup)
            count = 0
            self.advance(update)

    def on_exit_movie(self, update):
        print('Leaving movie')

    def on_enter_description(self, update):
        global count
        count = 0        
        if update.message.text.lower()=='返回':
            self.go_back(update)
        else:
            searchDe="第"
            searchDe+=str(movieNum)
            searchDe+="部"
            movie_list = []
            for case in switch(update.message.text):
                if case('1'):
                    if movieNum==14:
                        img = "https://zh.wikipedia.org/wiki/%E5%90%8D%E4%BE%A6%E6%8E%A2%E6%9F%AF%E5%8D%97%EF%BC%9A%E5%A4%A9%E7%A9%BA%E7%9A%84%E9%81%87%E9%9A%BE%E8%88%B9#/media/File:Conan_14.jpg"
                    elif movieNum==19:
                        img = "https://zh.wikipedia.org/wiki/%E5%90%8D%E5%81%B5%E6%8E%A2%E6%9F%AF%E5%8D%97%EF%BC%9A%E6%A5%AD%E7%81%AB%E7%9A%84%E5%90%91%E6%97%A5%E8%91%B5#/media/File:Detective_Conan_the_movie_19.jpg"
                    else:
                        result = soup2.find(text=searchDe)
                        img = "http://www.conan.url.tw/"
                        img += result.findParent('td').findParent('tr').find('img')["src"]
                    update.message.reply_photo(photo=img)
                    if movieNum==1:
                        moviename = "M"+str(movieNum)
                    elif movieNum<10:
                        moviename = "M0"+str(movieNum)
                    else:
                        moviename = "M"+str(movieNum)
                    link = "https://www.bilibili.com/"
                    link += soupt.find(text=re.compile(moviename)).findParent('option')["value"]
                    update.message.reply_text("預告連結: %s" % link)                  
                    break
                    #filename = "M"+str(movieNum)+".mp4"
                    #file1 = open(filename,'rb')
                    #update.message.reply_video(video=file1)
                    #file1.close()
                if case('2'):
                    result = soup2.find(text=searchDe)
                    update.message.reply_text(result.findParent('td').find('h4').text.split("\n")[1])
                    contents = result.findParent('td').find_all('p')
                    for p in contents:
                        if not (p.find('a',href=True) is None):
                            movie_list.append("更多資料:")
                            movie_list.append(p.find('a').get('href'))
                        elif not (p.text is None):
                            movie_list.append(p.text.replace(" ",""))
                            movie_list.append(" ")
                    update.message.reply_text('\n'.join(movie_list))
                    break
            self.advance(update)

    def on_exit_description(self, update):
        print('Leaving description')

    def on_enter_final2(self, update):
        custom_keyboard = [['認識角色'],['劇場版介紹'],['愛情支線查詢']]
        reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
        update.message.reply_text("我不是兇手\n但你可以選擇以下功能\n認識角色",reply_markup=reply_markup)
        self.go_back(update)

    def on_exit_final2(self, update):
        print('Leaving final2')

    def on_enter_loveline(self, update):
        global count
        count = 0        
        if update.message.text=='返回':
            self.go_back(update)
        else:
            global loveNum
            for case in switch(loveNum):
                love_list = []
                if case(1):
                    divs = soup3.find_all('div',attrs={'id':['CollapsiblePanel1']})
                    break
                if case(2):
                    divs = soup3.find_all('div',attrs={'id':['CollapsiblePanel10']})
                    break
                if case(3):
                    divs = soup3.find_all('div',attrs={'id':['CollapsiblePanel2']})
                    break
                if case(4):
                    divs = soup3.find_all('div',attrs={'id':['CollapsiblePanel3']})
                    break
                if case(5):
                    divs = soup3.find_all('div',attrs={'id':['CollapsiblePanel4']})
                    break
                if case(6):
                    divs = soup3.find_all('div',attrs={'id':['CollapsiblePanel7']})
                    break
                if case(7):
                    divs = soup3.find_all('div',attrs={'id':['CollapsiblePanel6']})
                    break
                if case(8):
                    divs = soup3.find_all('div',attrs={'id':['CollapsiblePanel8']})
                    break
                if case(9):
                    divs = soup3.find_all('div',attrs={'id':['CollapsiblePanel9']})
                    break
                if case():
                    break
            count = 0    
            for tds in divs:
                td = tds.find_all('td',attrs={'class':['title2']})
                for s in td:                    
                    num = s.text.split("\n")[0]
                    link = "http://www.conan.url.tw/"+s.findParent('tr').find('img')["src"]
                    name = "[{}]({})"
                    love_list.append(name.format(num,link))
            love_list.append("\n點擊可查看相片喔")
            update.message.reply_text('\n'.join(str(l) for l in love_list),parse_mode=telegram.ParseMode.MARKDOWN)
            #yo = "%s" % str(loveNum)
            #link = "http://www.conan.url.com/lovelist/85.jpg"
            
            #update.message.reply_text(text=name.format(str(loveNum),link),parse_mode=telegram.ParseMode.MARKDOWN)
            self.advance(update)

    def on_exit_loveline(self, update):
        print('Leaving loveline')

    def on_enter_final3(self, update):
        custom_keyboard = [['認識角色'],['劇場版介紹'],['愛情支線查詢']]
        reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
        update.message.reply_text("我不是兇手\n但你可以選擇以下功能",reply_markup=reply_markup)
        self.go_back(update)

    def on_exit_final3(self, update):
        print('Leaving final3')

    def on_enter_garbage(self, update):
        custom_keyboard = [['認識角色'],['劇場版介紹'],['愛情支線查詢']]
        reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
        update.message.reply_text("我不是兇手\n但你可以選擇以下功能",reply_markup=reply_markup)
        self.go_back(update)

    def on_exit_garbage(self, update):
        print('Leaving garbage')
