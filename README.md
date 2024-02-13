# sc_ddns - 阿里云域名DDNS客户端
使用阿里云openapi v2.0版本接口，在阿里云控制台添加域名后，直接配置access密钥、子域名、二级域名即可更新域名解析IP。
公网ip地址获取使用opnsense的api，直接获取opnsense的pppoe0地址，可以自行修改。
此软件主要为了解决opnsense插件不能更新阿里云DNS问题，但仅限于使用路由拨号的场景，即公网IP在opnsense上！！

## python依赖
1. python3，但也要看aliyun_openapi的要求
2. alibabacloud_alidns20150109
3. python3-requests，python3-json

## 配置详解
1. 使用systemd实现了定时执行任务，时间周期60s，通常个人DNS最快600sTTL，因此60s已经足够，间隔太低意义不大
2. 访问密钥与域名均在/etc/sc_ddns/environment文件配置。注：等号两边不要随意加空格
3. 字段含义
	 - access_key_id=''	阿里云access密钥
	 - access_key_secret=''
	 - domain_name=''	二级域名，例：a.com
	 - prefix=''		子域名，例：t1(t1.a.com), t2.t3(t2.t3.a.com)
	 - opnsense_domain=''	opnsense的地址，例：https://192.168.1.1，不要加'/'
	 - opnsense_verify=''	opnsense的证书，https才使用，ca证书路径
	 - opnsense_key=''	opnsense账户访问密钥，添加账户时，下方的访问密钥
	 - opnsense_secret=''
4. 

## 常见问题排除
1. systemd服务未设置运行用户与组，默认为root:root，因此必须注意pip安装位置，有可能需要单独为root用户安装，即使用sudo pip3安装程序依赖；也可使用python虚拟环境运行，此操作需要修改systemd unit文件；还可使用其他账户，但需要注意权限问题。
2. systemd文件安装或更改配置后，必须执行systemctl daemon-reload更新unit，否则会异常
3. 安装python依赖前，最好使用命令pip3 install --upgrade pip更新一下pip

## 联系方式
可站内私信或邮件
