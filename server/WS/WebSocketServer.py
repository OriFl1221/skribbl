import asyncio
import json
import random
import string
import websockets


class WebSocket:
    def __init__(self, ip, port):
        self._ip = ip
        self._port = port
        self.rooms = {}

    # starts server
    def listen(self):
        asyncio.get_event_loop().run_until_complete(
            websockets.serve(self.handler, self._ip, self._port))
        asyncio.get_event_loop().run_forever()

    # creates room
    def create_room(self):
        room = Room()

        # add to room map
        self.rooms[room.code] = room
        return room.code

    # handles a msg
    async def handler(self, websocket, path):
        # gets code and sends msg to correct room
        code = path[1:]
        if code in self.rooms.keys():
            await self.rooms[code].handle(websocket, path)


class Room:
    def __init__(self, code_length=4):
        # generates random code
        self.code = ''.join(random.choice(string.ascii_uppercase +
                                          string.digits)
                            for _ in range(code_length))
        self.connected_sockets = set()
        self.chat = []
        self.canvas = []

    # handles a msg
    async def handle(self, websocket, path):
        # Register socket
        self.connected_sockets.add(websocket)
        try:
            async for msg in websocket:
                print(f"new msg {msg}")

                # converts msg to json
                msgJSON = json.loads(msg)

                # new chat msg
                if msgJSON["type"] == "chatMsg":
                    # adds msg to chat history and sends msg to all sockets
                    self.chat.append(msgJSON)
                    for conn in self.connected_sockets:
                        await conn.send(msg)

                # new player joins
                elif msgJSON["type"] == "newJoin":
                    # sends back chat and canvas history
                    await websocket.send(
                        json.dumps(
                            {
                                'type': 'newJoin',
                                'content': {
                                    "chat": self.chat,
                                    "canvas": self.canvas
                                }
                            }))
                # interaction with canvas
                elif msgJSON["type"] == "mousePress" \
                        or msgJSON["type"] == "mouseReleased" \
                        or msgJSON["type"] == "colorChange":

                    # adds change to canvas history and
                    # updates all other sockets
                    self.canvas.append(msgJSON)
                    for conn in self.connected_sockets:
                        if conn != websocket:
                            await conn.send(msg)
        except Exception:
            print("disconnected")
        finally:
            # unregister socket
            self.connected_sockets.remove(websocket)
