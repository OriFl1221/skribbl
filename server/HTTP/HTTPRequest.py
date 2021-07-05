from server.HTTP.HTTP import HTTP


class HTTPRequest(HTTP):
    def __init__(self, *args):
        super().__init__(*args)
        if len(args) == 1 and isinstance(args[0], str):
            # split first line by spaces and assign values accordingly
            try:
                self.method, self.url, _ = args[0].split('\r\n')[0].split(" ")
            except Exception:
                raise ValueError("badly formatted HTTP request/response")
        elif len(args) == 0:
            self.method, self.url = "", ""
        else:
            raise ValueError("bad args")

    def construct_body(self):
        return (self.method + ' ' + self.url + ' ' +
                HTTP.HTTP_VERSION + '\r\n').encode() + super().construct_body()
