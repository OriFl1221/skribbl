class HTTP:
    HTTP_VERSION = "HTTP/1.1"
    __HEADER_SPLIT = "&&AND&&"


    def __init__(self, *args):
        if len(args) == 1 and isinstance(args[0], str):  # parses HTTP request
            # as string
            self.__headers = {}
            try:
                # put headers in a dict
                splitted = args[0].split('\r\n')
                i = 1
                while len(splitted[i]) != 0:
                    header = splitted[i].split(": ")
                    self.add_header(header[0], header[1])
                    i = i + 1
                # rest is body
                self.__body = "".join(splitted[i:]).encode()
            except Exception:
                raise ValueError('badly formatted: ' + str(args))
            pass
        elif len(args) == 0:
            self.__headers = {}
            self.__body = b''

        pass

    def get_header(self, header):
        return self.__headers[header].split(HTTP.__HEADER_SPLIT)

    def add_header(self, key, value):
        if key not in self.__headers.keys():
            self.__headers[key] = value
        else:
            self.__headers[key] += self.__HEADER_SPLIT + value

    def del_header(self, header):
        del self.__headers[header]

    def set_body(self, body):
        if type(body) == str:
            self.__body = body.encode()
        elif type(body) == bytes:
            self.__body = body
        else:
            raise AttributeError("body must be of type bytes or str")

    def has_header(self, header):
        return header in self.__headers

    def get_body(self):
        return self.__body

    def construct_body(self):
        s = b""
        for key in self.__headers.keys():
            values = str(self.__headers[key]).split(HTTP.__HEADER_SPLIT)
            for value in values:
                s += (key + ": " + str(value) + '\r\n').encode()
        s += b"\r\n" + self.__body
        return s
