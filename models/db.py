# -*- coding: utf-8 -*-

#########################################################################
## This scaffolding model makes your app work on Google App Engine too
## File is released under public domain and you can use without limitations
#########################################################################

## if SSL/HTTPS is properly configured and you want all HTTP requests to
## be redirected to HTTPS, uncomment the line below:
# request.requires_https()

if not request.env.web2py_runtime_gae:
    ## if NOT running on Google App Engine use SQLite or other DB
    db = DAL('sqlite://storage.sqlite',pool_size=1,check_reserved=['all'])
else:
    ## connect to Google BigTable (optional 'google:datastore://namespace')
    db = DAL('google:datastore+ndb')
    ## store sessions and tickets there
    session.connect(request, response, db=db)
    ## or store session in Memcache, Redis, etc.
    ## from gluon.contrib.memdb import MEMDB
    ## from google.appengine.api.memcache import Client
    ## session.connect(request, response, db = MEMDB(Client()))

## by default give a view/generic.extension to all actions from localhost
## none otherwise. a pattern can be 'controller/function.extension'
response.generic_patterns = ['*'] if request.is_local else []

## (optional) optimize handling of static files
# response.optimize_css = 'concat,minify,inline'
# response.optimize_js = 'concat,minify,inline'
## (optional) static assets folder versioning
# response.static_version = '0.0.0'
#########################################################################
## Here is sample code if you need for
## - email capabilities
## - authentication (registration, login, logout, ... )
## - authorization (role based authorization)
## - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
## - old style crud actions
## (more options discussed in gluon/tools.py)
#########################################################################
from gluon.tools import Auth, Crud, Service, PluginManager, prettydate
auth = Auth(db, hmac_key=Auth.get_or_create_key())
crud, service, plugins = Crud(db), Service(), PluginManager()

auth.settings.extra_fields['auth_user']=[Field('roll_no',unique=True)]


## create all tables needed by auth if not custom tables
auth.define_tables(username=False, signature=False)

## configure email
mail = auth.settings.mailer
#mail.settings.server = 'logging' if request.is_local else 'smtp.gmail.com:587'
#mail.settings.sender = 'you@gmail.com'
#mail.settings.login = 'username:password'
mail.settings.server = 'students.iiit.ac.in'
mail.settings.sender = 'shivang.nagaria@students.iiit.ac'

## configure auth policy
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = True

## if you need to use OpenID, Facebook, MySpace, Twitter, Linkedin, etc.
## register with janrain.com, write your domain:api_key in private/janrain.key
from gluon.contrib.login_methods.janrain_account import use_janrain
use_janrain(auth, filename='private/janrain.key')

#########################################################################
## Define your tables below (or better in another model file) for example
##
## >>> db.define_table('mytable',Field('myfield','string'))
##
## Fields can be 'string','text','password','integer','double','boolean'
##       'date','time','datetime','blob','upload', 'reference TABLENAME'
## There is an implicit 'id integer autoincrement' field
## Consult manual for more options, validators, etc.
##
## More API examples for controllers:
##
## >>> db.mytable.insert(myfield='value')
## >>> rows=db(db.mytable.myfield=='value').select(db.mytable.ALL)
## >>> for row in rows: print row.id, row.myfield
#########################################################################

## after defining tables, uncomment below to enable auditing
# auth.enable_record_versioning(db)
db.define_table('auth_books',Field('name',unique=True,requires=IS_NOT_EMPTY()),Field('author'),Field('publisher'),Field('Subject'),Field('ISBN'),Field('book_pos',requires=IS_NOT_EMPTY()),auth.signature,Field('bookcount','integer'))
db.auth_books.name.requires = IS_NOT_IN_DB(db, 'auth_books.name')
db.auth_books.author.requires = IS_NOT_EMPTY()
db.auth_books.publisher.requires = IS_NOT_EMPTY()
db.auth_books.book_pos.requires = IS_NOT_IN_DB(db,'auth_books.book_pos')
db.auth_books.ISBN.requires=IS_NOT_EMPTY()
db.auth_books.Subject.requires=IS_NOT_EMPTY()


db.define_table('issued_books',Field('name'),Field('author'),Field('publisher'),Field('ISBN'),Field('Subject'),Field('issue_name'),Field('roll_no'),Field('email_id'),auth.signature,Field('datelimit','datetime'))
db.issued_books.name.requires=IS_NOT_EMPTY()
db.issued_books.author.requires=IS_NOT_EMPTY()
db.issued_books.ISBN.requires=IS_NOT_EMPTY()
db.issued_books.Subject.requires=IS_NOT_EMPTY()
db.issued_books.email_id.requires=IS_EMAIL()
db.issued_books.roll_no.requires=IS_INT_IN_RANGE(199900000,201500000)
db.issued_books.issue_name.requires=IS_NOT_EMPTY()

db.define_table('reserve_books',Field('name',requires=IS_NOT_EMPTY()),Field('author'),Field('ISBN'),Field('Subject'),auth.signature,Field('issue_name'),Field('roll_no'),Field('email_id'))
db.reserve_books.author.requires=IS_NOT_EMPTY()
db.reserve_books.ISBN.requires=IS_NOT_EMPTY()
db.reserve_books.Subject.requires=IS_NOT_EMPTY()
db.reserve_books.email_id.requires=IS_EMAIL()
db.reserve_books.roll_no.requires=IS_INT_IN_RANGE(199900000,201500000)
db.reserve_books.issue_name.requires=IS_NOT_EMPTY()

db.define_table('announcements',Field('name',unique=True,requires=IS_NOT_EMPTY()),Field('description',requires=IS_NOT_EMPTY()))
db.announcements.name.requires=IS_NOT_IN_DB(db,db.announcements.name)
db.announcements.description.requires=IS_NOT_EMPTY()

db.define_table('e_resource',Field('name',requires=IS_NOT_EMPTY()),Field('softwares','upload'),auth.signature)

db.define_table('book_request',Field('name',requires=IS_NOT_EMPTY()),Field('author'),Field('ISBN'),Field('publisher'))

db.define_table('news',Field('name',requires=IS_NOT_EMPTY()),Field('subject'),Field('link'))

db.define_table('journals',Field('name',requires=IS_NOT_EMPTY()),Field('author'),Field('Subject'))

db.auth_user.roll_no.requires=IS_NOT_EMPTY()

db.define_table('faq',Field('question'),Field('answer'))
