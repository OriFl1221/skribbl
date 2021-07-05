import traceback
import glob
import json
import os
import pathlib
import socket
import threading
from urllib.parse import parse_qs

from server.HTTP.HTTPRequest import HTTPRequest
from server.HTTP.HTTPResponse import HTTPResponse


class HTTPServer:
    def __init__(self, location):
        if type(location) is tuple:
            self.__location = location
            self.__middlewareQueue = []
            self.__routes = {}
            self.route404 = None

            # read MIMEFormats file and load to memory
            MIME_formats_file = \
                open(str(pathlib.Path(__file__).parent.absolute()) +
                     '\\MIMEFormats.json', 'r')
            self.MIMEFormats = json.loads(MIME_formats_file.read())
            MIME_formats_file.close()
        else:
            raise TypeError()
        pass

    # start server
    def listen(self):
        # start server on new thread
        threading.Thread(target=self.__listen_thread_function).start()
        pass

    def __listen_thread_function(self):
        # setup socket
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(self.__location)
        server_socket.listen(1)
        print('Listening on port %s ...' % self.__location[1])

        while True:
            # Wait for client connections
            client_connection, client_address = server_socket.accept()

            # Get the client request
            request = client_connection.recv(1024).decode()
            print("================\nnew request")
            try:
                # process request
                request = {"raw": HTTPRequest(request)}
                print(request["raw"].method + ' ' + request["raw"].url)

                # send to middleware
                self.__pass_to_middleware(request)

                # pass to correct route function
                res = self.__route_req(request)

                # do final process of response
                self.__format_res(res=res, req=request)

                # send response
                res = res.construct_body()
                client_connection.sendall(res)
            except Exception:
                err = traceback.format_exc()
                print(err)
                client_connection.sendall(self.__default_server_error(request, err)
                                          .construct_body())
            client_connection.close()

        # Close socket
        server_socket.close()
        pass

    # middleware are functions that allow the
    # user to parse the response data similar to node.js express middleware
    def __pass_to_middleware(self, req):
        # pass request to every middleware function
        for middleware in self.__middlewareQueue:
            middleware(req)
        pass

    # adds route to server
    def add_route(self, method, path, response):
        self.__routes[method + " " + path] = response
        pass

    # passes request through the route map
    def __route_req(self, req):
        # build string of request method + url (without url params)
        key = req["raw"].method + " " + req["raw"].url.split('?')[0]
        if key in self.__routes.keys():
            # if value of key in the routes map is string or byte
            # return response with the value in the body
            if isinstance(self.__routes[key], bytes) or \
                    isinstance(self.__routes[key], str):
                res = HTTPResponse()
                res.code = 200
                res.phrase = 'ok'
                res.set_body(self.__routes[key])
                return res
            # if it isnt string nor bytes then in must be a function.
            else:
                return self.__routes[key](req)
        # if key isnt found send 404
        elif self.route404 is None:
            return self.__default_route(req)
        else:
            return self.route404(req)

    # routes entire dir at selected route (useful for static content)
    def add_dir_to_route(self, route, directory):
        # gets directories of all files inside provided dir
        paths_of_files = self.__get_all_files(directory)

        # formats the provided dir so all \\ become / and all \ become /
        directory = directory.replace('\\\\', '/').replace('\\', '/')
        for path_of_file in paths_of_files:
            # read data of file
            f = open(path_of_file, 'rb')
            data = f.read()
            f.close()

            # formats the provided dir so all \\ become / and all \ become /
            path_of_file = path_of_file.replace('\\\\', '/') \
                .replace('\\', '/').replace(directory, '')

            # make sure there is no / in beginning
            if path_of_file[0] == '/':
                path_of_file = path_of_file[1:]

            # adds file to route map
            self.add_route('GET', route + path_of_file, data)

    # wrapper funcion of __get_all_files_rec
    def __get_all_files(self, starting_dir):
        return self.__get_all_files_rec(starting_dir, [])

    # gets dir all files inside a directory
    def __get_all_files_rec(self, starting_dir, all_dirs):
        # for every file or folder inside directory (not deep)
        for filename in glob.iglob(starting_dir + '**\**'):
            # if folder add its content to
            if os.path.isdir(filename):
                all_dirs = all_dirs + self.__get_all_files_rec(filename, [])
            # if file add its dir to list of dirs
            else:
                all_dirs.append(filename)
        return all_dirs

    # adds Content-Type and Content-Length headers to response
    # if possible and if Content-Type doesnt exist already
    def __format_res(self, res, req):
        # check header doesnt exist and that a file extension exist in url
        if not (res.has_header('Content-Type')) and '.' in req["raw"].url:
            # get file extension
            file_format = req["raw"].url.split(".")[-1]

            # check if a MIMEFormat is available for this extension
            if file_format in self.MIMEFormats.keys():
                res.add_header('Content-Type', self.MIMEFormats[file_format])

        # add Content-Length header to res
        res.add_header('Content-Length', len(res.get_body()))

    # adds a function to the middleware list
    def add_middleware(self, middleware):
        self.__middlewareQueue.append(middleware)

    # default 404 route
    @staticmethod
    def __default_route(req):
        res = HTTPResponse()
        res.code = 404
        res.phrase = "not found"
        res.add_header('Content-Type', 'text/html')
        res.set_body("<h1>404 not found</h1> unknown url: " + req["raw"].url)
        return res

    # default 500 route
    @staticmethod
    def __default_server_error(req, err):
        res = HTTPResponse()
        res.code = 500
        res.phrase = "Internal Server Error"
        res.add_header('Content-Type', 'text/html')
        res.set_body(f"<h1>server error:</h1> <p>{err}</p>")
        return res

    # url params middleware
    @staticmethod
    def url_params(req):
        # splits request URL by ? takes URL params, URL decodes
        # and translates to dict
        url_params = req["raw"].url.split('?')[-1]
        req['url_params'] = parse_qs(url_params)

    # form data middleware
    @staticmethod
    def form_data(req):
        try:
            # check if request contains form data
            if req['raw'].get_header('Content-Type')[0] == \
                    'application/x-www-form-urlencoded':
                req['form_data'] = parse_qs(req['raw'].get_body().decode())
        except KeyError:
            # if Content-Type header doesnt exist
            pass
