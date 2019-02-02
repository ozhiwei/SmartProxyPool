import sys
sys.path.append("Src")

from Forward.base import HTTP, Proxy

from Manager import ProxyManager
from Config import ConfigManager

class ForwardProxy(Proxy):

    def get_address(self, request):
        if request.method == b'CONNECT':
            https=True
        else:
            https=False

        item = ProxyManager.proxy_manager.getSampleUsefulProxy(https=https)
        proxy = item.get("proxy")
        address = proxy.split(":")
        return address

class ForwardHttp(HTTP):

    def __init__(self):
        bind_host = ConfigManager.base_config.setting.get("forward_bind_host")
        bind_port = ConfigManager.base_config.setting.get("forward_bind_port")

        super(ForwardHttp, self).__init__(hostname=bind_host, port=bind_port)

    def handle(self, client):

        fp = ForwardProxy(client,
            auth_code=self.auth_code,
            server_recvbuf_size=self.server_recvbuf_size,
            client_recvbuf_size=self.client_recvbuf_size,
        )
 
        fp.daemon = True
        fp.start()
 

if __name__ == '__main__':
    fh = ForwardHttp()
    fh.run()