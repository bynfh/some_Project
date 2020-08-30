import asyncio
import aiohttp
import argparse
import logging
import json
import requests
import time
from aiohttp import web
import pprint
##############################ARGPARSE##############################
parser = argparse.ArgumentParser(description='API_Wallet')
parser.add_argument('--period', default=1, type=int,
                    help='How many times per minute, default = 1')
parser.add_argument('--rub', default=0, type=int,
                    help='Value is rubles, default = 0')
parser.add_argument('--usd', default=0, type=int,
                    help='Value is usds, default = 0')
parser.add_argument('--eur', default=0, type=int,
                    help='Value is eurs, default = 0')
parser.add_argument('--debug', default=0, type=str,
                    help='Type or no into console, default = False')
args = parser.parse_args()
##############################CONSTANT##############################
table = {}
URL = 'https://www.cbr-xml-daily.ru/daily_json.js'
TimesPerMinute = args.period * 60
DebugOn = ['1', 'true', 'True', 'y', 'Y']
#################################LOG################################
# логирование
FORMAT = '%(asctime)s [%(levelname)s]: %(message)s'
file_handler = logging.FileHandler('Api_wallet.log', 'w', encoding='utf-8')
file_handler.setFormatter(logging.Formatter(FORMAT))

# уровень логгинга (DEBUG или INFO)
if args.debug in DebugOn:
    logging.basicConfig(level=logging.DEBUG, format=FORMAT, datefmt='%Y/%m/%d %H:%M:%S')
else:
    logging.basicConfig(level=logging.INFO, format=FORMAT, datefmt='%Y/%m/%d %H:%M:%S')

logging.getLogger().addHandler(file_handler)
logging.getLogger('asyncio').setLevel(logging.INFO)
##############################Functions#############################
async def get_data_about_course(session,url):
    logging.debug('WORK Function get_data_about_course')
    while True:
        async with session.get(url) as response:
            try:
                data = await response.read()
                json_response = json.loads(data)
            except Exception as error:
                logging.error('Error in receiving the exchange rate.'
                              'Error description from interpreter:{error}'.format(error=error))
        if isinstance(json_response, dict) and json_response != {}:
            logging.info('Data about exchange received successfully')
            try:

                for valuteX in json_response['Valute']:
                    table['RUB' + '-' + valuteX] = 1 / json_response['Valute'][valuteX]['Value']
                    table[valuteX + '-' + 'RUB'] = json_response['Valute'][valuteX]['Value']
                    for valuteY in json_response['Valute']:
                        table[valuteX + '-' + valuteY] = json_response['Valute'][valuteX]['Value'] \
                                                         / json_response['Valute'][valuteY]['Value']
                #logging.debug('LIST with data about exchanges :{table}'.format(table=table))
            except Exception as error:
                logging.error('Error in receiving the exchange rate.'
                              'Error description from interpreter:{error}'.format(error=error))
            response.close()
        await asyncio.sleep(TimesPerMinute)

async def test_print():
    while True:
        logging.debug('WORK Function test_print')

        await asyncio.sleep(5)
# Routes
def create_runner():
    app = web.Application()
    # app.add_routes([
    #     web.get('/rub/get', api_get),
    #     web.get('/usd/get', api_get),
    #     web.get('/eur/get', api_get),
    #     web.get('/amount/get', api_get),
    #     web.post('/amount/set', api_post),
    #     web.post('/modify', api_post)])

    return web.AppRunner(app)
# Server
async def start_server(host='127.0.0.1', port=8080):
    runner = create_runner()
    await runner.setup()
    site = web.TCPSite(runner, host, port)
    await site.start()

async def main(loop):
    logging.debug('WORK Function main')
    logging.info('Aplication [Wallet App] started')
    urls = ["https://www.cbr-xml-daily.ru/daily_json.js"]
    async with aiohttp.ClientSession(loop=loop) as session:
        tasks = [get_data_about_course(session, url) for url in urls]
        await asyncio.gather(*tasks)

if __name__=="__main__":
    loop = asyncio.get_event_loop()
    tasks = [
            loop.create_task(start_server()),
            loop.create_task(main(loop)),
            loop.create_task(test_print()),
            ]
    loop.run_until_complete(asyncio.wait(tasks))
    loop.close()






