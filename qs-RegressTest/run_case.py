import time
import os
import smtplib
import unittest
import HTMLTestRunnerEN
from email.utils import parseaddr, formataddr
from email.header import Header
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

# 用例路径
case_path = os.path.join(os.getcwd(), "RunFast//TestCase//")#PHZEmptyCardCheckout#ThreeTiFiveKan#AllScoreCheckout
print(case_path)
# 报告存放路径
report_path = os.path.join(os.getcwd(), 'report')
print (report_path)

def all_case():
    discover = unittest.defaultTestLoader.discover(case_path, pattern="*init.py", top_level_dir=None)
    print (discover)
    return (discover)

#格式化邮箱地址、名称
def format_addr(s):
    name, addr = parseaddr(s)
    return formataddr((Header(name, 'utf-8').encode(), addr))

#发送smtp邮件
def sendMail(file_new):
    sender = '13687097822@163.com'
    # 收件人邮箱，，可设置多个
    receiver = ['13687097822@163.com', ]  # "wenjianhua@novaszco.com"
    # 抄送人
    mailToCc = ['zhaoyangyang@lewanhuyu.com']
    subject = '跑胡子自动化测试报告'
    smtpserver = 'smtp.163.com'
    username = '13823720073@163.com'
    password = 'zhao12'

    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ';'.join(mailToCc)


    puretext = MIMEText('自动化执行测试报告请见附件!')
    msg.attach(puretext)
    # 首先是html类型的附件
    htmlpart = MIMEApplication(open(file_new, 'rb').read())
    htmlpart.add_header('Content-Disposition', 'attachment', filename='testReport.html')
    msg.attach(htmlpart)

    smtp = smtplib.SMTP()
    smtp.connect(smtpserver)
    smtp.login(username, password)
    smtp.sendmail(sender, receiver + mailToCc, msg.as_string())
    smtp.quit()

if __name__ == '__main__':

    # 1、获取当前时间，这样便于下面的使用。
    now = time.strftime("%Y-%m-%d", time.localtime(time.time()))#-%H_%M_%S

    # 2、html报告文件路径
    report_abspath = os.path.join(report_path, "result_"+now+".html")

    # 3、打开一个文件，将result写入此file中
    fp = open(report_abspath, "wb")
    runner = HTMLTestRunnerEN.HTMLTestRunner(stream=fp,
                                           title=u'接口自动化测试报告,测试结果如下：',
                                           description=u'用例执行情况：')
    # 4、调用add_case函数返回值
    runner.run(all_case())
    fp.close()

    #5.发送报告邮件
    # sendMail(report_abspath)
    # print("发送成功")


