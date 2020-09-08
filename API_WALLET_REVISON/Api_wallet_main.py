import asyncio
import aiohttp
import argparse
import logging
import json
from aiohttp.abc import AbstractAccessLogger
import requests
import time
from aiohttp import web
import pprint
from Class_wallet import Wallet
class AccessLogger(AbstractAccessLogger):

    def log(self, request, response, time):

        if request.method == 'POST':
            self.logger.debug('Request: ' + str(request.remote) + ' ' +
                          str(request.method) + ' ' + str(request.path))
            self.logger.debug('Response code: ' + str(response.status) +
                              ' | ' + str(response.text))

        elif request.method == 'GET':
            self.logger.info('Request: ' + str(request.remote) + ' ' +
                          str(request.method) + ' ' + str(request.path))
            self.logger.info('Response code: ' + str(response.status))
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
ClassInitialization = Wallet({'rub':args.rub,'eur':args.eur,'usd':args.usd})
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
logging.getLogger('asyncio').setLevel(logging.INFO)
logger.debug('Constant, argparse, log successful')
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
                table['RUB-RUB'] = 1.0 # For full array
                #logging.debug('LIST with data about exchanges :{table}'.format(table=table['RUB-RUB']))
            except Exception as error:
                logger.error('Error in receiving the exchange rate.'
                              'Error description from interpreter:{error}'.format(error=error))
            response.close()
        await asyncio.sleep(TimesPerMinute)

async def get_values_valute(request):
    url = str(request.url.raw_parts[-2])  # usd, eur или rub
    TextForResponse = str(InPocket[url])
    logger.info(url)
    response = web.Response(status=200, reason='ОК',
                            text=TextForResponse, charset='utf-8',
                            content_type='text/plain')
    return response

async def api_get_amount(request):
    TextForResponse = ''
    summ = {}
    for key in InPocket:
        summ[key] = 0

    for valute, cash in InPocket.items():
        TextForResponse += '{value}:{cash}\n'.format(value=valute, cash=cash)
        for valute_x, cash_x in InPocket.items():
            summ[valute] += (cash_x * table[valute_x.upper() + '-' + valute.upper()])
    TextForResponse += 'rub-usd:{rub_usd:.2f}\n' \
                       'rub-eur:{rub_eur:.2f}\n' \
                       'eur-usd:{eur_usd:.2f}\n'.format(rub_usd=table['USD-RUB'],
                                                        rub_eur=table['EUR-RUB'],
                                                        eur_usd=table['EUR-USD'],)
    TextForResponse += 'sum:'
    for valute, summ_x in summ.items():
        TextForResponse += '{summ:.2f} {valute} /'.format(summ=summ_x, valute=valute)

    response = web.Response(status=200, reason='ОК',
                            text=TextForResponse, charset='utf-8',
                            content_type='text/plain')
    return response

async def api_post_set(request):
    reason = ''
    res = await request.content.read()
    try:
        s = json.loads(res)
        for key, value in s.items():
            InPocket[key] = value
            reason += 'You set {valute}:{value}\n'.format(valute=key, value=value)
    except json.decoder.JSONDecodeError:
        reason = 'Incorrect data'
    return web.Response(status=200, reason='ОК',
                        text=reason,
                        charset='utf-8', content_type='text/plain')

async def api_post_modify(request):
    reason = ''
    res = await request.content.read()
    try:
        s = json.loads(res)
        for key, value in s.items():
            InPocket[key] += value
            reason += 'You modify {valute}:{value}\n'.format(valute=key, value=value)
    except json.decoder.JSONDecodeError:
        reason = 'Incorrect data'
    return web.Response(status=200, reason='ОК',
                        text=reason,
                        charset='utf-8', content_type='text/plain')

def create_runner():
    logger.debug('WORK Function create_runner')
    app = web.Application()
    app.add_routes([
        web.get('/rub/get', get_values_valute),
        web.get('/usd/get', get_values_valute),
        web.get('/eur/get', get_values_valute),
        web.get('/amount/get', api_get_amount),
        web.post('/amount/set', api_post_set),
        web.post('/modify', api_post_modify)])

    return web.AppRunner(app, access_log_class=AccessLogger)
# Servers
async def start_server(host='127.0.0.1', port=8080):
    logger.debug('WORK Function start_server')
    runner = create_runner()
    await runner.setup()
    site = web.TCPSite(runner, host, port)
    await site.start()
    logger.info('SERVER START {host}:{port}'.format(host=host, port=port))

async def print_to_console():
    while True:
        TextForResponse = ''
        if table != {}:
            if ClassInitialization.CheckChangeCashInPocket(InPocket) is True\
            or ClassInitialization.CheckChangeCourseValute(table):
                CashInPocket = ClassInitialization.DataAboutCashLocal
                CourseValute = ClassInitialization.DataAboutCourseLocal
                for valute, cash in CashInPocket.items():
                    TextForResponse += '{value}:{cash} '.format(value=valute, cash=cash)


                TextForResponse += '\nrub-usd:{rub_usd:.2f}\n' \
                                   'rub-eur:{rub_eur:.2f}\n' \
                                   'eur-usd:{eur_usd:.2f}\n'.format(rub_usd=CourseValute['USD-RUB'],
                                                                    rub_eur=CourseValute['EUR-RUB'],
                                                                    eur_usd=CourseValute['EUR-USD'],)

                logger.info('Cash or Curse is change:\n{data}'.format(data=TextForResponse))
        await asyncio.sleep(3)

async def main(loop):
    logger.debug('WORK Function main')
    logger.info('Aplication [Wallet App] started')
    urls = ["https://www.cbr-xml-daily.ru/daily_json.js"]
    async with aiohttp.ClientSession(loop=loop) as session:
        tasks = [get_data_about_course(session, url) for url in urls]
        # task = print_to_console()
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    try:
        loop = asyncio.get_event_loop()
        tasks = [
                loop.create_task(start_server()),
                loop.create_task(main(loop)),
                loop.create_task(print_to_console()),
                ]
        loop.run_until_complete(asyncio.wait(tasks))
        loop.run_forever()
        loop.close()
    except KeyboardInterrupt:
        logger.debug("You stopped program")








