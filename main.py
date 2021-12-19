from pythonosc.osc_server import AsyncIOOSCUDPServer
from pythonosc.dispatcher import Dispatcher
import asyncio

#from dynamixel_sdk import * # Uses Dynamixel SDK library
from dxl_controller import dxl_controller
import keyboard

dcon41 = dxl_controller(41)
#dcon42 = dxl_controller(42)


#dcon42.release()

def filter_handler(address, *args):
    print(f"{address}: {args}")

    
dispatcher = Dispatcher()
dispatcher.map("/filter", filter_handler)

ip = "127.0.0.1"
port = 1337


async def loop():
    while(1):
        try:
            if keyboard.read_key() == "b":
                dcon41.controllVelocity(10)
                
            if keyboard.read_key() == "a":
                dcon41.controllVelocity(0)
            
            if keyboard.read_key() == "q":
                dcon41.release()
        except KeyboardInterrupt:
            dcon41.release()
            break



async def init_main():
    server = AsyncIOOSCUDPServer((ip, port), dispatcher, asyncio.get_event_loop())
    transport, protocol = await server.create_serve_endpoint()  # Create datagram endpoint and start serving

    await loop()  # Enter main loop of program

    transport.close()  # Clean up serve endpoint


asyncio.run(init_main())