
高质量, 高灵活的开放代理池服务
---

# 目标

本项目fork于 `jhao104/proxy_pool`, 致敬!

`jhao104/proxy_pool` 的目标是`通用代理池的框架`.

而我们的目标是构建一个`高质量`, `高灵活`的开放代理池服务.

讲的太抽象了, 简单点来说.

`jhao104/proxy_pool` 是提供给开发人员的定制化使用, 面向的是开发人员!

`1again/proxy_pool`  是提供给一般人员的标准化使用, 面向的是人民群众! 

# 安装/部署

## 生产环境 Docker/docker-compose

```shell
# In WORKDIR proxy_pool

# Install Docker
curl -sSL https://get.docker.com | sh

# Build proxy_pool image
docker build -t proxy_pool .

# Install docker-compose
pip install docker-compose

# Start proxy_pool service
docker-compose -f Docker/docker-compose.yml up -d
```

## 开发环境 Docker

```shell
# In WORKDIR proxy_pool

# Install Docker
curl -sSL https://get.docker.com | sh

# Build proxy_pool image
docker build -t proxy_pool .

# Start proxy_pool container
# I think you are great developer
# So you should how to create a mongodb with Docker or Other, Right?
# !!! Remember modify your database in Config.ini file
docker run -it --rm -v $(pwd):/usr/src/app -p 5010:5010 proxy_pool
```

# 使用

　　启动过几分钟后就能看到抓取到的代理IP, 你可以直接到数据库中查看

　　也可以通过api访问http://server_ip:5010 查看。

## Http Api

| api | method | Description | arg|
| ----| ---- | ---- | ----|
| / | GET | api介绍 | None |
| /get | GET | 随机获取一个代理 | None|
| /get_all | GET | 获取所有代理 |None|
| /get_status | GET | 查看代理数量 |None|
| /delete | GET | 删除代理  |proxy=host:ip|

## 扩展代理

项目默认包含几个免费的代理获取方法，但是免费的毕竟质量不好，所以如果直接运行可能拿到的代理质量不理想。所以，提供了代理获取的扩展方法。

添加一个新的代理获取方法如下:

首先在`ProxyGetter/getFreeProxy.py:32`类中添加你的获取代理的静态方法,

该方法需要以生成器(yield)形式返回`host:ip`格式的代理，例如:

```python

class GetFreeProxy(object):
    # ....

    # 你自己的方法
    @staticmethod
    def freeProxyCustom():  # 命名不和已有重复即可

        # 通过某网站或者某接口或某数据库获取代理 任意你喜欢的姿势都行
        # 假设你拿到了一个代理列表
        proxies = ["139.129.166.68:3128", "139.129.166.61:3128", ...]
        for proxy in proxies:
            yield proxy
        # 确保每个proxy都是 host:ip正确的格式就行
```

添加好方法后，修改Config.ini文件中的`[ProxyGetter]`项：

在`Config.ini`的`[ProxyGetter]`下添加自定义的方法的名字:

```shell

[ProxyGetter]
;register the proxy getter function
freeProxyFirst  = 0  # 如果要取消某个方法，将其删除或赋为0即可
....
freeProxyCustom  = 1  # 确保名字和你添加方法名字一致

```


`ProxyRefreshSchedule`会每隔一段时间抓取一次代理，下次抓取时会自动识别调用你定义的方法。

# 问题反馈

任何问题欢迎在[Issues](https://github.com/1again/proxy_pool/issues)中反馈.

我们的目标是, 没有蛀牙!