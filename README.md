# sc_ddns - 阿里云域名DDNS客户端

使用阿里云openapi v2.0版本接口，在阿里云控制台添加域名后，直接配置access密钥、子域名、二级域名即可更新域名解析IP。

## python依赖

1. python3，但也要看aliyun_openapi的要求

2. alibabacloud_alidns20150109

3. requests

## 配置详解

1. 使用systemd实现了定时执行任务，时间周期300s，通常个人DNS最快600sTTL，因此300s已经足够，间隔太低意义不大
2. 访问密钥与域名均在/etc/sc_ddns/environment文件配置。注：等号两边不要随意加空格

## 常见问题排除

1. systemd服务未设置运行用户与组，默认一般为root:root权限，因此必须注意pip安装位置，有可能需要单独为root用户安装，即使用sudo pip3安装程序依赖；也可使用python虚拟环境运行，此操作需要修改systemd unit文件。

2. systemd文件安装或更改配置后，必须执行systemctl daemon-reload更新unit，否则会异常

3. 安装python依赖前，最好使用命令pip3 install --upgrade pip更新一下pip
