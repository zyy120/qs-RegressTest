import os,re,unittest,time,smtplib,subprocess,yaml
from email.utils import parseaddr, formataddr
from email.header import Header
from email.mime.text import MIMEText
from HTMLTestRunnerEN import *
# import HTMLTestRunnerEN
from email import encoders

#加载数据文件
def runFastData():
    run_Fast_Data = yaml.load(open('../../conf/runFast/runFast.yml', 'r',encoding='utf-8'))
    return run_Fast_Data

def commonData():
    commonData = yaml.load(open('../../conf/common/common.yml', 'r',encoding='utf-8'))
    return commonData

#封装print方法打印日志，加入开关控制。可以自定义打印或不打印
#入参condition：0 为打印日志，其他值为不打印。默认打印
def printLog(context, condition = 0):
    if 0 == condition:
        print(context)
		
#封装print方法打印web url，加入开关控制。可以自定义打印或不打印
#入参condition：0 为打印日志，其他值为不打印。默认打印
def printUrl(context, condition = 0):
    if 0 == condition:
        print(context)
		
#从文件中匹配相关字符
def getCharInFile(file,replacestr):
    html = open(file,'rb').readlines()
    for line in html:
      result = re.search('Status.+%',bytes.decode(line))
      if result:
         status = result.group().replace(replacestr,'')
         return status

#格式化邮箱地址、名称
def format_addr(s):
    name, addr = parseaddr(s)
    return formataddr((Header(name, 'utf-8').encode(), addr))

#定义需要连跑的测试用例，即测试套
def testSuite(testCaseDir,testCase):
    testSuite = unittest.TestSuite()

    dir_list = []
    for parent, dirnames, filenames in os.walk(testCaseDir):
        if len(dirnames) is 3:
            for i in dirnames:
                dir_list.append(os.path.join(parent, i))

    for _dir in dir_list:
        discover=unittest.defaultTestLoader.discover(_dir, pattern= testCase, top_level_dir= None)
        unittest.defaultTestLoader._top_level_dir = None
        #discover 方法筛选出来的用例，循环添加到测试套件中
        for test_suit in discover:
            testSuite.addTests(test_suit)

    return testSuite

#测试报告生成
def testRunner(reportDir,title,description):
    fr = open(reportDir,'wb')
    testRunner = HTMLTestRunnerEN.HTMLTestRunner(stream=fr, title=title,description=description)
    # fr.colse()
    return testRunner

#发送smtp邮件
def sendMail(mmeText,fromAddr,toAddr,header,smtpServer,passwd):
    msg = MIMEText(mmeText, 'plain', 'utf-8')
    msg['From'] = format_addr(fromAddr)
    msg['To'] = format_addr(toAddr)
    msg['Subject'] = Header(header, 'utf-8').encode()
    smtp = smtplib.SMTP(smtpServer, 25)
    # smtp.set_debuglevel(1)
    smtp.login(fromAddr, passwd)
    smtp.sendmail(fromAddr, toAddr, msg.as_string())
    smtp.quit()

#浮点数支持range
    ''' Computes a range of floating value.
        Input:
            start (float)  : Start value.
            end   (float)  : End value
            steps (integer): Number of values
        
        Output:
            A list of floats
        
        Example:
            >>> print floatrange(0.25, 1.3, 5)
            [0.25, 0.51249999999999996, 0.77500000000000002, 1.0375000000000001, 1.3]
    '''
def floatrange(start,stop,steps):
    return [start+float(i)*(stop-start)/(float(steps)-1) for i in range(steps)]

# def specialTestCaseRun():
    #运行指定用例
    # suiteTest = unittest.TestSuite()
    # suiteTest.addTest(TestAccountFunctionsaa("test_getCachedUserByIdaa"))
    # suiteTest.addTest(TestAccountFunctionsaa("test_getCachedUserByIdaa"))
    # print('Suite_level_1 运行')
    # return suiteTest

#获取执行电脑的用户名和ip。提供给测试报告用
def get_computer_info(regularIP = "192.168"):
    ipList = os.popen("ipconfig |findstr IPv4|findstr " + regularIP)
    userName = os.popen("set USERNAME")
    localName = userName.read().replace("USERNAME=", "")
    localIP = re.findall(regularIP + '.\d+.\d+',ipList.read())
    return( str(", ".join(tuple(localIP))) + ": " + localName)

#获取最后提交者及信息
def lastCommit():
    popen = subprocess.Popen('git log --pretty=format:"%an | %s" -n 1', stdout=subprocess.PIPE, shell=True)
    origin_strs = popen.stdout.read() # 得到的是 bytes, b'字符串内容'
    gitLog = str(origin_strs , encoding='utf-8') 
    return gitLog

