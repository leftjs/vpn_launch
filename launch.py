#!/usr/bin/python
# -*- coding: UTF-8 -*-
import socket, fcntl, struct
import commands
import time
import smtplib
from email.mime.text import MIMEText
from email.header import Header

# 第三方 SMTP 服务
mail_host="smtp.qq.com"  #设置服务器
mail_user="leftjs@foxmail.com"    #用户名
mail_pass="xxxx"   #授权口令
sender = 'leftjs@foxmail.com'
receivers = ['lefttjs@gmail.com']  # 接收邮件，可设置为你的QQ邮箱或者其他邮箱



def send_email(text):
    message = MIMEText('%s' % text, 'plain', 'utf-8')
    message['From'] = Header("leftjs", 'utf-8')
    message['To'] =  Header("jason zhang", 'utf-8')
    subject = 'vpn 报告'
    message['Subject'] = Header(subject, 'utf-8')
    try:
        smtpObj = smtplib.SMTP_SSL()
        smtpObj.connect(mail_host, 465)    # 25 为 SMTP 端口号
        smtpObj.login(mail_user,mail_pass)
        smtpObj.sendmail(sender, receivers, message.as_string())
        print "邮件发送成功"
    except smtplib.SMTPException:
        print "Error: 无法发送邮件"

def get_local_ip(ifname):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        inet = fcntl.ioctl(s.fileno(), 0x8915, struct.pack('256s', ifname[:15]))
        return socket.inet_ntoa(inet[20:24])
    except Exception, e:
        send_email(str(e))
        return

def check_ping():
    (ping_state, res) = commands.getstatusoutput('ping 202.193.75.254 -c 2')
    # (ping_state_baidu, res_baidu) = commands.getstatusoutput('ping www.baidu.com -c 2')
    # ping_state == 0 when ping is ok
    # return True if ping_state == 0 and ping_state_baidu == 0 else False
    return True if ping_state == 0 else False

def read_file_content(file_name):
    the_file = open(file_name, 'r')
    file_content = the_file.read()
    the_file.close()
    return file_content

def write_file_content(file_name, new_content):
    out_file = open(file_name, 'w')
    out_file.write(new_content)
    out_file.close()

def create_interfaces_static_file(intranet_ip):
    raw_content = read_file_content('./interfaces/raw_interfaces_static')
    write_file_content('./interfaces/interfaces_static', raw_content % intranet_ip)

def restart_pptpd(intranet_ip):
    raw_content = read_file_content('./pptpd/raw_pptpd.conf')
    write_file_content('./pptpd/pptpd.conf', raw_content % intranet_ip)
    commands.getstatusoutput('cp -f ./pptpd/pptpd.conf /etc/pptpd.conf')
    commands.getstatusoutput('sudo /etc/init.d/pptpd restart')

def restart_dnsmasq(intranet_ip):
    raw_content = read_file_content('./dns/raw_dnsmasq.conf')
    write_file_content('./dns/dnsmasq.conf', raw_content % intranet_ip)
    commands.getstatusoutput('cp -f ./dns/dnsmasq.conf /etc/dnsmasq.conf')
    commands.getstatusoutput('service dnsmasq restart')

def add_route_item():
    commands.getstatusoutput('ip route add 202.193.0.0/16 via 10.20.40.254 dev eno1')
    commands.getstatusoutput('ip route add 10.100.123.0/24 via 10.20.40.254 dev eno1')
    commands.getstatusoutput('ip route add 10.20.0.0/16 via 10.20.40.254 dev eno1')
    commands.getstatusoutput('ip route add 172.16.0.0/16 via 10.20.40.254 dev eno1')


if __name__ == '__main__':
    old_ip = None
    while True:
        ping_state = check_ping()
        if ping_state == False or old_ip == None:
            print time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
            print 'network restart.'
            commands.getstatusoutput('dhclient eno1')
            # get new intranet ip
            intranet_ip = get_local_ip("eno1")
            if intranet_ip is None:
                continue
            if old_ip == None or old_ip != intranet_ip:
                print 'new ip: ',intranet_ip
                send_email('新的ip为: %s' % intranet_ip)
                create_interfaces_static_file(intranet_ip)
                restart_pptpd(intranet_ip)
                # restart_dnsmasq(intranet_ip)
                old_ip = intranet_ip
            commands.getstatusoutput('cp -f ./interfaces/interfaces_static /etc/network/interfaces')
            commands.getstatusoutput('/etc/init.d/networking restart')
            # commands.getstatusoutput('dhclient eth0')
            # commands.getstatusoutput('cp -f ./dns/resolv.conf /etc/resolv.dnsmasq.conf')
            add_route_item()
            time.sleep(1)
            print 'config complete.'
            continue
        time.sleep(2)
