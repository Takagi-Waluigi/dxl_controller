from pythonosc.osc_server import AsyncIOOSCUDPServer
from pythonosc.dispatcher import Dispatcher
import asyncio
 
 #from dynamixel_sdk import * # Uses Dynamixel SDK library
from dxl_controller import dxl_controller
 
dxlCon = dxl_controller(41, 42)
#dcon42 = dxl_controller(42)
 
vel = 0
 
#dcon42.release()
 
def filter_handler(address, *args):
    global vel
    vel = args[0]
    #print(f"{address}: {args}")
 
     
dispatcher = Dispatcher()
dispatcher.map("/vel", filter_handler)
 
ip = "127.0.0.1"
port = 1337
 
 
async def loop():
    global vel
    while(1):
         
        try:
            dxlCon.controllVelocity(41, 0)
            dxlCon.controllVelocity(42, 0)
           # dcon42.controllVelocity(vel)
           # await asyncio.sleep(0.00001)
        except KeyboardInterrupt:
            dxlCon.controllVelocity(0)
            dxlCon.release()
            break

 
async def init_main():
    server = AsyncIOOSCUDPServer((ip, port), dispatcher, asyncio.get_event_loop())
    transport, protocol = await server.create_serve_endpoint()

    await loop()
    transport.close()
 
asyncio.run(init_main())