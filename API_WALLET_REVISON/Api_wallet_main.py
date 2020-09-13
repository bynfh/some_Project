import asyncio
import aiohttp
import argparse
import logging
import json
from aiohttp.abc import AbstractAccessLogger
# import requests
from aiohttp import web
from Class_wallet import Wallet

class AccessLogger(AbstractAccessLogger):

    def log(self, request, response, time):

        if request.method == 'POST':
            self.logger.debug('Request: ' + str(request.remote) + ' ' +
                          str(request.method) + ' ' + str(request.path))
            self.logger.debug('Response code: ' + str(response.status) +
                               ' | ' + str(response.text))

        elif request.method == 'GET':
            self.logger.debug('Request: ' + str(request.remote) + ' ' +
                          str(request.method) + ' ' + str(request.path))
            self.logger.debug('Response code: ' + str(response.status))
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
MyWallet = Wallet({'rub':args.rub, 'eur':args.eur, 'usd':args.usd})
#################################LOG################################
logger = logging.getLogger('Api_wallet_main')
FORMAT = '%(asctime)s  %(name)s [%(levelname)s]: %(message)s'
file_handler = logging.FileHandler('Api_wallet.log', 'a', encoding='utf-8')
file_handler.setFormatter(logging.Formatter(FORMAT))

# choose level logging (DEBUG или INFO)
if args.debug in DebugOn:
    logging.basicConfig(level=logging.DEBUG, format=FORMAT, datefmt='%Y/%m/%d %H:%M')
else:
    logging.basicConfig(level=logging.INFO, format=FORMAT, datefmt='%Y/%m/%d %H:%M')

logger.addHandler(file_handler)
logging.getLogger('asyncio').setLevel(logging.INFO)
logger.debug('\n\nTHIS START:Input data receive successful, object MyWallet with cash created:{obj}'.format(obj=MyWallet.CashInWallet))
##############################Functions#############################
async def get_data_about_course(session,url):
    logger.debug('WORKING Function get_data_about_course')
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
                MyWallet.SetRate(table)

            except Exception as error:
                logger.error('Error in receiving the exchange rate.'
                             'Error description from interpreter:{error}'.format(error=error))
            response.close()
        await asyncio.sleep(TimesPerMinute)

async def GetValueValute(request):
    Valute = str(request.url.raw_parts[-2])  # usd, eur, rub or another
    try:
        Value = str(MyWallet.GetValuesCashInWallet(Valute))
        TextForResponse = Valute + ':' + Value
    except AssertionError as ClassError:
        TextForResponse = 'You used unsupport valute:{valute}'.format(valute=Valute)
        logger.warning(TextForResponse + ' Exception from class:{error}'.format(valute=Valute,
                                                                                error= ClassError))


    response = web.Response(status=200, reason='ОК',
                            text=TextForResponse, charset='utf-8',
                            content_type='text/plain')
    return response

async def GetAmount(request):
    TextForResponse = ''
    Cash = MyWallet.CashInWallet
    Rate = MyWallet.Rate
    try:
        for valute, cash in Cash.items():
            TextForResponse += '{value}:{cash}\n'.format(value=valute, cash=cash)

        for valute in Cash:
            for valute_x in Cash:
                if valute_x != valute and valute_x == 'rub':
                    NeedRate = (str(valute).upper() + '-' + str(valute_x).upper())
                    TextForResponse += '{Name}:{Value:.2f}\n'.format(Name=NeedRate, Value=Rate[NeedRate])

        TextForResponse += 'sum:'
        for valute in Cash:
            amount = MyWallet.GetAmountInAnyValute(valute)
            TextForResponse += '{summ:.2f} {valute}|'.format(summ=amount, valute=valute)
    except AssertionError as ClassError:
        TextForResponse = 'You used unsupported valute'
        logger.warning('You used unsupported valute:{error}'.format(error=ClassError))
    response = web.Response(status=200, reason='ОК',
                            text=TextForResponse, charset='utf-8',
                            content_type='text/plain')
    return response

async def PostAmountSet(request):
    reason = ''
    res = await request.content.read()

    try:
        JsonResponse = json.loads(res)
        MyWallet.SetCashInWallet(JsonResponse)
        for key, value in JsonResponse.items():
            reason += 'You set {valute}:{value}\n'.format(valute=key, value=value)
    except json.decoder.JSONDecodeError:
        reason = 'Incorrect data'
        logger.warning('Incorrect data')
    except AssertionError as ClassError:
        reason = 'You used unsupported valute. {valute}'.format(valute=ClassError)
        logger.warning(reason)

    return web.Response(status=200, reason='ОК',
                        text=reason,
                        charset='utf-8', content_type='text/plain')

async def PostModify(request):
    reason = ''
    res = await request.content.read()

    try:
        JsonResponse = json.loads(res)
        MyWallet.ModifyCashInWallet(JsonResponse)
        for key, value in JsonResponse.items():
            reason += 'You modify {valute}:{value}\n'.format(valute=key, value=value)
    except json.decoder.JSONDecodeError:
        reason = 'Incorrect data'
        logger.warning(reason)
    except AssertionError as ClassError:
        reason = 'You used unsupported valute. {valute}'.format(valute=ClassError)
        logger.warning(reason)

    return web.Response(status=200, reason='ОК',
                        text=reason,
                        charset='utf-8', content_type='text/plain')

def create_runner():
    logger.debug('WORKING Function create_runner')
    app = web.Application()
    app.add_routes([
        web.get('/amount/get', GetAmount),
        web.get('/{name}/get', GetValueValute),
        web.post('/amount/set', PostAmountSet),
        web.post('/modify', PostModify)])

    return web.AppRunner(app, access_log_class=AccessLogger)
# Servers
async def start_server(host='127.0.0.1', port=8080):
    logger.debug('WORKING Function start_server')
    runner = create_runner()
    await runner.setup()
    site = web.TCPSite(runner, host, port)
    await site.start()
    logger.info('SERVER START {host}:{port}'.format(host=host, port=port))

async def print_to_console():
    NeedRate = ''
    while True:
        CheckRate = MyWallet.CheckChangeRate()
        CheckCash = MyWallet.CheckChangeCash()
        TextForResponse = ''

        if (CheckRate is not None and CheckCash is True) or CheckRate is True:
            Cash = MyWallet.CashInWallet
            Rate = MyWallet.Rate

            for valute, cash in Cash.items():
                TextForResponse += '{value}:{cash} \n'.format(value=valute, cash=cash)

            for valute in Cash:
                for valute_x in Cash:
                    if valute_x != valute and valute_x == 'rub':
                        NeedRate = (str(valute).upper() + '-' + str(valute_x).upper())
                        TextForResponse += '{Name}:{Value:.2f}\n'.format(Name = NeedRate,Value = Rate[NeedRate])

            TextForResponse += 'sum:'
            for valute in Cash:
                amount = MyWallet.GetAmountInAnyValute(valute)
                TextForResponse += '{summ:.2f} {valute}|'.format(summ=amount, valute=valute)

            logger.info('Cash or Curse is change:\n{data}'.format(data=TextForResponse))
            await asyncio.sleep(60)
        else:
            await asyncio.sleep(1)


async def main(loop):
    logger.debug('WORKING Function main')
    logger.info('Aplication [Wallet App] started')
    urls = ["https://www.cbr-xml-daily.ru/daily_json.js"]
    async with aiohttp.ClientSession(loop=loop) as session:
        tasks = [get_data_about_course(session, url) for url in urls]
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








