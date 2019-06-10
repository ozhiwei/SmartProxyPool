
高质量, 高灵活的开放代理池服务

可能是`全球第一个`带有`智能动态代理`的代理池服务.

这下牛皮吹大了, 不好下来.

[ProxyPool Demo](http://proxy.1again.cc:35050/api/v1/proxy/) (我就是个栗子, 别指望我能有多稳定!)

---

# 功能/特点

我们的目标是`高质量`, `高灵活`.

所有功能都是围绕这两点开发的:

1. 所有代理都有验证计数, 验证成功的次数 / 总计验证的次数 == 代理可用率 (数据库界面)

![Proxy Pool](Docs/images/2.PNG)

2. 获取代理时可以根据是否支持`https`, 透明还是匿名(普匿)`type`, 代理的所在的区域`region`进行过滤, 举栗子

```
# 获取支持https的proxy
http://proxy.1again.cc:35050/api/v1/proxy/?https=1

# 获取匿名的proxy
http://proxy.1again.cc:35050/api/v1/proxy/?type=2

# 获取所在区域为中国的proxy
http://proxy.1again.cc:35050/api/v1/proxy/?region=中国

# 获取所在区域不为中国的proxy
http://proxy.1again.cc:35050/api/v1/proxy/?region=!中国

# 获取支持https, 匿名, 所在区域为中国的rpoxy
http://proxy.1again.cc:35050/api/v1/proxy/?https=1&type=2&region=中国
```

3. 可以通过配置控制`获取新代理的间隔`, `验证代理的间隔`, `保留代理数量`, `自定义的代理验证url`等等...

![Proxy Pool](Docs/images/3.PNG)

4. [WEB页面的管理](http://proxy.1again.cc:35050/admin) 用户名:admin 密码:admin (尔敢乱动, 打洗雷啊!)

![Proxy Pool](Docs/images/1.PNG)

5. 统计获取代理网站的数据

![Proxy Pool](Docs/images/4.PNG)


6. 支持`gevent`并发模式, 效果杠杠的, 别看广告, 看疗效!

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

7. 支持动态代理(手动加粗)

```
root@1again:~# curl -x "proxy.1again.cc:36050" https://httpbin.org/ip
{
  "origin": "183.82.32.56"
}
root@1again:~# curl -x "proxy.1again.cc:36050" https://httpbin.org/ip
{
  "origin": "200.149.19.170"
}
root@1again:~# curl -x "proxy.1again.cc:36050" https://httpbin.org/ip
{
  "origin": "125.21.43.82"
}
root@1again:~# curl -x "proxy.1again.cc:36050" https://httpbin.org/ip
{
  "origin": "110.52.235.124"
}
root@1again:~# curl -x "proxy.1again.cc:36050" https://httpbin.org/ip
{
  "origin": "176.74.134.6"
}
```

8. 实在编不下去了, 你行你来!

# 文档

[设计文档](docs/Design.md)

# 目前

基本上满足了当初的设想, 准备开始写文档和代码优化.

# 使用场景

1. 主要还是用于爬虫.

2. 公司需要有个内部代理池服务, 用来干一些丧尽天良的坏事.

3. 个人需要用来干一些见不得人的事.

# 安装/部署

## 生产环境

```shell
# Install Docker
curl -sSL https://get.docker.com | sh

# start mongo database
docker run -d --name mongo -v /data/mongodb:/data -p 27017:27017 mongo

# Start proxy_pool container
docker run -d --name proxy_pool --link mongo:proxy_pool_db -p 35050:35050 1again/proxy_pool
```

## 开发环境

```shell
# Clone Repo
git clone https://github.com/1again/ProxyPool

# Entry Dir
cd ProxyPool

# Install Docker
curl -sSL https://get.docker.com | sh

# start mongo database
docker run -d --name mongo -v /data/mongodb:/data -p 27017:27017 mongo

# Start proxy_pool container
docker run -it --rm --link mongo:proxy_pool_db -v $(pwd):/usr/src/app -p 35050:35050 1again/proxy_pool
```

# 使用

启动过几分钟后就能看到抓取到的代理IP, 你可以直接在WEB管理界面中中查看

## DYNAMIC PROXY

```shell
curl -x 'your_server_ip:36050' your_access_url

like this:
curl -x "proxy.1again.cc:36050" https://httpbin.org/ip
```

## RESTFUL API

```python

API_LIST = {
    "/api/v1/proxy/": {
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
}

```

## 扩展代理

项目默认包含几个免费的代理获取方法

如果遇到好的免费代理渠道, 可以自行添加其他代理获取的方法.

添加一个新的代理获取方法如下:

首先在`Src/Fetcher/fetchers/`目录中添加你的代理类.

该类需要有一个`run`方法, 以生成器(yield)形式返回`host:ip`格式的代理，例如:

```python

# 文件名和class名要保持一致
class Fetcher1():
    # 用来识别的, 会映射到数据库里面
    fetcher_name = "Fetcher1"

    def run(self):
        url_list = [
            'http://www.xxx.com/',
        ]
        for url in url_list:
            html_tree = getHtmlTree(url)
            ul_list = html_tree.xpath('//ul[@class="l2"]')
            for ul in ul_list:
                try:
                    yield ':'.join(ul.xpath('.//li/text()')[0:2])
                except Exception as e:
                    print(e)
```

`ProxyFetchSchedule` 会每隔一段时间抓取一次代理，下次抓取时会自动识别调用你定义的方法。

# Contributing

感谢你的支持, 让我们变得更好!

为了规范和清晰, 我们需要一起做些简单约定.

两个主要的分支
develop  为下个版本的内容
master   为当前稳定版本的内容

1. 小修小改, 不影响原版本的修改, 可以在develop上进行, 然后pull requests
2. 大动干戈, 影响之前版本的修改, 需要新建一个分支eg: feature_random_proxy, 然后进行pull requests.

我会将新分支合并到develop上, 并在演示的机器上运行一段时间后合并至master.

以上, 感谢!

# 问题反馈

任何问题欢迎在[Issues](https://github.com/1again/ProxyPool/issues)中反馈.

我们的目标是, 没有蛀牙!
