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
InPocket = {'rub':args.rub,'eur':args.eur,'usd':args.usd}
#################################LOG################################
logger = logging.getLogger('Api_wallet_main')
FORMAT = '%(asctime)s  %(name)s [%(levelname)s]: %(message)s'
file_handler = logging.FileHandler('Api_wallet.log', 'w', encoding='utf-8')
file_handler.setFormatter(logging.Formatter(FORMAT))

# уровень логгинга (DEBUG или INFO)
if args.debug in DebugOn:
    logging.basicConfig(level=logging.DEBUG, format=FORMAT, datefmt='%Y/%m/%d %H:%M')
else:
    logging.basicConfig(level=logging.INFO, format=FORMAT, datefmt='%Y/%m/%d %H:%M')

logger.addHandler(file_handler)
#logging.getLogger('asyncio').setLevel(logging.INFO)
##############################Functions#############################
async def get_data_about_course(session,url):
    logger.debug('WORK Function get_data_about_course')
    while True:
        async with session.get(url) as response:
            try:
                data = await response.read()
                json_response = json.loads(data)
            except Exception as error:
                logger.error('Error in receiving the exchange rate.'
                              'Error description from interpreter:{error}'.format(error=error))
        if isinstance(json_response, dict) and json_response != {}:
            logger.info('Data about exchange received successfully')
            try:

                for valuteX in json_response['Valute']:
                    table['RUB' + '-' + valuteX] = 1 / json_response['Valute'][valuteX]['Value']
                    table[valuteX + '-' + 'RUB'] = json_response['Valute'][valuteX]['Value']
                    for valuteY in json_response['Valute']:
                        table[valuteX + '-' + valuteY] = json_response['Valute'][valuteX]['Value'] \
                                                         / json_response['Valute'][valuteY]['Value']
                table['RUB-RUB'] = 1.0
                logging.debug('LIST with data about exchanges :{table}'.format(table=table['RUB-RUB']))
            except Exception as error:
                logger.error('Error in receiving the exchange rate.'
                              'Error description from interpreter:{error}'.format(error=error))
            response.close()
        await asyncio.sleep(TimesPerMinute)

async def test_print():
    while True:
        logging.info('\nRUB:{RUB}\nEUR:{EUR}\nUSD:{USD}'.format(RUB=InPocket.get('rub'),
                                                                EUR=InPocket.get('eur'),
                                                                USD=InPocket.get('usd')))
        await asyncio.sleep(5)

async def main(loop):
    logger.debug('WORK Function main')
    logger.info('Aplication [Wallet App] started')
    urls = ["https://www.cbr-xml-daily.ru/daily_json.js"]
    async with aiohttp.ClientSession(loop=loop) as session:
        tasks = [get_data_about_course(session, url) for url in urls]
        await asyncio.gather(*tasks)

async def api_get(request):
    TextForResponse = ''
    summ = {}
    for key in InPocket:
        summ[key] = 0
    url = str(request.url.raw_parts[-2])  # usd, eur или rub
    if url == 'amount':
        for valute, cash in InPocket.items():
            TextForResponse += '{value}:{cash}\n'.format(value=valute, cash=cash)
            for valute_x, cash_x in InPocket.items():
                summ[valute] += (cash_x * table[valute_x.upper() + '-' + valute.upper()])
                logger.info(str(summ))
        TextForResponse += 'rub-usd:{rub_usd}\n' \
                           'rub-eur:{rub_eur}\n' \
                           'eur-usd:{eur_usd}\n'.format(rub_usd=table['USD-RUB'],
                                                        rub_eur=table['EUR-RUB'],
                                                        eur_usd=table['EUR-USD'],)
        TextForResponse += 'sum:'
        for valute, summ_x in summ.items():
            TextForResponse += '{summ:.2f} {valute} /'.format(summ=summ_x,valute=valute)

    else:
        TextForResponse = 'TEST'
    response = web.Response(status=200, reason='ОК',
                            text=TextForResponse, charset='utf-8',
                            content_type='text/plain')
    return response
async def api_post(request):
    reason = request.url.raw_parts[-1]  # set или modify

    return web.Response(status=200, reason='ОК',
                        text=reason,
                        charset='utf-8', content_type='text/plain')
def create_runner():
    app = web.Application()
    app.add_routes([
        web.get('/rub/get', api_get),
        web.get('/usd/get', api_get),
        web.get('/eur/get', api_get),
        web.get('/amount/get', api_get),
        web.post('/amount/set', api_post),
        web.post('/modify', api_post)])

    return web.AppRunner(app)
# Server
async def start_server(host='127.0.0.1', port=8080):
    runner = create_runner()
    await runner.setup()
    site = web.TCPSite(runner, host, port)
    await site.start()
    logger.info('SERVER START {host}:{port}'.format(host=host, port=port))

if __name__=="__main__":
    loop = asyncio.get_event_loop()
    tasks = [
            loop.create_task(start_server()),
            loop.create_task(main(loop)),
            loop.create_task(test_print()),
            ]
    loop.run_until_complete(asyncio.wait(tasks))
    loop.run_forever()
    loop.close()