####创建一个目录#
def mkdir(dirName):
    if not os.path.exists(dirName):
        #如果不存在则创建目录
        os.makedirs(dirName) 
        print(dirName + ' created succ.')
    else:
        #如果目录存在则不创建，并提示目录已存在
        print(dirName + ' dir exist!')

#############获取当前时间相关方法######################
#获取当前的年。如：2018
def getCurryear():
    localtime = time.localtime()
    return localtime.tm_year

#获取当前的月。如：1
def getCurrmonth():
    localtime = time.localtime()
    return localtime.tm_mon

#获取当前的日期。如：24
def getCurrday():
    localtime = time.localtime()
    return localtime.tm_mday

#获取当前星期几。如：3
def getCurrWeek():
    localtime = time.localtime()
    return localtime.tm_wday + 1

#获取当前时间为几点。如：12 .用于风控停止时间保护设置
def getCurrHour():
    localtime = time.localtime()
    return localtime.tm_hour

#############################################################
#odbc mssql数据库删除数据操作
# def delete_db_data(server,port,database,uid,pwd,sql):
    # cnxn = pyodbc.connect('DRIVER={SQL Server};SERVER=' + server + ';PORT=' + port + ';DATABASE=' + database + ';UID=' + uid + ';PWD=' + pwd)
    # cursor = cnxn.cursor()
    # deleted = cursor.execute(sql).rowcount
    # cnxn.commit()

# odbc mssql数据库查询数据操作
# def select_db_data(server,port,database,uid,pwd,sql):
    # cnxn = pyodbc.connect('DRIVER={SQL Server};SERVER=' + server + ';PORT=' + port + ';DATABASE=' + database + ';UID=' + uid + ';PWD=' + pwd)
    # cursor = cnxn.cursor()
    # cursor.execute(sql)
    # row = cursor.fetchall()
    # if row:
        # return row

####consul 操作。 获取consul某个字段的值
def consul_operater(host='',port='',server='',key='',scheme='http'):
    warnings.simplefilter("ignore", ResourceWarning)
    c = consul.Consul(host=host,port=port,scheme=scheme)
    data = c.catalog.service(server)
    for value in data[1]:
        return value[key]


#pymssql 操作mssql，默认返回元祖。将废弃。请调用下面接口
def mssql_operater(host='',port='',database='',uid='',pwd='',sql=''):
    try:  
        conn = pymssql.connect(host=host,port=port,user=uid,password=pwd,database=database,charset="utf8",tds_version="7.0").cursor()
        #如果是update/delete/insert记得要conn.commit()  #否则数据库事务无法提交
        conn.execute(sql) 
        conn.commit() 
        return conn.fetchall()
    finally:  
        conn.close()

#pymssql 操作mssql，默认返回dict
def mssql_operaters(host='',port='',database='',uid='',pwd='',sql=''):
    try:  
        conn = pymssql.connect(host=host,port=port,user=uid,password=pwd,database=database,charset="utf8",tds_version="7.0",as_dict=True)
        cursor = conn.cursor()
        #如果是update/delete/insert记得要conn.commit()  #否则数据库事务无法提交
        cursor.execute(sql)
        conn.commit()
        for row in cursor:
            return row
    finally:  
        conn.close()


##pymongo 操作mongoDB
def mongoDB_operater(host='',port=''):
    conn = MongoClient(host=host, port=port)
    return conn

##pyhive 操作presto数据库
def presto_operater(host='',port=''):
    cursor = presto.connect(host=host,port=port).cursor()
    # cursor.execute(sql)
    return cursor


#pymysql 操作mysql。默认返回元祖。打算废弃，请调用下面的方法
def mysql_operater(host='',port='',db='',user='',passwd='',sql=''):
    try:  
        connect = pymysql.connect(host=host,port=port,user=user,password=passwd,db=db,charset="utf8")
        cursor = connect.cursor()
        cursor.execute(sql)  
        connect.commit()
        return cursor.fetchall()
    finally:  
        connect.close()

#pymysql 操作mysql。默认返回字典。
def mysql_operaters(host='',port='',db='',user='',passwd='',sql=''):
    try:  
        connect = pymysql.connect(host=host,port=port,user=user,password=passwd,db=db,charset="utf8",cursorclass=pymysql.cursors.DictCursor)
        cursor = connect.cursor()
        cursor.execute(sql)  
        connect.commit()
        for row in cursor.fetchall():
            return row
    finally:  
        connect.close()

