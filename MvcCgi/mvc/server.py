from http.server import CGIHTTPRequestHandler, HTTPServer
import argparse

class MvcCgiHandler(CGIHTTPRequestHandler):

    def is_cgi(self):

        original = self.path
        self.path=self.controller_path
        params_idx = original.find("?")
        if params_idx > -1:
            self.path += original[params_idx:]+"&_orig_url="+original[:params_idx]
        else:
            self.path +="?_orig_url="+original

        print(self.path)
        return super().is_cgi()



def main(path="controller.py",ip='127.0.0.1',port=8080):
    print('starting server...')
    # Server settings
    # Choose port 8080, for port 80, which is normally used for a http server, you need root access
    server_address = (ip, port)
    handler = MvcCgiHandler
    handler.cgi_directories=['/']
    handler.controller_path = path
    # I can configure the directories I want to use here
    httpd = HTTPServer(server_address, handler)
    print('running server...')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()


if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', default=8080, type=int,
                    help='Specify the port')
    parser.add_argument('--ip', '-b', default='127.0.0.1', type=str,
                    help='Specify ip address ')
    parser.add_argument('path', action='store',
                    default="controller.py", type=str,
                    help='Specify the default cgi script')

    args = parser.parse_args()

    main(port=args.port,ip=args.ip,path=args.path)