from server.HTTP.HTTP import HTTP


class HTTPResponse(HTTP):
    def __init__(self, *args):
        super().__init__(*args)
        if len(args) == 1 and isinstance(args[0], str):
            # split first line by spaces and assign values accordingly
            try:
                _, self.code, self.phrase = args[0].split('\r\n')[0].split(" ")
            except Exception:
                raise ValueError("badly formatted HTTP request/response")
        elif len(args) == 0:
            self.code, self.phrase = 0, ""
        else:
            raise ValueError("bad args")

    def construct_body(self):
        return (HTTP.HTTP_VERSION + ' ' + str(self.code) + ' ' + self.phrase +
                '\r\n').encode() + super().construct_body()
