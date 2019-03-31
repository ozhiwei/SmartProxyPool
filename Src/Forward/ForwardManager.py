import sys
sys.path.append("Src")

from Forward.base import HTTP, Proxy

from Manager import ProxyManager
from Config import ConfigManager

class ForwardProxy(Proxy):

    def _get_host_and_port(self):
        https = None
        if self.request.method == b'CONNECT':
            https = ProxyManager.PROXY_HTTPS["ENABLE"]

        domain = self.request.url.netloc
        if isinstance(domain, bytes):
            domain = domain.decode("utf8")

        ProxyManager.proxy_manager.tickDomainRequestState(domain, "total")
        counter = ProxyManager.proxy_manager.getDomainCounter(domain)
        count = counter.get("total")
        item = ProxyManager.proxy_manager.getQualityUsefulProxy(https=https, count=count, domain=domain)
        proxy = item.get("proxy")
        address = proxy.split(":")
        return address

    def before_process_response(self):
        domain = self.request.url.netloc
        if isinstance(domain, bytes):
            domain = domain.decode("utf8")

        if isinstance(self.response.code, bytes):
            status_code = "status_code_%s" % self.response.code.decode()
        else:
            status_code = "status_code_%s" % self.response.code

        ProxyManager.proxy_manager.tickDomainRequestState(domain, status_code)

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