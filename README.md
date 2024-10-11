# Simple server and client communicating via sockets in Python
**NOT FINISHED YET**

This is an example of a server and client communicating via sockets in Python. Server generates some messages and 
pushes it immediately to all connected clients. Both server and client require standard libraries only. Both 
server and client were tested on `Python 3.12`.

Run server:

    python asyncio_socket_server_v1.py

Run client:

    python socket_client.py


`asyncio_socket_server_v0` doesn't handle properly server interruption

`asyncio_socket_server_v1` is a completely working solution, but may be improved. I'd like to:
- avoid the coroutines switch by `await asyncio.sleep(0)`
- avoid global variables usage as much as possible
- avoid explicitly canceling the task with `t.cancel()`; add the exception-raising task as it is recommended in 
the [documentation](https://docs.python.org/3/library/asyncio-task.html#terminating-a-task-group)
- eliminate the ~2-second delay in notifying client disconnections on the server side; i.e. the delay in printing 
`f'Socket {socname} closed'`

`asyncio_socket_server_[under_construction].py` is the under construction version of server.
