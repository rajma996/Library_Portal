import smtplib
from gluon.scheduler import Scheduler
from datetime import *
def send_mail_issue():
    issue=db().select(db.issued_books.ALL)
    for u in issue:
        r=[]
        user=str(u.issue_name)
        book=str(u.name)
        email=str(u.email_id)
        server=str(u.email_id).split('@')[1]
        msg=str("Hello "+user+".You have not returned "+book+".")
        mesg='Subject: Library Books Overdue Notice\nFrom: library<library@iiit.ac.in>\nTo: %s\n\n%s'%(user,msg)
        try :
            server=smtplib.SMTP(server)
            server.sendmail("library@iiit.ac.in",[email],mesg)
            server.quit()
        except SMTPError:
            print "Message not sent"
    return 1


scheduler=Scheduler(db)
