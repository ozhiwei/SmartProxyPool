
高质量, 高灵活的开放代理池服务 [ProxyPool Demo](http://proxy.1again.cc:5010/api/v1/proxy/)
---

# 目标

本项目fork于 `jhao104/proxy_pool`, 致敬!

`jhao104/proxy_pool` 的目标是`通用代理池的框架`, 会做很多兼容性的开发.

而我们的目标是构建一个`高质量`, `高灵活`的开放代理池服务, 会做很多体验上的开发.

讲的太抽象了, 简单点来说.

`jhao104/proxy_pool` 是提供给开发人员的定制化使用, 面向的是开发人员!

`1again/ProxyPool`  是提供给一般人员的标准化使用, 面向的是人民群众! 

`ProxyPool` 另外我觉得首字母大写会庄重严肃很多!

# 功能/特点

我们的目标是`高质量`, `高灵活`.

所有功能都是围绕这两点开发的:

1. 所有代理都有验证计数, 验证成功的次数 / 总计验证的次数 == 代理可用率

2. ~~通过token参数, 可以获取到`不重复`, `高可用率`的代理~~

3. 获取代理时可以根据是否支持`https`, 透明还是匿名(普匿)`type`, 代理的所在的区域`region`进行过滤

4. 可以通过配置文件(`Config.ini`)控制`获取新代理的间隔`, `验证代理的间隔`, `清除代理的间隔`

5. 可以通过配置文件(`Config.ini`)控制`自定义的代理验证url`

6. 在清理代理时会根据`代理可用率`进行排序, 清理低可用率的代理, 这个数量可以在配置文件(`Config.ini`)中设置

7. [WEB页面的管理](http://proxy.1again.cc:5010/admin) 用户名:admin 密码:admin

8. 支持`gevent`并发模式, 效果杠杠的, 别看广告, 看疗效!

9. 实在编不下去了, 你行你来!


# 疗效

```
2019-01-23 16:14:38,805 ProxyClean.py[line:42] INFO clean raw_proxy, total_number:1196, clean_number:1195, remain_number:1
2019-01-23 16:14:38,809 ProxyClean.py[line:33] INFO clean useful, total_number:2539, clean_number:0, hold_number:-1
2019-01-23 16:14:49,137 ProxyFetch.py[line:84] INFO fetch [freeProxyFifth] proxy finish, total:20, succ:20, fail:0, skip:0, elapsed_time:6s
2019-01-23 16:14:50,261 ProxyFetch.py[line:84] INFO fetch [freeProxyFirst] proxy finish, total:50, succ:50, fail:0, skip:0, elapsed_time:7s
2019-01-23 16:14:54,119 ProxyFetch.py[line:84] INFO fetch [freeProxyTwelve] proxy finish, total:32, succ:23, fail:0, skip:9, elapsed_time:10s
2019-01-23 16:14:57,033 ProxyFetch.py[line:84] INFO fetch [freeProxyTen] proxy finish, total:60, succ:55, fail:0, skip:5, elapsed_time:13s
2019-01-23 16:14:57,977 ProxyFetch.py[line:84] INFO fetch [freeProxyEleven] proxy finish, total:65, succ:51, fail:0, skip:14, elapsed_time:14s
2019-01-23 16:14:58,548 ProxyFetch.py[line:84] INFO fetch [freeProxySeventh] proxy finish, total:75, succ:55, fail:0, skip:20, elapsed_time:15s
2019-01-23 16:15:00,064 ProxyFetch.py[line:84] INFO fetch [freeProxyFourth] proxy finish, total:400, succ:307, fail:0, skip:93, elapsed_time:16s
2019-01-23 16:15:04,796 ProxyVerify.py[line:242] INFO raw_proxy verify  proxy finish, total:1196, succ:3, fail:1193, skip:0, elapsed_time:26s
2019-01-23 16:15:14,441 ProxyVerify.py[line:310] INFO useful_proxy verify proxy finish, total:2539, succ:550, fail:1989, elapsed_time:35s
```

# 目前

目前还在重构阶段, 所以不保证安全稳定哦!

先体验一下 [ProxyPool Demo](http://proxy.1again.cc:5010/api/v1/proxy/)

然后Star一下, 养肥了再杀!

目前不支持windows, 大概率以后也不会支持!

# 使用场景

1. 主要还是用于爬虫.

2. 公司需要有个内部代理池服务, 用来干一些丧尽天良的坏事.

3. 个人需要用来干一些见不得人的事.

# 安装/部署

## 生产环境 Docker/docker-compose

```shell
# In WORKDIR ProxyPool
# Install Docker
curl -sSL https://get.docker.com | sh

# Install docker-compose
pip install docker-compose

# Start proxy_pool service
docker-compose -f Docker/docker-compose.yml up -d
```

## 开发环境 Docker

```shell
# In WORKDIR ProxyPool
# Install Docker
curl -sSL https://get.docker.com | sh

# Start proxy_pool container
# I think you are great developer
# So you should how to create a mongodb with Docker or Other, Right?
# 记得先创建一个mongodb数据库
# !!! Remember modify your database in Config.ini file
# !!! 记住修改你的数据库配置文件 Config.ini
docker run -it --rm -v $(pwd):/usr/src/app -p 5010:5010 1again/proxy_pool
```

# 使用

启动过几分钟后就能看到抓取到的代理IP, 你可以直接到数据库中查看

也可以通过api访问http://server_ip:5010 查看。

## RESTFUL API

```python

API_LIST = {
    "/api/v1/proxy/": {
        "args": {
            "token": {
                "value": "random string + random number",
                "desc": "Avoid Get Repetition Proxy",
                "required": False,
            },
            "https": {
                "value": [1],
                "desc": "need https proxy? 1 == true",
                "required": False,
            },
            "region": {
                "value": "region name like 中国 or 广州 or 江苏",
                "desc": "Get Region Proxy",
                "required": False,
            },
            "type": {
                "value": [1,2],
                "desc": "clear proxy 1 or (common) anonymous 2",
                "required": False,
            }
        },
        "desc": "Get A Random Proxy"
    },
    "/api/v1/proxies/": {
        "args": {
            "https": {
                "value": [1],
                "desc": "need https proxy? 1 == true",
                "required": False,
            },
            "region": {
                "value": "region name like 中国 or 广州 or 江苏",
                "desc": "Get Region Proxy",
                "required": False,
            },
            "type": {
                "value": [1,2],
                "desc": "clear proxy 1 or (common) anonymous 2",
                "required": False,
            }
        },
        "desc": "Get All Proxy",
    },
    "/api/v1/proxies/stat/": {
        "args": {},
        "desc": "Statistics All Vaild Proxies",
    }
}

```

## 扩展代理

项目默认包含几个免费的代理获取方法

如果遇到好的免费代理渠道, 可以自行添加其他代理获取的方法.

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

`ProxyFetchSchedule` 会每隔一段时间抓取一次代理，下次抓取时会自动识别调用你定义的方法。

# 问题反馈

任何问题欢迎在[Issues](https://github.com/1again/ProxyPool/issues)中反馈.

我们的目标是, 没有蛀牙!