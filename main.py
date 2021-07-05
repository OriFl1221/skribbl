import json
import pathlib
import socket
from server.HTTP.HTTPResponse import HTTPResponse
from server.HTTP.HTTPServer import HTTPServer
from server.WS.WebSocketServer import WebSocket

SERVER_HOST, SERVER_PORT = '0.0.0.0', 80
WS_IP, WS_PORT = '0.0.0.0', 443
ws = WebSocket(WS_IP, WS_PORT)


class RouteHandler:
    @staticmethod
    def home_route(req):
        res = HTTPResponse()
        res.code = 303
        res.phrase = "See Other"
        res.add_header("Location", "/index.html")
        return res
        pass

    @staticmethod
    def cookie(req):
        res = HTTPResponse()
        res.code = 200
        res.phrase = "OK"
        res.add_header('Set-Cookie', 'us=2')
        res.add_header('Set-Cookie', 'u1=2sdf')
        return res
        pass

    @staticmethod
    def join_room(req):
        # redirect user to room
        res = HTTPResponse()
        res.code = 303
        res.phrase = "See Other"
        res.add_header("Location", f"/room/index.html?room={req['url_params']['id'][0]}&name={req['url_params']['name'][0]}")
        return res
        pass

    @staticmethod
    def create_room(req):
        # create room and redirect user to it
        res = HTTPResponse()
        res.code = 303
        res.phrase = "See Other"
        res.add_header("Location", f"/room/index.html?room={ws.create_room()}&name={req['url_params']['name'][0]}")
        return res
        pass

    @staticmethod
    def web_socket_location(req):
        res = HTTPResponse()
        res.code = 200
        res.phrase = "OK"
        res.add_header("Content-Type", "application/json")

        # create json object
        obj = {"ip": socket.gethostbyname(socket.gethostname()), "port": WS_PORT}
        res.set_body(json.dumps(obj))
        return res



def main():
    # create server object
    server = HTTPServer(('0.0.0.0', 8080))

    # setup routes
    server.add_route('GET', '/', RouteHandler.home_route)
    server.add_route('GET', '/join', RouteHandler.join_room)
    server.add_route('GET', '/create', RouteHandler.create_room)
    server.add_route('GET', '/wsLocation', RouteHandler.web_socket_location)
    server.add_route('GET', '/cookie', RouteHandler.cookie)

    server.add_dir_to_route('/', str(pathlib.Path(__file__).parent
                                     .absolute()) + '\\client')

    # add middleware
    server.add_middleware(HTTPServer.form_data)
    server.add_middleware(HTTPServer.url_params)

    # start servers
    server.listen()
    ws.listen()

    pass


if __name__ == '__main__':
    main()

