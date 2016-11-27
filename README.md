# 简介
由于桂电实验室上网需要 **高额的** 费用，考虑到实验室和宿舍的网络都是基于校园网来进行内网连接的，基于这一点，考虑在宿舍通过笔记本或树莓派设备来启动一个vpn服务器连接内网，然后再宿舍的设备上将内外网进行桥接，即该设备可以同时上内外网，由于大多数笔记本或者树莓派都具有双网卡，所以采用无线网卡来接入一个已经具备上网功能的路由器，使用有线网卡连接内网。

## 配置 _永不掉线_ 的路由器
桂电宿舍的网线都是单网线三网通用的，其实原理很简单，就是在上层做了一下网关开放的工作，通过一个叫做出校器的工具，选择一个运营商，将拨号所用的mac地址和相关的运营商进行绑定，此后的所有的数据包都发往指定运营商的网关，基于这个原理，可以在实验室等能够连通内网的设备上定期进行相关端口开放的工作(前提是讲该设备的mac修改为路由器的mac地址)，另外，这里推荐一个师大师兄编写的mac、linux、windows下的第三方出校器和端口开放工具[ipclient_gxnu][890a6ed5],项目中的有详细的介绍和文档，推荐学习。此外，如果仅仅是需要进行运营商和mac地址的绑定的话，推荐使用桂电某学生编写的在线端口绑定网站:[http://sec.guet.edu.cn/open/][72f609bc]将路由mac地址和某运营商端口进行绑定

## ubuntu发行版本选择
由于之前我用的是ubuntu的最新的发行版本，在dhcp的时候经常会出现三个默认路由的情况，我也没有深入研究原因，后来换到16.02LTS上后，同样的配置，dhcp后默认只有一个默认路由，所以推荐16.02LTS

## 配置
安装pptpd
```bash
sudo apt-get install pptpd
```
配置虚拟ip，编辑/etc/pptpd.conf:
```
localip 10.20.39.111 # 本机ip
remoteip 10.100.123.2-100 # 分配的ip段
```
在/etc/ppp/pptpd-options下中设置dns:
```
#根据实际情况设置dns
ms-dns 192.168.199.1
ms-dns 114.114.114.114
```
在/etc/ppp/chap-secrets中配置vpn账号:
```
"user"  pptpd   "user"  * #星号是不限制ip的意思
```
不过默认情况下，pptpd无法给vpn连接分配ip，所以如果是多用户的话需要手动分配ip具体配置类似:
```
"user1"   pptpd   "user1"   10.100.123.2
"user2"   pptpd   "user2"   10.100.123.3
```
重启pptpd服务:
```
sudo /etc/init.d/pptpd restart
```
在/etc/sysctl.conf中配置ip转发(取消该行注释):
```
net.ipv4.ip_forward=1
```
使配置立即生效:
```
sudo sysctl -p
```
安装iptables,这个是用于配置NAT映射的:
```
sudo apt-get install iptables
```
建立一个NAT:
```
sudo iptables -t nat -A POSTROUTING -s 10.100.123.0/24 -o wlo1 -j MASQUERADE
```
其中-o参数配置的是流量的出口,也就是我这的外网出口
设置MTU,防止包过大而丢包:
```
sudo iptables -A FORWARD -s 10.100.123.0/24 -p tcp -m tcp --tcp-flags SYN,RST SYN -j TCPMSS --set-mss 1200
```
保存规则(此处需要root权限):
```
sudo iptables-save >/etc/iptables-rules
```
编辑/etc/network/interfaces,在末尾加一行,使网卡加载时自动加载规则:
```
per-up iptables-restore </etc/iptables-rules
```
配置到此为止

## 网卡名称修改问题
新版的ubuntu网卡名称都是随机的，可以自定义修改网卡的名称，比如本文章中，有线网卡为:wlo1， 无线网卡为:eno1。
默认，/etc/udev/rules.d/只有一个README文件。
新建了70-persistent-net.rules文件，然后编辑：
```
SUBSYSTEM=="net", ACTION=="add", ATTR{address}=="44:33:4c:07:ad:48", NAME="eno1"

```

## 服务器启动代码
主要用于
1. 修改dhcp后的ip为静态ip
2. 添加内外网路由，默认情况下重启后路由表会丢失
3. 持续ping对方网关，保证服务器的稳定


  [911b7533]: https://github.com/leftjs/vpn_launch "leftjs/vpn_launch"
  [890a6ed5]: https://github.com/xuzhipengnt/ipclient_gxnu "ipclient_gxnu"
  [72f609bc]: http://sec.guet.edu.cn/open/ "http://sec.guet.edu.cn/open/"
