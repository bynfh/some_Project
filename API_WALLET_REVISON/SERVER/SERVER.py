from aiohttp import web
import asyncio
import aiohttp
import argparse
import logging
import time
import os

##############################ARGPARSE##############################
parser = argparse.ArgumentParser(description='Server')
parser.add_argument('--debug', default=0, type=str,
                    help='Type or no into console, default = False')
args = parser.parse_args()
##############################CONSTANT##############################
DebugOn = ['1', 'true', 'True', 'y', 'Y']
#################################LOG################################
logger = logging.getLogger(__name__)
FORMAT = '%(asctime)s %(name)s [%(levelname)s]: %(message)s'
file_handler = logging.FileHandler(os.path.join( os.path.dirname(__file__), '..' ) + '/Log/Server.log', 'w', encoding='utf-8')
file_handler.setFormatter(logging.Formatter(FORMAT))

# уровень логгинга (DEBUG или INFO)
if args.debug in DebugOn:
    logging.basicConfig(level=logging.DEBUG, format=FORMAT, datefmt='%Y/%m/%d %H:%M:%S')
else:
    logging.basicConfig(level=logging.INFO, format=FORMAT, datefmt='%Y/%m/%d %H:%M:%S')

logger.addHandler(file_handler)
logger.setLevel(logging.INFO)
logging.getLogger('asyncio').setLevel(logging.INFO)


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
    logger.info("SERVER {host}:{port} START".format(host=host,port=port))

if __name__=="__main__":
    loop = asyncio.get_event_loop()
    tasks = [
            loop.create_task(start_server()),
            ]
    loop.run_until_complete(asyncio.wait(tasks))
    loop.run_forever()
    loop.close()
