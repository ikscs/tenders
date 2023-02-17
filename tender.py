#encoding: utf-8
import requests
from bs4 import BeautifulSoup as bs
from core.core_io import load_table, add_record
from core.play import Playwright

import os
import telebot
from datetime import datetime
import random
import time
import zlib

from core.credentials import TELEGRAM

TOKEN = TELEGRAM['token']
CHAT_ID = TELEGRAM['chat_id']

class TN_receiver:
    def __init__(self, keys, keys_minus, link):
        self.result = []
        self.count = 0
        self.keys = keys
        self.keys_minus = keys_minus
        self.link = link

        schema, path = self.link.split('://', 1)
        host, path = path.split('/', 1)
        self.host = '://'.join((schema, host.rstrip('/')))

    def __call__(self, title, link = None):
        link = self.link if link == None else link
        self.count += 1
        if not '://' in link:
            link = self.host + '/' + link.lstrip('/')
        if self.check_keys_minus(title.lower()):
            return
        if self.check_keys(title.lower()):
            self.result.append(f'<a href="{link}">{title}</a>')

    def check_keys(self, title):
        if not(self.keys): return True
        for key in self.keys:
            if key in title:
                return True
        return False

    def check_keys_minus(self, title):
        if not(self.keys_minus): return False
        for key in self.keys_minus:
            if key in title:
                return True
        return False

    @property
    def product(self):
        return self.result[9::-1], self.count

