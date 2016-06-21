---
title: moinmoin 在 ubuntu 16.04 server 版本中安装
date: 2016-06-21 20:07:14
categories: 日常技术
tags:
- python
- nginx
- moinmoin
- uwsgi
---



## moinmoin 在ubuntu 16.04 的安装
moinmoin是python写的一个wiki引擎. 应用广泛，支持多种扩展, 可二次开发。


python版本: python2.7 (monmoin目前是不支持python3)

### 安装python开发包与pip:
   $sudo apt-get install python-dev python-pip

### 安装uwsgi:
   $sudo pip  install uwsgi

### 安装moinmoin
``` bash
$sudo wget http://static.moinmo.in/files/moin-1.9.8.tar.gz
$sudo tar -xzvf moin-1.9.8.tar.gz
$sudo cd moin-1.9.8
$sudo python setup.py install --prefix=/usr/local
```
  安装完之后， 
  moinmoin代码包位于 /usr/local/lib/python2.7/dist-packages/
  moinmoin数据以及配置包位于 /usr/local/share/moin

### 配置moinmoin
``` bash
   $sudo cd /usr/local/share/moin
   $sudo cp server/moin.wsgi .    #copy server目录下的sample配置到当前目录
   $sudo vi moin.wsgi
```
       # 添加以下两行。主要配置Moinmoin的代码与配置安装路径
``` bash
      sys.path.insert(0, '/usr/local/lib/python2.7/dist-packages/')
      sys.path.insert(0, '/usr/local/share/moin/')
```

### 创建uwsgi.ini 配置文件
``` bash
    $sudo vi uwsgi.ini
    [uwsgi]
    uid = www-data      #配置运行Moinmoin的用户. www-data则是在安装完Moinmoin时创建的
    gid = www-data
    socket = /usr/local/share/moin/moin.sock    # 通过socket与nginx通信
    chmod-socket = 660
    logto = /var/log/uwsgi/uwsgi.log

   chdir = /usr/local/share/moin/
   wsgi-file = moin.wsgi           # uwsgi使用的wsgi文件. 

   [master]
   workers = 3
   max-requests = 200
   harakiri = 30
   die-on-term
```
### 创建uwsgi log文件夹
``` bash
   $sudo mkdir -p /var/log/uwsgi
   $sudo chown www-data /var/log/uwsgi
```

### 创建初始脚本用于启动moinmoin. 
    该脚本主要用于在server重启之后能够使用uwsgi来启动Moinmoin
``` bash
   $sudo vi /etc/init/moin.conf
   description "moin uwsgi service"

   start on runlevel [2345]
   stop on runlevel [!2345]

   chdir /usr/local/share/moin        # moinmoin安装位置
   exec /usr/local/bin/uwsgi /usr/local/share/moin/uwsgi.ini     #uwsig与uwsgi.ini脚本位置
   respawn
```
### 配置wiki
``` bash
   $sudo cd /usr/local/share/moin
   $sudo cp config/wikiconfig.py .
   $sudo vi wikiconfig.py
   sitename = u'Wiki标题名字'
   page_front_page = u"FrontPage"    # 出现头版
   superuser = [u"WikiAdmin", ]         # 配置管理员
```
### 改变moin目录的Owner权限
``` bash
   $sudo chown -R www-data: /usr/local/share/moin
   $sudo chmod -R o-rwx /usr/local/share/moin
```

### 启动moin
``` bash
   $sudo start moin
```
 到目前为止，moinmoin已配置完成并已经启动了。接下来搭配nginx来使用wiki

### 安装nginx
``` bash
   $sudo apt-get install nginx
```
### 配置nginx
``` bash
   $sudo cd /etc/nginx/sites-available
   $sudo vi moin
   server {
    listen 80;
    server_name localhost;

    access_log /var/log/nginx/access.log;
    error_log /var/log/nginx/error.log;

    location / {
        include uwsgi_params;
        uwsgi_pass unix:///usr/local/share/moin/moin.sock;    #转到uwsgi的socket
        uwsgi_modifier1 30;
    }
  }

   $sudo cd /etc/nginx/sites-enabled
   $sudo ln -s ../sites-available/moin .
   $sudo rm default
```
### 启动nginx
``` bash
   $sudo service nginx restart
```
### 访问moinmoin
      在浏览器输入服务器的地址就可以对moinmoin进行访问了

## 将moinmoin配置到服务器的子路径

以上基于服务器根路径的moinmoin就已经搭建好了，但是真正用的时候，还是不会把他放到根路径，所以下面就介绍部署到子路径的方法.


### 如果将moinmoin的路径配置在/wiki的路径，需要修改/etc/nginx/sites-available/moin 文件中
``` python
location ^~ /wiki {
        include uwsgi_params;
        uwsgi_pass unix:///usr/local/share/moin/moin.sock;    #转到uwsgi的socket
        uwsgi_param UWSGI_PYHOME /data/web/moinmoin/python-env/;
        uwsgi_param UWSGI_CHDIR /data/web/moinmoin/wiki/;
        uwsgi_param UWSGI_SCRIPT moin_wsgi;
        uwsgi_param SCRIPT_NAME /wiki;
        uwsgi_modifier1 30;
}

location ^~ /wiki/moin_static/ {      #moin_static wiki网页资源的位置,
        alias /data/web/moinmoin/python-env/lib/python2.7/site-packages/MoinMoin/web/static/htdocs/;
        add_header Cache-Control public;
        expires 20M;                  #将上传附件的大小限制到20M，如果不配置，默认上传大小是512K,很小的
}

```
### 还要需要wikiconfig.py，这个文件中的url_prefix_static是他的服务器路径前缀，需要在这里进行加入子路径的字符串。
``` bash
$vi /usr/local/share/moin/wikiconfig.py
url_prefix_static = '/wiki' + url_prefix_static
```

### 启动服务
``` bash
   $sudo start moin
   $sudo service nginx restart
```
访问服务器主机的子路径就可以访问到moinmoin了

# p.s.最后发现moinmoin还是用的不爽，最后还是改成sphinx了。。。。这个文章就当做纪念吧