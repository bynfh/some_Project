import asyncio
import aiohttp
import argparse
import logging
import json
from aiohttp import web
from ZeroTouch.ClassUH_ID import ClassSwitchesInHouse
from ZeroTouch import test

#################################LOG################################
logger = logging.getLogger('Api_wallet_main')
FORMAT = '%(asctime)s  %(name)s [%(levelname)s]: %(message)s'
file_handler = logging.FileHandler('Api_wallet.log', 'a', encoding='utf-8')
file_handler.setFormatter(logging.Formatter(FORMAT))

# choose level logging (DEBUG или INFO)
logging.basicConfig(level=logging.DEBUG, format=FORMAT, datefmt='%Y/%m/%d %H:%M')
logger.addHandler(file_handler)
logging.getLogger('asyncio').setLevel(logging.INFO)

async def FirstApi(request):
    JsonFromRequest = json.loads(request.match_info['json'])

    a = ClassSwitchesInHouse(str(JsonFromRequest['UH_IDs'][0]['UH_ID']))
    a = test.main()
    response = web.Response(status=200, reason='ОК',
                            text='KAEF', charset='utf-8',
                            content_type='text/plain')
    return response

def create_runner():
    logger.debug('WORKING Function create_runner')
    app = web.Application()
    app.add_routes([
    #     web.get('/amount/get', GetAmount),
    #     web.get('/{name}/get', GetValueValute),
    #     web.post('/amount/set', PostAmountSet),
         web.get('/api_zero_touch/get_unified_house_id/json={json}', FirstApi)])

    return web.AppRunner(app)

async def start_server(host='127.0.0.1', port=8080):
    logger.debug('WORKING Function start_server')
    runner = create_runner()
    await runner.setup()
    site = web.TCPSite(runner, host, port)
    await site.start()
    logger.info('SERVER START {host}:{port}'.format(host=host, port=port))

async def main(loop):
    logger.debug('WORKING Function main')
    logger.info('Aplication [Wallet App] started')
    # urls = ["https://www.cbr-xml-daily.ru/daily_json.js"]
    # async with aiohttp.ClientSession(loop=loop) as session:
    #     tasks = [get_data_about_course(session, url) for url in urls]
    #     await asyncio.gather(*tasks)

if __name__ == "__main__":
    try:
        loop = asyncio.get_event_loop()
        tasks = [
                loop.create_task(start_server()),
                loop.create_task(main(loop)),
                ]
        loop.run_until_complete(asyncio.wait(tasks))
        loop.run_forever()
        loop.close()
    except KeyboardInterrupt:
        logger.debug("You stopped program")
    except Exception as Error:
        logger.debug("This error unknown:{error}".format(error=Error))