import asyncio
import datetime as dt
import struct

from random import randrange
from zoneinfo import ZoneInfo

writers = []
weather = b''

async def prepare_weather_data():
    global weather, writers
    while True:
        await asyncio.sleep(randrange(0, 7))
        now = dt.datetime.now(ZoneInfo("Europe/Kyiv")).replace(microsecond=0).isoformat()
        message = f"{now} The temperature is {str(randrange(20, 30))} degrees Celsius"

        message_encoded = message.encode()
        message_length = struct.pack('>I', len(message_encoded))

        weather = message_length + message_encoded

        writers = []
        print(message)


async def read_message(reader: asyncio.StreamReader):
    # Read the 4-byte length header
    length_data = await reader.readexactly(4)
    message_length = struct.unpack('>I', length_data)[0]
    message_encoded = await reader.readexactly(message_length)
    return message_encoded.decode()


async def handle_client(
    writer: asyncio.StreamWriter,
):
    try:
        socname = writer.get_extra_info('peername')
        while True:
            await asyncio.sleep(0)
            if socname not in writers:
                writers.append(socname)
                writer.write(weather)
                await writer.drain()
    except ConnectionResetError:
        writer.close()
        print(f'Socket {socname} closed')


async def client_handler(reader, writer):
    message = await read_message(reader)
    socname = writer.get_extra_info('peername')
    print(f"Socket {socname} connected. Received message: \"{message}\"")

    await handle_client(writer)


async def run_server():
    server = await asyncio.start_server(client_handler, "localhost", 8000)
    async with server:
        try:
            await server.serve_forever()
        # todo (AA): except or finally?
        # todo (AA): Can we replace it with the commented "except KeyboardInterrupt" block presented above?
        except asyncio.CancelledError as e:
            print('Server stopped.')
            for writer in writers:
                # todo (AA): It requires making writers as dict
                # todo (AA): Do we need closing writer?
                writer.close()
            raise e

async def main():
    async with asyncio.TaskGroup() as group:
        group.create_task(prepare_weather_data())
        group.create_task(run_server())


if __name__ == "__main__":
    asyncio.run(main())
