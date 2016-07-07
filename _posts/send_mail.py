# coding: utf-8
import email,sys,os
import smtplib
from email.MIMEText import MIMEText
from email.MIMEMultipart import MIMEMultipart
from email.MIMEImage import MIMEImage

SENDER = 'xxxx@xxxx.com'
SMTPSERVER = 'smtp.xxxx.com:xxx'
USERNAME = 'xxxx'
APIKEY = 'xxxx'

##############
#subject  :标题
#receivers:收件人
#cc       :抄送人
#content  :内容
#atts     :附件
##############
def sendMail(subject, receivers, cc, content, atts):
    msg = MIMEMultipart('related')
    msg['Subject'] = unicode(subject, "UTF-8")
    msg['From'] = SENDER
    msg['To'] = receivers
    msg['Cc'] = cc

    if os.path.isfile(content):
        if(content.split('.')[-1]=='html'):
            cont = MIMEText(open(content).read(),'html','utf-8')
        else:
            cont = MIMEText(open(content).read(),'plain','utf-8')
    else:
        cont = MIMEText(content, 'plain','utf-8')
    msg.attach(cont)

    if atts != -1 and atts != '':
        for att in atts.split(','):
            os.path.isfile(att)
            name = os.path.basename(att)
            att = MIMEText(open(att).read(), 'base64', 'utf-8')
            att["Content-Type"] = 'application/octet-stream'

            att["Content-Disposition"] = 'attachment; filename=%s' % name.decode('utf-8').encode('gbk')
            msg.attach(att)
    print "test1"
    smtp = smtplib.SMTP()
    print smtp

    smtp.connect(SMTPSERVER)
    smtp.ehlo()
    smtp.starttls()
    smtp.ehlo
    smtp.login(USERNAME, APIKEY)
    for recev in receivers.split(','):
        smtp.sendmail(SENDER,recev, msg.as_string())
    if cc != '':
        for c in cc.split(','):
            smtp.sendmail(SENDER,c, msg.as_string())
    smtp.quit()
 
def main():
    print "start send mail[sendmail.py]"
    subject = sys.argv[1]
    receivers = sys.argv[2]
    print receivers
    print subject
    #cc = sys.argv[3]
    leng = len(sys.argv)
    if leng == 3:
        cc = ""
        content = ""
        atts = -1
    elif leng == 4:
        print "The parameters is not currect!"
        sys.exit(0)
    elif leng == 5:
        cc = sys.argv[3]
        content = sys.argv[4]
        atts = -1
    elif leng == 6:
        cc = sys.argv[3]
        content = sys.argv[4]
        atts = sys.argv[5]
    sendMail(subject, receivers, cc, content, atts)

    print "finish send mail[sendmail.py]"

#sys.argv =[sys.argv[0],'this is for test','xxx@xxx.com','',"Hello world", "D:/1.txt"] 
if __name__=='__main__':
    main()