class Report:
    def __init__(self):
        self.body = ''

    def __call__(self, client, counter1, counter2, counter3):
        name = self.split_name(client)
        self.body += '<code>'
        if counter3:
            self.body += f'{name}{counter1:>5}{counter2:>5}{counter3:>5}'
        else:
            self.body += f'{name}   zero tenders'
        self.body += '</code>\n'

    def split_name(self, name):
        first_line = ''
        if len(name) > 15:
            first_line = f'{name[:30]}\n'
            name = name[30:]
        second_line = name
        while len(second_line) < 15:
            second_line += '.'
        return first_line + second_line

    def add_info(self, client, info):
        name = self.split_name(client)
        self.body += '<code>'
        self.body += f'{name}{info}'
        self.body += '</code>\n'
        pass

    def make_header(self):
        self.header = '<b>-= Tenders weekly report =-</b>\n'

    def make_footer(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        with open(current_dir + '/bender.txt', encoding='utf-8') as f:
            lines = f.read().splitlines()
        line = random.choice(lines)
        self.footer = f'\n---\n<i>{line}</i>\n'

    @property
    def text(self):
        self.make_header()
        self.make_footer()
        return self.header + self.body + self.footer

def load_site(tender_provider, method, time_sleep):
    client = tender_provider['client']
    url = tender_provider['url']

#    if method in ('requests', 'playwright'):
#        method = 'debug'

    if method == 'requests':
        resp = requests.get(url)
        content = resp.text
    elif method == 'playwright':
        play.get(url)
        time.sleep(time_sleep)
        content = play.page_source
#        with open('xxxx.html', 'w', encoding = 'utf-8') as f:
#            f.write(content)
    elif method == 'debug':
        with open('./banks/' + client + '.html', 'r', encoding = 'utf-8') as f:
            content = f.read()
    else:
        print(f'{client}: Missing loader function')
        content = ''
    return content

#Parser functions
def tenders_raif(content, receiver):
    for part in content.find_all('div', {'class' : 'faq-question'}):
        title = part.contents[0].strip()
        receiver(title)

def tenders_coe(content, receiver):
    for part in content.find_all('div', {'class' : 'clearfix'}):
        part = part.find('h3')
        if not part: continue
        title = part.contents[1].text.strip()
        link = part.contents[1].attrs['href']
        receiver(title, link)

def tenders_industrialbank(content, receiver):
    content = content.find('div', {'class' : 'content-page'})
    if not content: return
    for part in str(content).split('<hr/>'):
        block = bs(part, features='lxml').find('p')
        if not block: continue
        title = block.get_text().strip()
        if not 'оголошення' in title.lower(): continue
        receiver(title)

def tenders_ideabank(content, receiver):
    for part in content.find_all('article', {'class' : 'tenders-preview'}):
        title = '\n'.join([p.text.strip() for p in part.contents])
        receiver(title)

def tenders_comerc_industrial_bank(content, receiver):
    content = content.find('div', {'class' : 'page-content'})
    if not content: return
    for part in content.find_all('h3'):
        title = part.get_text().strip()
        receiver(title)

#def tenders_kominvestbank(content, receiver):

def tenders_cristall(content, receiver):
    for part in content.find_all('td', {'class' : 'list-title'}):
        title = part.contents[1].text.strip()
        link = part.contents[1].attrs['href']
        receiver(title, link)

def tenders_otp(content, receiver):
    content = content.find('div', {'class' : 'tenders_table'})
    if not content: return
    for part in content.find_all('td', {'data-label' : 'Назва'}):
        title = part.contents[0].text.strip()
        link = part.find('a').attrs['href']
        receiver(title, link)

def tenders_oshadbank(content, receiver):
    for part in content.find_all('h5', {'class' : 'procurement-card__title'}):
        title = part.contents[0].text.strip()
        receiver(title)

def tenders_pinbank(content, receiver):
    for part in content.find_all('h4', {'class' : 'vc_tta-panel-title'}):
        title = part.contents[0].text.strip()
        link = part.find('a').attrs['href']
        receiver(title, link)

#def tenders_pravex(content, receiver):

def tenders_privatbank(content, receiver):
    for part in content.find_all('div', {'class' : 'tender-col'})[1:]:
        title = part.contents[1].text.strip()
        link = part.contents[-2].text.split(' ')[-1].strip()
        receiver(title, link)

def tenders_procredit(content, receiver):
    content = content.find('ul', {'class' : 'tenders'})
    if not content: return
    for part in content.find_all('div', {'class' : 'title'}):
        title = part.text.strip()
        link = part.find('a').attrs['href']
        receiver(title, link)

def tenders_pumb(content, receiver):
    #https://smarttender.biz/tendermirror/?mirrorId=40536
    for part in content.find_all('div', {'data-qa' : 'trade-subject-title'}):
        link = part.find('a').attrs['href']
        if not '://' in link:
            link = receiver.host + '/' + link.lstrip('/')

        reuse_link = False
        for e in old_tenders:
            if link in e:
                #reuse link
                reuse_link = True
                receiver(*old_tenders[e])
        if reuse_link: continue

        #follow link
        content = load_site({'client': 'pumb', 'url': link}, 'playwright', 3)
        part = bs(content, features='lxml').find('h1', {'data-qa' : 'tender-title'})
        if not part: continue
        title = part.text.strip()
        receiver(title, link)

def tenders_ukrgasbank(content, receiver):
    content = content.find('div', {'class' : 'tenders-list'})
    if not content: return
    for part in content.find_all('h2'):
        title = part.text.strip()
        receiver(title)

def tenders_forward(content, receiver):
    content = content.find('div', {'class' : 'accordion'})
    if not content: return
    for part in content.find_all('div', {'class' : 'accordion_s'}):
        part = part.find_all('span')
        title = '\n'.join([p.text for p in part])
        receiver(title)

def tenders_x(content, receiver):
    #default unknown state
    receiver.count = '?'

    #Pravex bank
    if 'торгів на даний момент немає' in content.text:
        receiver.count = '-'
        return

    #UKRSIBBANK
    if 'немає тендерів' in content.text:
        receiver.count = '-'
        return

    #UKRSIBBANK2
    body = content.find_all('div', {'class' : 'module-text__descr'})
    if body:
        text = ''
        for e in body:
            text += e.text.strip()
        crc32 = zlib.crc32(bytes(text, 'utf-8'))
        if crc32 in (3801051663, 533529352):
            receiver.count = '-'
            return
        else:
            print(crc32, end=' ')

    #Kominvest bank
    body = content.find_all('div', {'class' : 'text'})
    if body:
        text = ''
        for e in body:
            text += e.text.strip()
        crc32 = zlib.crc32(bytes(text, 'utf-8'))
        if crc32 == 2867518990:
            receiver.count = '-'
            return
        else:
            print(crc32, end=' ')

    #UBRR
    body = content.find('main')
    if body:
        text = body.text.strip()
        crc32 = zlib.crc32(bytes(text, 'utf-8'))
        if crc32 == 774496847:
            receiver.count = '-'
            return
        else:
            print(crc32, end=' ')

def tenders_usembassy(content, receiver):
    url = content.find('link', {'rel' : 'canonical'}, href = True)
    url = url['href'] if url else ''

    content = content.find('div', {'class' : 'panel-group'})
    if not content: return

    for part in content.find_all('div', {'class' : 'panel-default'}):
        item = part.find('a')
        title = item.text

        link = item.attrs['href']
        if not link.startswith('http'):
            link = f'{url}{link}'
        receiver(title, link)

def load_keys(inp):
    if not inp: return []
    keys1 = inp.strip().strip('[ ]').split(',')
    keys = []
    for key in keys1:
        key = key.strip(' \'\"').lower()
        if key: keys.append(key)
    return keys

#Loader methods, parser functions
parsers = {
            'Райффайзен Банк': ('requests', 0, tenders_raif),
            'Рада Європи': ('requests', 0, tenders_coe),
            'Індустріалбанк': ('requests', 0, tenders_industrialbank),
            'Idea Bank (Ідея Банк)': ('playwright', 0, tenders_ideabank),
            'Комерційний Індустріальний Банк': ('requests', 0, tenders_comerc_industrial_bank),
#            'КомІнвестБанк': ('playwright', 0, tenders_kominvestbank),
            'КомІнвестБанк': ('playwright', 0, tenders_x),
            'КРИСТАЛ БАНК': ('requests', 0, tenders_cristall),
            'ОТП Банк': ('requests', 0, tenders_otp),
            'Ощадбанк': ('playwright', 7, tenders_oshadbank),
            'Перший Інвестиційний Банк': ('playwright', 2, tenders_pinbank),
#            'Правекс Банк': ('requests', 0, tenders_pravex),
            'Правекс Банк': ('requests', 0, tenders_x),
            'ПриватБанк': ('playwright', 5, tenders_privatbank),#
            'ПроКредит Банк': ('requests', 0, tenders_procredit),
            'Перший Український Міжнародний Банк': ('playwright', 3, tenders_pumb),#https://smarttender.biz/tendermirror/?mirrorId=40536
            'Укргазбанк': ('playwright', 0, tenders_ukrgasbank),
            'UKRSIBBANK': ('playwright', 0, tenders_x),
            'Український банк реконструкції та розвитку': ('requests', 0, tenders_x),
            'Forward Bank': ('requests', 0, tenders_forward),
            'U.S. Embassy': ('playwright', 0, tenders_usembassy),
          }

if __name__ == '__main__':
    bot = telebot.TeleBot(TOKEN)
    play = Playwright()
    friday_report = Report()

#    path_to_db = 'tn.db'
    path_to_db = None

    tn_tenders = load_table('tn_tenders', 'tender', path_to_db)
    old_tenders = dict()
    for old_tender in (e[0] for e in tn_tenders):
        link, title = old_tender.split('">')
        link = link.split('\"')[-1]
        title = title.split('</a>')[0]
        old_tenders[old_tender] = (title, link)

    tn_url_load = load_table('tn_url', 'id, klient, url, filtr, filtr_minus, flag', path_to_db)
    tender_providers = []
    for e in tn_url_load:
        tn = dict()
        tn['id'] = e[0]
        tn['client'] = e[1].strip()
        tn['url'] = e[2].strip()
        tn['filtr'] = load_keys(e[3])
        tn['filtr_minus'] = load_keys(e[4])
        tn['flag'] = e[5]
        tender_providers.append(tn)

    total_messages_send = 0
    for tender_provider in tender_providers:
        #Get client settings, bypass empty data
        client = tender_provider['client']
        if not tender_provider['flag']:
            friday_report.add_info(client, '       disabled')
            continue
        if not client in parsers:
            friday_report.add_info(client, 'provider missed')
            continue
        if not parsers[client]:
            friday_report.add_info(client, '  parser absend')
            continue

        #Get download method, timeout, parsed function from dictionary
        method, time_sleep, parser_function = parsers[client]

        #Get page contant with requests or playwright
        content = load_site(tender_provider, method, time_sleep)

        #Make soup
        parsed_html = bs(content, features='lxml')

        #Prepare receiver with filtr and default link
        receiver = TN_receiver(tender_provider['filtr'], tender_provider['filtr_minus'], tender_provider['url'])

        #Execute parser - fill receiver with tender titles and links
        parser_function(parsed_html, receiver)

        #Get filtered result
        new_tenders, count_total = receiver.product

        print(client, len(new_tenders), count_total)

        count_new = 0
        for new_tender in new_tenders:
            if not (new_tender in old_tenders):
                count_new += 1
                print(f'{client}: {new_tender}')
                if total_messages_send == 19: time.sleep(60)
                elif total_messages_send >= 19: time.sleep(3)
                try:
                    total_messages_send += 1
                    bot.send_message(CHAT_ID, text=f'<b>{client}</b>\n{new_tender}', parse_mode='html')
                except:
                    pass
                else:
                    add_record(table = 'tn_tenders', id_klient = tender_provider['id'], tender = new_tender, path = path_to_db)
        friday_report(client, count_new, len(new_tenders), count_total)

    print(friday_report.text)
    #Friday report
    if datetime.today().weekday() == 4:
        if total_messages_send >= 19: time.sleep(3)
        bot.send_message(CHAT_ID, text=friday_report.text, parse_mode='html')
    play.close()
