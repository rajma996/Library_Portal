# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - api is an example of Hypermedia API support and access control
#########################################################################
from reportlab.platypus import *
from reportlab.lib.pagesizes import letter,A4
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.rl_config import defaultPageSize
from reportlab.lib.units import inch,mm,cm
from reportlab.lib.enums import TA_LEFT,TA_RIGHT,TA_CENTER,TA_JUSTIFY
from reportlab.lib import colors
from uuid import uuid4
from cgi import escape
import datetime
from gluon.contrib.pyfpdf import FPDF
import os
import time
import smtplib
if auth.has_membership('librarian')==True:
    response.menu+=[['Manage',False,URL(''),[['Books',True,'manage_book'],['Announcements',True,URL('add_announce')],['FAQ',True,'manage_faq']]]]
def index():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html

    if you need a simple wiki simply replace the two lines below with:
    return auth.wiki()
    """
    #response.flash = T("Welcome to web2py!")
    #table=TABLE(TR(TD("About Library")),TR(TD("Services")),TR(TD("Recent Additions")),TR(TD("Library Rules")),TR(TD("Working Hours")),TR(TD("Book Requisition Form")),_class="side_table")
    #table=['Issued Books','Reserved Books','About Library','Services','Announcements','E-Resources','Recent Additions','Library Rules','Working Hours','Book Requisition Form','Print Journals','Newspaper Coverages']
    #if auth.is_logged_in()==True:
    #if auth.user!=None:
    announce=db(db.announcements).select()
    return dict(announce=announce)



def change():
    if auth.has_membership('librarian')==True:
        var_1=db().select(db.issued_books.ALL)
        var_2=db().select(db.reserve_books.ALL)
    elif auth.is_logged_in()==True:
        var_1=db(db.issued_books.roll_no==(auth.user.roll_no)).select()
        var_2=db(db.reserve_books.roll_no==(auth.user.roll_no)).select()
    if request.vars.what=="1":
        r=[]
        p=[]
        for req in var_1:
            r.append(req.issue_name)
            r.append(req.name)
            r.append(req.roll_no)
            r.append(str(req.datelimit).split()[0])
            p.append(list(r))
            r=[]
        return CAT(H3('Issued Books'),TABLE(TR(TH('Name'),TH('Book Name'),TH('Roll Number'),TH('Return Date')),[TR(f) for f in p],_class="book",_id="res_book"))
        #return tuple(var_2.name,var_2.issue_name)
    elif request.vars.what=="2": 
        r=[]
        p=[]
        for req in var_2:
            r.append(req.issue_name)
            r.append(req.name)
            r.append(req.roll_no)
            p.append(list(r))
            r=[]
        return CAT(H3('Reserved Books'),TABLE(TR(TH('Name'),TH('Book Name'),TH('Roll Number')),[TR(f) for f in p],_class="book",_id="res_book"))

    elif request.vars.what=="email":
        today=datetime.datetime.now()
        all_user=db(db.issued_books).select()
        for user in all_user:
            return_date=user.datelimit
            diff=(return_date-today).days
            if diff==1 or diff==4:
                server=str(user.email_id).split('@')[1]
                msg=str(user.issue_name+",your have for "+user.name+" .Please return it on "+str(user.datelimit).split()[0] +".")
                mseg='Subject: Book return reminder.\nFrom: library<library@iiit.ac.in>\nTo: %s\n\n%s'%(user.issue_name,msg)
                ser=smtplib.SMTP(server)
                ser.sendmail("library@iiit.ac.in",[user.email_id],mseg)
                ser.quit()
            elif diff<=0:
                server=str(user.email_id).split('@')[1]
                msg=str(user.issue_name+",your have for "+user.name+" .Please return it to library immediately.")
                mseg='Subject: Book return reminder.\nFrom: library<library@iiit.ac.in>\nTo: %s\n\n%s'%(user.issue_name,msg)
                ser=smtplib.SMTP(server)
                ser.sendmail("library@iiit.ac.in",[user.email_id],mseg)
                ser.quit()
        return "Mail send succesfully."


    elif request.vars.what=="3":
        p=open(os.path.join(request.folder,'static','text/about_library.txt'),'rb')
        para=[]
        for line in p.readlines():
            para.append(line)
        return CAT(H3('About Library'),BEAUTIFY(para))
    elif request.vars.what=="4":
        p=open(os.path.join(request.folder,'static','text/service.txt'),'rb')
        para=[]
        for line in p.readlines():
            para.append(line)
        return CAT(H3('Services'),UL([LI(f) for f in para]))
        return None
    elif request.vars.what=="5":
        announce=db(db.announcements).select()
        p=[]
        for req in announce:
            r=[]
            r.append(req.description)
            p.append(list(r))
        return CAT(H3('Announcements'),UL([LI(f) for f in p]))
    elif request.vars.what=="6":
        soft=db().select(db.e_resource.ALL)
        p=[]
        for req in soft:
            size=os.path.getsize(os.path.join(request.folder,'uploads',str(req.softwares)))
            if size<1024:
                size=str(size)+str(" B") 
            else:
                tmp=float(size/1024)
                if tmp<1024:
                    size=str(tmp)+str(" KB")
                else:
                    size=str(float(tmp/1024))+str(" MB")
            r=[]
            r.append(req.name)
            r.append(req.created_on)
            r.append(req.softwares)
            r.append(size)
            p.append(list(r))
        return CAT(H3('E-Resources'),TABLE(TR(TH('Software'),TH('Uploaded On'),TH('Size')),[TR(A(f[0],_href=URL('download',args=f[2])),str(f[1]).split()[0],str(f[3])) for f in p],_class="book",_id="res_book"))
    elif request.vars.what=="7":
        books=db(db.auth_books).select()
        today=datetime.datetime.today()
        p=[]
        count=1
        get_class=lambda a: "even" if a%2==0 else "odd"
        for book in books:
            r=[]
            creation_date=book.created_on
            diff=(today-creation_date).days
            if diff<=120:
                r.append(book.name)
                r.append(book.author)
                r.append(book.Subject)
                r.append(book.ISBN)
                r.append(book.publisher)
                r.append(book.created_on)
                r.append(count)
                p.append(list(r))
                count=count+1
        return CAT(H3('Recent Additions'),TABLE(TR(TH('Book'),TH('Author'),TH('Subject'),TH('ISBN'),TH('Publisher'),TH('Added On')),[TR(f[0],f[1],f[2],f[3],f[4],f[5],_class=get_class(int(f[6]))) for f in p],_class="book",_id="res_book"))
        #return str("Aaj din hai "+bday+" aur mahina hai "+bmonth+" aur saal hai"+byear)
    elif request.vars.what=="8":
        p=open(os.path.join(request.folder,'static','text/rules.txt'),'rb')
        para=[]
        for line in p.readlines():
            para.append(line)
        return CAT(H3('About Library'),BEAUTIFY(para))
    elif request.vars.what=="9":
        form=FORM(
                CAT(SPAN("Book: "),INPUT(_name="name",_type="text",_class="form")),BR(),
                CAT(SPAN("Author "),INPUT(_name="author",_type="text",_class="form")),BR(),
                CAT(SPAN("Subject "),INPUT(_name="sub",_type="text",_class="form")),BR(),
                CAT(SPAN("ISBN  "),INPUT(_name="isbn",_type="text",_class="form")),BR(),
                CAT(SPAN("Publisher "),INPUT(_name="publish",_type="text",_class="form")),BR(),
                INPUT(_name="sub",_type="submit",_value="submit",_onsubmit="ajax('change?what=13',[],'change');")
                )
        return form
    elif request.vars.what=="10":
        form=SQLFORM(db.book_request)
        return form
    elif request.vars.what=="13":
        response.flash=T("Granted")
        return None
    '''
    elif request.vars.what=="11":
    elif request.vars.what=="12":
    '''

def get_pdf():
    return dict()
def gen_pdf():
    if request.vars.name=="1":
        title="Collections"
        heading="List of available books"
        user=db(db.auth_books).select()
        d=[['Book','Author','Subject','ISBN','Publisher']]
        for u in user:
            content=[]
            content.append(u.name)
            content.append(u.author)
            content.append(u.Subject)
            content.append(u.ISBN)
            content.append(u.publisher)
            content.append(str(u.created_on).split()[0])
            d.append(list(content))
    elif request.vars.name=="2":
        title="Issued Books"
        heading=""
        user=db(db.issued_books).select()
        d=[['Book','Issued By','Email ID','Roll No.']]
        for u in user:
            content=[]
            content.append(u.name)
            content.append(u.issue_name)
            content.append(u.email_id)
            content.append(u.roll_no)
            content.append(str(u.created_on).split()[0])
            d.append(list(content))
    elif request.vars.name=="3":
        title="Reserved Books"
        heading=""
        user=db(db.reserve_books).select()
        d=[['Book','Reserved By','Email ID','Roll No.']]
        for u in user:
            content=[]
            content.append(u.name)
            content.append(u.issue_name)
            content.append(u.email_id)
            content.append(u.roll_no)
            content.append(str(u.created_on).split()[0])
            d.append(list(content))
    elif request.vars.name=="4":
        title="All Library Users"
        heading=""
        user=db(db.auth_user).select()
        d=[['Name','Email Id','Roll No']]
        for u in user:
            content=[]
            content.append(str(u.first_name+" "+u.last_name))
            content.append(u.email)
            content.append(u.roll_no)
            d.append(list(content))
    elif request.vars.name=="5":
        title="Library Book Overdue Notice"
        heading="List of students"
        user=db(db.issued_books).select()
        d=[['Book','Issued By','Email ID','Roll No.']]
        for u in user:
            content=[]
            content.append(u.name)
            content.append(u.issue_name)
            content.append(u.email_id)
            content.append(u.roll_no)
            content.append(str(u.created_on).split()[0])
            d.append(list(content))
    styles=getSampleStyleSheet()
    tmpfilename=os.path.join(request.folder,'private',str(uuid4()))
    doc=SimpleDocTemplate(tmpfilename)
    story=[]
    story.append(Paragraph(escape(title),styles["Title"]))
    story.append(Paragraph(escape(heading),styles["Heading2"]))
    for t in d:
        text=str(t[0])+str(t[1])+str(t[2])
        story.append(Paragraph(escape(text),styles["Normal"]))
        story.append(Spacer(1,5*mm))
    doc.build(story)
    data=open(tmpfilename,"rb").read()
    os.unlink(tmpfilename)
    response.headers['Content-Type']='application/pdf'
    return data


#def searchbook():
#    search=db().select(db.auth_books.ALL)
#    grid=SQLFORM.smartgrid(db.auth_books,deletable=False,create=False,orderby='name',editable = auth.has_membership('librarian'))
#    form=FORM(INPUT(_type="submit",_value="Issue Book"))
#    if form.process().accepted:
#        redirect('default','issue')
#    return dict(grid=grid,search=search,form=form)
def searchbook():
    form=FORM(INPUT(_id='keyword',_name='keyword',_value="type any keyword",_onfocus="jQuery('#keyword').prop('value','');"),
            INPUT(_type="Submit",_value="Submit",_name="choice",_class="submit",default="shiv"),
            INPUT(_type="Submit",_value="List all books",_name="list_all",_class="list_all"),BR(),
            #,_onkeyup="ajax('callback',['keyword'],'target');"),BR(),
            CAT(SPAN('Search via:')),
            CAT(INPUT(_type="radio",_name="choose",_value="name"),SPAN('Name')),
            CAT(INPUT(_type="radio",_name="choose",_value="author"),SPAN('Author')),
            CAT(INPUT(_type="radio",_name="choose",_value="sub"),SPAN('Subject')),
            CAT(INPUT(_type="radio",_name="choose",_value="isbn"),SPAN('ISBN')),
            CAT(INPUT(_type="radio",_name="choose",_value="publisher"),SPAN('Publisher')),
            _class="choice")
    query=""
    if form.process().accepted:
        if request.vars.keyword=="type any keyword":
            query=db(db.auth_books).select(orderby=db.auth_books.name)
        elif request.vars.choose=="author":
            q=db.auth_books.author.contains(request.vars.keyword)
            query=db(q).select(orderby=db.auth_books.name)
        elif request.vars.choose=="sub":
            q=db.auth_books.Subject.contains(request.vars.keyword)
            query=db(q).select(orderby=db.auth_books.name)
        elif request.vars.choose=="isbn":
            q=db.auth_books.ISBN.contains(request.vars.keyword)
            query=db(q).select(orderby=db.auth_books.name)
        elif request.vars.choose=="publisher":
            q=db.auth_books.publisher.contains(request.vars.keyword)
            query=db(q).select(orderby=db.auth_books.name)
        else:
            q=db.auth_books.name.contains(request.vars.keyword)
            query=db(q).select(orderby=db.auth_books.name)
    return dict(form=form,query=query)
@auth.requires_membership('librarian')
def add_announce():
    form=FORM(
            CAT(SPAN('Name:'),INPUT(_type="text",_name="name")),BR(),
            CAT(SPAN('Description:'),INPUT(_type="text",_name="des")),BR(),
            CAT(INPUT(_type="radio",_name="cho",_value="del"),SPAN("Check to delete")),BR(),
            CAT(INPUT(_type="radio",_name="cho",_value='up'),SPAN("Check to update")),BR(),
            INPUT(_type="submit",_value="Submit"))
    if form.process().accepted:
        if request.vars.cho=="del":
            db(db.announcements.name==request.vars.name).delete()
        elif request.vars.cho=="up":
            u=db(db.announcements.name==request.vars.name).validate_and_update(description=request.vars.des)
            if u.errors:
                response.flash=T("Invalid Form")
            else:
                response.flash=T('announcement updated!')
        else:
            r=db.announcements.validate_and_insert(name=request.vars.name,description=request.vars.des)
            if r.errors:
                response.flash=T("Record already exist")
            else:
                response.flash=T('New announcement added!')
    elif form.errors:
        response.flash=T("Invalid Form")
    query=db(db.announcements).select()
    return dict(form=form,query=query)

@auth.requires_membership('librarian')
def manage_book():
    form=SQLFORM.factory(
            Field('book_name',label="Enter book name",type="textbox",requires=IS_NOT_EMPTY()),
            Field('book_number',label="Book Number",type="textbox",requires=IS_INT_IN_RANGE(1,10000000000)),
            Field('author',label="Author(update/insert)",type="textbox",requires=IS_NOT_EMPTY()),
            Field('subject',label="Subject(update/insert)",type="textbox"),
            Field('isbn',label="ISBN(update/insert)",type="textbox"),
            Field('publisher',label="Publisher(update/insert)",type="textbox"),
            Field('book_pos',label="Book Positon(update/insert)",type="textbox"),
            Field('count',label="Total number of copies(update/insert)",type="textbox"),
            Field('Option',widget=SQLFORM.widgets.radio.widget,requires=IS_IN_SET({True:'Update',False:'Delete',None:'Add'})))
    if form.process().accepted:
        bookname=str(form.vars.book_name)
        booknum=int(form.vars.book_number)
        if form.vars.Option=="True":
            book=db(db.auth_books.name==bookname).validate_and_update(author=form.vars.author,Subject=form.vars.subject,ISBN=form.vars.isbn,book_pos=form.vars.book_pos,publisher=form.vars.publisher,id=booknum,bookcount=int(form.vars.count))
            if book.errors:
                response.flash=T("Invalid Form")
            else:
                response.flash=T("Book details Updated")
        elif form.vars.Option=="False":
            db(db.auth_books.name==bookname).delete()
            response.flash=T("Book details removed")
        else:
            book=db.auth_books.validate_and_insert(name=bookname,author=form.vars.author,Subject=form.vars.subject,ISBN=form.vars.isbn,book_pos=form.vars.book_pos,publisher=form.vars.publisher,id=booknum,bookcount=int(form.vars.count))
            if book.errors:
                response.flash=T("Book already exist")
            else:
                response.flash=T("New Book added")
    return dict(form=form)


@auth.requires_membership('librarian')
def manage_faq():
    form=SQLFORM.factory(
            Field('faq_Q',label="Enter Question",type="textbox",requires=IS_NOT_EMPTY()),
            Field('faq_A',label="Enter Answer",type="textbox",requires=IS_NOT_EMPTY()),
            Field('Option',widget=SQLFORM.widgets.radio.widget,requires=IS_IN_SET({True:'Update',False:'Delete',None:'Add'}))
            )
    if form.process().accepted:
        ques=str(form.vars.faq_Q)
        if form.vars.Option=="True":
            F=db(db.faq.question==ques).validate_and_update(answer=form.vars.faq_A)
            if F.errors:
                response.flash=T("Invalid Form")
            else:
                response.flash=T("Answer Updated")
        elif form.vars.Option=="False":
            db(db.faq.question==ques).delete()
            response.flash=T("Question removed")
        else:
            F=db.faq.validate_and_insert(question=ques,answer=form.vars.faq_A)
            if F.errors:
                response.flash=T("Question already exist")
            else:
                response.flash=T("Question added")
    return dict(form=form)


def issue():

           form=FORM(
                   CAT(SPAN('Enter Bookname:'),INPUT(_id='keyword',_name='keyword',_value="type any keyword",_onfocus="jQuery('#keyword').prop('value','');")),
            BR(),
             #,_onkeyup="ajax('callback',['keyword'],'target');"),BR(),
             CAT(SPAN('Search via:')),
             CAT(INPUT(_type="radio",_name="key",_value="name"),SPAN('Name')),
             CAT(INPUT(_type="radio",_name="key",_value="author"),SPAN('Author')),
             CAT(INPUT(_type="radio",_name="key",_value="subject"),SPAN('Subject')),
             CAT(INPUT(_type="radio",_name="key",_value="isbn"),SPAN('ISBN')),
             CAT(INPUT(_type="radio",_name="key",_value="publisher"),SPAN('Publisher')),BR(),
             CAT(SPAN('Issue for')),
             CAT(INPUT(_type="radio",_name="sop",_value="student"),SPAN('Student')),
             CAT(INPUT(_type="radio",_name="sop",_value="faculty"),SPAN('Faculty')),BR(),
             CAT(SPAN('Select')),
             CAT(INPUT(_type="radio",_name="is_for",_value="issue"),SPAN('Issue Book')),
             CAT(INPUT(_type="radio",_name="is_for",_value="book_return"),SPAN('Return Book')),BR(),
             CAT(SPAN('Roll Number'),INPUT(_id="keyword1",_name="keyword1",_value="Enter Roll NO.",_onfocus="jQuery('#keyword1').prop('value','');")),BR(),
             INPUT(_type="Submit",_value="Submit",_name="choice",_class="submit",default="shiv"),
             _class="choice")
           query=""
           y=form.process().accepted
           if (y and request.vars.is_for!="issue" and request.vars.is_for!="book_return"):
                session.error=1
                redirect(URL('error'))
           if (y and request.vars.is_for=="issue"):
             if(request.vars.key=="name"):
                 q=db.auth_books.name.contains(request.vars.keyword)
                 query=db(q).select(orderby=db.auth_books.name)
             elif request.vars.key=="author":
                 q=db.auth_books.author.contains(request.vars.keyword)
                 query=db(q).select(orderby=db.auth_books.name)
             elif request.vars.key=="subject":
                 q=db.auth_books.Subject.contains(request.vars.keyword)
                 query=db(q).select(orderby=db.auth_books.name)
             elif request.vars.key=="isbn":
                 q=db.auth_books.ISBN.contains(request.vars.keyword)
                 query=db(q).select(orderby=db.auth_books.name)
             elif request.vars.key=="publisher":
                 q=db.auth_books.publisher.contains(request.vars.keyword)
                 query=db(q).select(orderby=db.auth_books.name)
             else:
                 q=db.auth_books.name.contains(request.vars.keyword)
                 query=db(q).select(orderby=db.auth_books.name)
             session.query=query
             session.name=None
             session.roll=request.vars.keyword1
             if (request.vars.sop=="student"):
                 session.name="student"
             if request.vars.sop=="faculty":
                 session.name="faculty"
             if(session.name!=None and session.query!=""):
                 redirect(URL('default','issuesubmit'))
             else:
                 redirect(URL('default','error'))
                 #redirect(URL('default','index'))
           elif (y and request.vars.is_for=="book_return"):
             if request.vars.keyword=="type any keyword":
                 response.flash=T('Please enter a book name')
             elif request.vars.key=="name":
                 q=db.issued_books.name.contains(request.vars.keyword)
                 query=db(q).select(orderby=db.issued_books.name)
             elif request.vars.key=="author":
                 q=db.isued_books.author.contains(request.vars.keyword)
                 query=db(q).select(orderby=db.issued_books.name)
             elif request.vars.key=="subject":
                 q=db.issued_books.Subject.contains(request.vars.keyword)
                 query=db(q).select(orderby=db.issued_books.name)
             elif request.vars.key=="isbn":
                 q=db.issued_books.ISBN.contains(request.vars.keyword)
                 query=db(q).select(orderby=db.issued_books.name)
             elif request.vars.key=="publisher":
                 q=db.issued_books.publisher.contains(request.vars.keyword)
                 query=db(q).select(orderby=db.issued_books.name)
             else:
                 q=db.issued_books.name.contains(request.vars.keyword)
                 query=db(q).select(orderby=db.issued_books.name)
             session.query=query
             session.name=None
             session.roll=request.vars.keyword1
             if request.vars.sop=="student":
                 session.name="student"
             if request.vars.sop=="faculty":
                 session.name="faculty"
             if(session.name!=None and session.query!=""):
                 redirect(URL('default','book_returnsubmit'))
             else:
                 redirect(URL('default','error'))
           return dict(form=form)

def error():
    if(session.error==1):
        session.flash=T('Select wheter to issue or return book.')
    elif(session.error==2):
        session.flash=T('The student has already 3 books issued.')
    elif(session.error==3):
        session.flash=T('Same book issued to same student.')
    elif(session.error==7):
        session.flash=T('All the copies had issued.')
    else:
        session.flash=T('Not successful')
    session.error=0
    redirect(URL('default','issue'))

def book_returnsubmit():
            for i in session.query:
                 myquery=(db.issued_books.name==i.name) & (db.issued_books.roll_no==session.roll)
                 db(myquery).delete()
                 j=db(db.auth_books.name==i.name).select()
                 for k in j:
                        db(db.auth_books.name==i.name).update(bookcount=k.bookcount+1)
            redirect(URL('default','index'))           

def issuesubmit():
     count=0
     j=db(db.issued_books.roll_no==session.roll).select()
     for i in j:
            count=count+1
     if(count==3):
                session.error=2
                redirect (URL('default','error'))
     j=db(db.auth_user.roll_no==session.roll).select()
     for i in session.query:
         raj=(db.issued_books.name==i.name) & (db.issued_books.roll_no==session.roll)
         s=db(raj).select()
         for sh in s:
             session.error=3
             redirect(URL('default','error'))
         if(i.bookcount==0):
             session.error=7
             redirect('error')
         elif(i.bookcount>0):
             db.issued_books.insert(name=i.name,author=i.author,ISBN=i.ISBN,Subject=i.Subject,publisher=i.publisher)
             d1= datetime.datetime.today()
             if (session.name=="student"):
                  d1+=datetime.timedelta(days=15)
             if(session.name=="faculty"):
                  d1+=datetime.timedelta(days=30)
             db(db.issued_books.name==i.name).update(datelimit=d1)
             i.update_record(bookcount=i.bookcount-1)
             for k in j:
                 db(db.issued_books.roll_no==None).update(issue_name=str(k.first_name+" "+k.last_name),email_id=k.email,roll_no=k.roll_no)
                 issue_send(str(k.first_name+" "+k.last_name),str(i.name),k.email,d1)
     redirect(URL('default','index'))
            
def faq():
    que=db(db.faq).select()
    return locals()
@auth.requires_login() 
def reserve():
    '''form=FORM(
            CAT(SPAN('Your Name '),INPUT(_type="text",_name="issued_by")),BR(),
            CAT(SPAN('Your Email Id '),INPUT(_type="text",_name="email_id")),BR(),
            CAT(INPUT(_type="checkbox",_name="stud"),SPAN('student')),BR(),
            CAT(SPAN('Your Email Id '),INPUT(_type="text",_name="roll_no")),BR(),
            CAT(SPAN('Enter the bookname '),INPUT(_type="text",_name="book_name")),_class="reserve_book")'''
    if auth.has_membership('librarian')==False:
        form=SQLFORM.factory(
            Field('book_name',label="Enter book name",type="textbox",requires=IS_NOT_EMPTY()),
            Field('unreserve',type='boolean',label='Check to unreserve entered book')
            )
        username=str(str(auth.user.first_name)+" "+str(auth.user.last_name))
        Roll_no=auth.user.roll_no
        email=auth.user.email
    else:
        form=SQLFORM.factory(
            Field('name',label="Student's Name",type="textbox",requires=IS_NOT_EMPTY()),
            Field('roll_no',label="Student's Roll Number",type="textbox",requires=IS_NOT_EMPTY()),
            Field('book_name',label="Enter book name",type="textbox",requires=IS_NOT_EMPTY()),
            Field('unreserve',type='boolean',label='Check to unreserve entered book')
            )
    if form.process().accepted:
        if auth.has_membership('librarian')==True:
            username=str(form.vars.name)
            Roll_no=form.vars.roll_no
            email=db(db.auth_user.roll_no==Roll_no).select()
            l=[]
            for g in email:
                l.append(str(g.email))
                first_name=g.first_name
                last_name=g.last_name
            fname=username.split()[0].lower()
            try:
                lname=username.split()[1].lower()
            except:
                lname=None
            if l==[] or (fname!=str(first_name).lower() and lname!=str(last_name).lower()):
                response.flash=T("Wrong name or roll number!!")
                return dict(form=form)
            email=g.email
        if form.vars.unreserve==True:
            bookname=db(db.reserve_books.name==form.vars.book_name).select()
            flag_got1=0
            for book in bookname:
                if book.roll_no==Roll_no and book.name==form.vars.book_name:
                    response.flash=T(str(book.name + " unreseved.")) 
                    db(db.reserve_books.roll_no==Roll_no and db.reserve_books.name==form.vars.book_name).delete()
                    flag_got1=1
            if flag_got1==0:
                response.flash=T("No such book")
        else:
            bookname=db(db.auth_books.name==form.vars.book_name).select()
            flag_got2=0
            for book in bookname:
                flag_got2=1
                if book.bookcount==0:
                    response.flash=T(str(book.name + " reseved.")) 
                    db.reserve_books.insert(issue_name=username,email_id=email,roll_no=Roll_no,name=book.name,ISBN=book.ISBN,Subject=book.Subject,author=book.author)
                    reserve_send(book.name,email,username)
                else:
                    response.flash=T(str("Book " + book.name+" is available for issue."))
            if flag_got2==0:
                response.flash=T("No such book")
    return dict(form=form) 
def contact_us():
    return dict()
def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/manage_users (requires membership in
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())
def new_test():
    return dict()
def test():
    #doc=SimpleDocTemplate("form.pdf",pagesize=letter,rightMargin=2,leftMargin=30,bottomMargin=18)
    c=canvas.Canvas("form.pdf",pagesize=letter)
    #story.append(Image('IIITH_LP_logo.png',2*cm,2*cm))
    #c=canvas.Canvas("form.pdf",
    #doc.build(story)  
    story=[['a','b'],['1','2']]
    x=100
    y=700
    for l in story[0]:
        c.drawString(x,y,str(l))
        c.line(x-300,y-5,x+500,y-10)
        y=y-50
    c.save()
    #tmpfilename=os.path.join(request.folder,'private',str(uuid4()))
    p=open("form.pdf",'rb').read()
    response.headers['Content-Type']='application/pdf'
    return p
    '''issue=db().select(db.issued_books.ALL)
    r=[]
    l=[]
    for u in issue:
        user=str(u.issue_name)
        book=str(u.name)
        email=str(u.email_id).split('@')[1]
        r.append(str("Hello "+user+".You have not returned "+book+"."))
        r.append(email)
        l.append(list(r))
        r=[]'''
    #return dict(l=TABLE(TR(TH('Message'),TH('Email')),[TR(f) for f in l],_class="book",_id="res_book"))
    #return dict(l=BEAUTIFY(['a','b']))

@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


@auth.requires_login() 
def api():
    """
    this is example of API with access control
    WEB2PY provides Hypermedia API (Collection+JSON) Experimental
    """
    from gluon.contrib.hypermedia import Collection
    rules = {
            '<tablename>': {'GET':{},'POST':{},'PUT':{},'DELETE':{}},
            }
    return Collection(db).process(request,response,rules)
@auth.requires_login()
def issue_send(username,bookname,email,return_date):
    server=str(email).split('@')[1]
    msg=str(username+",library has issued you "+bookname+".Please return this book on "+str(return_date).split()[0]+" .")
    mseg='Subject: Succesfully Book Issued\nFrom: library<library@iiit.ac.in>\nTo: %s\n\n%s'%(username,msg)
    ser=smtplib.SMTP(server)
    ser.sendmail("library@iiit.ac.in",[email],mseg)
    ser.quit()

@auth.requires_login()
def reserve_send(bookname,email,username):
    #email to person who issued the book
    return_date=datetime.datetime
    server=str(email).split('@')[1]
    msg=str(username+",your reservation for "+bookname+" had been successful.")
    mseg='Subject: Successful book reservation\nFrom: library<library@iiit.ac.in>\nTo: %s\n\n%s'%     (username,msg)
    ser=smtplib.SMTP(server)
    ser.sendmail("library@iiit.ac.in",[email],mseg)
    ser.quit()
    
    #email to people who had the books
    query=db(db.issued_books.name==bookname).select()
    for email in query:
        Email=str(email.email_id)
        server=Email.split('@')[1]
        User=str(email.issue_name)
        msg=str(User+",reservation has been made on  "+bookname+".Please return the book to library at date.")
        mseg='Subject: Book reservation\nFrom: library<library@iiit.ac.in>\nTo: %s\n\n%s'%         (User,msg)
        ser=smtplib.SMTP(server)
        ser.sendmail("library@iiit.ac.in",[Email],mseg)
        ser.quit()

    redirect(URL('default','index'))
