import asyncio
import datetime as dt
import struct

from random import randrange
from zoneinfo import ZoneInfo

writers = []
all_writers = {}
weather = b''


async def prepare_weather_data(t):
    global weather, writers
    try:
        while True:
            await asyncio.sleep(randrange(0, 7))
            now = dt.datetime.now(ZoneInfo("Europe/Kyiv")).replace(microsecond=0).isoformat()
            message = f"{now} The temperature is {str(randrange(20, 30))} degrees Celsius"

            message_encoded = message.encode()
            message_length = struct.pack('>I', len(message_encoded))

            weather = message_length + message_encoded

            writers = []
            print(message)
    except asyncio.CancelledError:
        t.cancel()


async def read_message(reader: asyncio.StreamReader):
    # Read the 4-byte length header
    length_data = await reader.readexactly(4)
    message_length = struct.unpack('>I', length_data)[0]
    message_encoded = await reader.readexactly(message_length)
    return message_encoded.decode()


async def handle_client(
    writer: asyncio.StreamWriter,
):
    socname = writer.get_extra_info('peername')
    try:
        while True:
            # todo: refactor to avoid sleep
            await asyncio.sleep(0)
            if socname not in writers:
                writers.append(socname)
                writer.write(weather)
                await writer.drain()
    except* ConnectionResetError:
        del all_writers[socname]
        writer.close()
        print(f'Socket {socname} closed')
    except* asyncio.CancelledError:
        pass
    except* Exception as e:
        print(f'ERROR: {str(e)}')
        raise e


async def client_handler(reader, writer):
    socname = writer.get_extra_info('peername')
    all_writers[socname] = writer
    message = await read_message(reader)
    print(f"Socket {socname} connected. Received message: \"{message}\"")
    await handle_client(writer)


async def run_server():
    server = await asyncio.start_server(client_handler, "localhost", 8000)
    print(f'Serving on {server.sockets[0].getsockname()}')
    async with server:
        try:
            await server.serve_forever()
        finally:
            for writer in all_writers.values():
                writer.close()

async def main():
    try:
        async with asyncio.TaskGroup() as group:
            t = group.create_task(run_server())
            group.create_task(prepare_weather_data(t))
    except* asyncio.CancelledError:
        print('Stopped by user')


if __name__ == "__main__":
    asyncio.run(main())
