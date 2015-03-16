# -*- coding: utf-8 -*-
""" description mail op"""

from email.mime.text import MIMEText
import smtplib


class MailClient(object):
    def __init__(self, address, username, password, sender=None):
        """目前只支持 smtp
        :param address: smtp server address. eg. ('smtp.163.com', 25)
        :param username: the sender`s email. eg. 'gf0842wf@163.com'
        :param password: the sender`s password
        :param sender: the mail sender format. eg. 'wangfei<gf0842wf@163.com>'
        """
        self.address = address
        self.username = username
        self.password = password
        self.sender = sender or '%s<%s>'(username.split('@')[0], username)

        # 创建并连接
        self.handle = smtplib.SMTP(*address)
        # 登陆
        self.handle.login(username, password)

    def send_mail(self, receivers, subject, content, subtype='plain', charset='utf-8'):
        # 创建一个MIMEText实例，subtype设置为普通(plain)格式邮件, 设置为html就可以发送html内容了
        msg = MIMEText(content, subtype, charset)

        # 加邮件头
        msg['Subject'] = subject
        msg['From'] = self.sender
        msg['To'] = ';'.join(receivers)

        # 发邮件
        self.handle.sendmail(msg["From"], receivers,
                             msg.as_string())  # 必须使用 receivers ,而不是msg['To'],但是msg['To']不能省

    def close(self):
        self.handle.quit()

    def __del__(self):
        try:
            self.close()
        except:
            pass


if __name__ == '__main__':
    mail_client = MailClient(('smtp.163.com', 25), 'xxxx@163.com', 'password', 'xxxx<xxxx@163.com>')
    mail_client.send_mail(['11111@qq.com', '22222@qq.com'], 'test', u'测试', 'plain', 'utf-8')
    mail_client.send_mail(['11111@qq.com', '22222@qq.com'], 'test', u'测试2', 'plain', 'utf-8')
    mail_client.close()