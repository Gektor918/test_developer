from oauth2client.service_account import ServiceAccountCredentials
from classed import Config, Data_base
from datetime import date
from urllib.request import urlopen
from xml.etree import ElementTree as etree
import httplib2
import apiclient
import datetime
import requests as req
import time


cfg = Config()
cur =  Data_base.connection.cursor()
conn = Data_base.connection


create_table_query = '''CREATE TABLE if not exists TESTDEVSHEETS4
    (
    NUMBER  INT,
    PRICE   REAL,
    DATE    TEXT,
    PRICE_DOLLAR   REALs
    ); '''
cur.execute(create_table_query)


today_date = datetime.datetime.strftime(date.today(), '%d.%m.%Y').replace('.','/')
link_dollar_rate = 'https://www.cbr.ru/scripts/XML_daily.asp?date_req='


def connect_api():
    '''
    Read (id, token, key), job servis, and authorization user
    '''
    read_json_file = ServiceAccountCredentials.from_json_keyfile_name(cfg.json_file, cfg.job_servis)
    httpAuth = read_json_file.authorize(httplib2.Http())
    client = apiclient.discovery.build('sheets','v4', http = httpAuth)
    return client


def dollar_rate(link_dollar_rate,today_date):
    '''
    Get values dollar on the to day
    '''
    with urlopen(link_dollar_rate+today_date) as r:
        dollar = etree.parse(r).findtext('.//Valute[@ID="R01235"]/Value').replace(',','.')
    return float("{0:.1f}".format(float(dollar)))


def get_values_sheets(client):
    '''
    Get and preparing values to send to the database create tuple
    '''
    values = client.spreadsheets().values().get(
        spreadsheetId=cfg.id_doc,
        range='main_list',
        majorDimension='ROWS',
        valueRenderOption = 'FORMATTED_VALUE'
    ).execute()
    # Start at element 1 because element 0 is the column name
    values_for_psg = tuple(values.get('values')[1:])
    return values_for_psg


def add_convert_dollar(values_for_psg,doll):
    '''
    Calculation of the price in rubles and add in tuple values
    '''
    for x in values_for_psg:
        new_values = [float("{0:.1f}".format(float(x[1])*doll))]
        x.extend(new_values)
    final_values_for_psg = tuple(tuple(i) for i in values_for_psg)
    return final_values_for_psg


def delivery_time(values_for_psg):
    '''
    Delivery date check and send message telergam, if list not empty,
    compare dates with today
    '''
    num_zak = []
    date_zak = []
    delivery_time = []
    # Create two list to combine into a dict
    for i in values_for_psg:
        num_zak+=[i[0]] 
        date_zak+=[i[2]] 
    fin = dict(zip(num_zak,date_zak))
    for i,x in fin.items():
        if date.today() >= datetime.datetime.strptime(x, '%d.%m.%Y').date():
            delivery_time += [[i,x]]
    if not delivery_time:
        return print('Not alert send')
    else:
        send_telegram(delivery_time)
        return print('Alert sent')


def send_telegram(list_delivery):
    '''
    Create messege and sending chat users messages via admin bot
    '''
    send = ''
    url = 'https://api.telegram.org/bot5485716008:AAGROwbh-UCTC9eZdC0yYRK-8fDkni9iI-E/sendMessage'
    channel_id = '-1001630445663'
    for i in list_delivery:
        send +='Заказ №:'+str(i[0])+'    '+'Дата:'+str(i[1])+'     '
    r = req.post(url,data={
        "chat_id": channel_id,
        "text": send,
        })
    if r.status_code != 200:
        raise Exception("text error")


def insert_entry_in_table(final_values_for_psg):
    '''
    Preparing the database and inserting new values
    '''
    cur.execute(""" DELETE FROM TESTDEVSHEETS4 """)
    conn.commit()
    for i in final_values_for_psg:
        cur.execute(
        """ INSERT INTO TESTDEVSHEETS4 (NUMBER, PRICE, DATE, PRICE_DOLLAR) VALUES (%s, %s, %s, %s)""", i)
    conn.commit()
    return print('Update successful')


if __name__ == '__main__':
    while True:
        time.sleep(5)
        client = connect_api()
        doll = dollar_rate(link_dollar_rate, today_date)
        values_for_psg = get_values_sheets(client)
        final_values_for_psg = add_convert_dollar(values_for_psg,doll)
        list_delivery = delivery_time(final_values_for_psg)
        insert_entry_in_table(final_values_for_psg)