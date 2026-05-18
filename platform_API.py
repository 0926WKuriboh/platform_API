# coding=UTF-8
import json
import psycopg2 as psycopg2
from flask import Flask, request
from flask_cors import CORS
import csv
from io import StringIO
import uuid
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


app = Flask(__name__)
CORS(app)

@app.route('/Varify', methods=['POST'])#apply main account number
def Varify():
    data = request.get_json(force=True)  # 獲取json資料

    uuid = data['token']

    # connect and insert
    conn = psycopg2.connect(database="ddg1pjo52la6qm", user="qpbgbkjbwhryjo",
                            password="1960aac10b4729cca4ed82aec18bc6de7722dd77daeb95f195a6f5b7cf2cef01",
                            host="ec2-52-73-247-67.compute-1.amazonaws.com", port="5432")
    cursor = conn.cursor()

    cursor.execute("select mail from verify_data where id= '%s' " % uuid)
    mail = cursor.fetchall()

    if mail==[]:
        return 'False'

    mail=mail[0][0]
    cursor.execute("UPDATE user_data SET verify = '1' WHERE mail = '%s' "% mail)

    return 'success'

@app.route('/MainApply', methods=['POST'])#apply main account number
def main_apply():
    data = request.get_json(force=True)  # 獲取json資料

    name = data['name']
    mail = data['mail']
    password = data['password']

    # connect and insert
    conn = psycopg2.connect(database="ddg1pjo52la6qm", user="qpbgbkjbwhryjo",
                            password="1960aac10b4729cca4ed82aec18bc6de7722dd77daeb95f195a6f5b7cf2cef01",
                            host="ec2-52-73-247-67.compute-1.amazonaws.com", port="5432")
    cursor = conn.cursor()

    cursor.execute("select mail from user_data where mail= '%s' " % mail)
    myresult = cursor.fetchall()

    val1=(name,mail,password)

    if len(myresult)==0:
        cursor.execute("insert into user_data(name,mail,password) values(%s,%s,%s)", val1)
        cursor.execute("UPDATE user_data SET verify = '0' WHERE mail = '%s' "% mail)


        conn.commit()
        cursor.close()
        conn.close()

        return 'success'
    else:
        return 'no'

@app.route('/SubApply', methods=['POST'])#apply sub account number
def sub_apply():
    data = request.get_json(force=True)  # 獲取json資料

    name = data['name']
    mail = data['mail']
    password = data['password']
    main_mail=data['main_mail']

    # connect and insert
    conn = psycopg2.connect(database="ddg1pjo52la6qm", user="qpbgbkjbwhryjo",
                            password="1960aac10b4729cca4ed82aec18bc6de7722dd77daeb95f195a6f5b7cf2cef01",
                            host="ec2-52-73-247-67.compute-1.amazonaws.com", port="5432")
    val1 = (name, mail, password, main_mail)
    cursor = conn.cursor()
    cursor.execute("select mail from user_data where mail= '%s' " % mail)
    myresult = cursor.fetchall()
    print(len(myresult))
    if len(myresult) == 0:
        cursor.execute("insert into user_data(name,mail,password,parent) values(%s,%s,%s,%s)", val1)
        conn.commit()
        cursor.close()
        conn.close()
        return "success"
    else:
        return "no"

@app.route('/SignIn', methods=['POST'])
def SignIn():
    data = request.get_json(force=True)  # 獲取json資料

    mail = data['mail']
    password = data['password']

    conn = psycopg2.connect(database="ddg1pjo52la6qm", user="qpbgbkjbwhryjo",
                            password="1960aac10b4729cca4ed82aec18bc6de7722dd77daeb95f195a6f5b7cf2cef01",
                            host="ec2-52-73-247-67.compute-1.amazonaws.com", port="5432")

    cursor = conn.cursor()
    cursor.execute("select name,parent,varify from user_data where mail= '%s' and password='%s'  " % (mail,password))
    search_user=cursor.fetchall()

    conn.commit()
    cursor.close()
    conn.close()

    search_user = json.dumps(search_user)

    print(search_user)

    if search_user=="[]":
        return "false"
    else:
        return search_user

@app.route('/Article', methods=['GET'])#get article
def article():
    number = request.args.get('number')  # 獲取json資料


    conn = psycopg2.connect(database="ddg1pjo52la6qm", user="qpbgbkjbwhryjo",
                            password="1960aac10b4729cca4ed82aec18bc6de7722dd77daeb95f195a6f5b7cf2cef01",
                            host="ec2-52-73-247-67.compute-1.amazonaws.com", port="5432")

    cursor = conn.cursor()
    cursor.execute("select article,text,category from article_data where number='%s' " % number)

    article = cursor.fetchall()
    conn.commit()
    cursor.close()
    conn.close()

    article = json.dumps(article)

    return article

@app.route('/AddArticle', methods=['POST'])#use CSV to add article
def AddArticle():
    data = request.files['data']
    csvf = StringIO(data.read().decode())
    rows = csv.reader(csvf)

    conn = psycopg2.connect(database="ddg1pjo52la6qm", user="qpbgbkjbwhryjo",
                            password="1960aac10b4729cca4ed82aec18bc6de7722dd77daeb95f195a6f5b7cf2cef01",
                            host="ec2-52-73-247-67.compute-1.amazonaws.com", port="5432")

    cursor = conn.cursor()
    cursor.execute(" SELECT COUNT(number) FROM article_data")

    number = cursor.fetchall()
    number = int(number[0][0])

    list = []

    for row in rows:
        if rows.line_num == 1:
            continue  # skip first row
        for i in range(len(row)):
            list.append(row[i])
        print(list)
        cursor = conn.cursor()
        number=number+1
        number1=str(number)
        list.insert( 0 , number1)
        cursor.execute(
            "insert into article_data(number,article,text,q1,a1,q2,a2,q3,a3,category) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", list)
        conn.commit()
        list = []

    cursor.close()
    conn.close()

    return 'ok'

@app.route('/SubMail', methods=['POST']) #find children
def SubMail():
    data = request.get_json(force=True)  # 獲取json資料
    main=data['main']

    conn = psycopg2.connect(database="ddg1pjo52la6qm", user="qpbgbkjbwhryjo",
                            password="1960aac10b4729cca4ed82aec18bc6de7722dd77daeb95f195a6f5b7cf2cef01",
                            host="ec2-52-73-247-67.compute-1.amazonaws.com", port="5432")

    cursor = conn.cursor()
    cursor.execute("select name,mail,password,id,parent from user_data where parent= '%s'  " % main)

    sub=cursor.fetchall()
    conn.commit()
    cursor.close()
    conn.close()

    sub=json.dumps(sub)

    return sub

@app.route('/AddArticleWeb', methods=['POST'])#add article from web
def AddArticleWeb():
    data = request.get_json(force=True)  # 獲取json資料

    article = data['article']
    text = data['text']
    category = data['category']
    Q1 = data['Q1']
    A1 = data['A1']
    Q2 = data['Q2']
    A2 = data['A2']
    Q3 = data['Q3']
    A3 = data['A3']


    # connect and insert
    conn = psycopg2.connect(database="ddg1pjo52la6qm", user="qpbgbkjbwhryjo",
                            password="1960aac10b4729cca4ed82aec18bc6de7722dd77daeb95f195a6f5b7cf2cef01",
                            host="ec2-52-73-247-67.compute-1.amazonaws.com", port="5432")

    cursor = conn.cursor()
    cursor.execute(" SELECT COUNT(number) FROM article_data")

    number = cursor.fetchall()
    number=str(int(number[0][0])+1)



    val1 = (number, article, text, Q1 ,A1, Q2, A2, Q3, A3,category)
    cursor.execute("insert into article_data(number,article,text,q1,a1,q2,a2,q3,a3,category) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", val1)

    conn.commit()
    cursor.close()
    conn.close()

    val1 = json.dumps(val1)

    return val1

@app.route('/List', methods=['GET']) #Article list
def list():
    page = int(request.args.get('page'))  # 獲取json資料
    count = int(request.args.get('count'))
    conn = psycopg2.connect(database="ddg1pjo52la6qm", user="qpbgbkjbwhryjo",
                            password="1960aac10b4729cca4ed82aec18bc6de7722dd77daeb95f195a6f5b7cf2cef01",
                            host="ec2-52-73-247-67.compute-1.amazonaws.com", port="5432")
    cursor = conn.cursor()

    item = ['number', 'article', 'text']
    bb = []
    cc = []
    dd = []
    first = (page - 1) * count + 1
    last = page * count
    search = (first, last)

    cursor.execute("select DISTINCT category from article_data where number >= %d and number <= %d "% search)
    category = cursor.fetchall()
    for i in range(len(category)):
        dd.append(category[i][0])

    for t in range(len(category)):
        search2 = (dd[t],first,last)
        cursor.execute(
            "select number,article,text from article_data where category = '%s' and number >= %d and number <= %d " % search2)
        list = cursor.fetchall()

        for i in range(len(list)):

                dictionary = dict(zip(item, list[i]))
                bb.append(dictionary)
                dictionary = {}

        cc.append(bb)
        bb = []

    final = dict(zip(dd, cc))

    cursor.execute("SELECT COUNT(number) FROM article_data")
    num = cursor.fetchall()
    final ['num'] = num[0][0]

    article = json.dumps(final)
    conn.commit()
    cursor.close()
    conn.close()

    return article

@app.route('/SendMail', methods=['POST']) #Article list
def SendMail():
    data = request.get_json(force=True)  # 獲取json資料
    mail = data['mail']

    send_uuid = uuid.uuid1()
    print(send_uuid)
    send_uuid = str(send_uuid)

    text = 'click the link https://co-learning.herokuapp.com/current_version/sign_up.html?token=' + send_uuid

    message = Mail(
        from_email='0926testtest@gmail.com',
        to_emails=mail,
        subject='verify mail',
        html_content=text)
    try:
        sg = SendGridAPIClient('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')
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e)


    conn = psycopg2.connect(database="ddg1pjo52la6qm", user="qpbgbkjbwhryjo",
                            password="1960aac10b4729cca4ed82aec18bc6de7722dd77daeb95f195a6f5b7cf2cef01",
                            host="ec2-52-73-247-67.compute-1.amazonaws.com", port="5432")
    cursor = conn.cursor()

    val1=(send_uuid,mail)

    cursor.execute("insert into verify_data(id,mail) values(%s,%s)", val1)

    conn.commit()
    cursor.close()
    conn.close()

    return send_uuid

@app.route('/Modify', methods=['POST']) #Article list
def Modify():
    data = request.get_json(force=True)  # 獲取json資料

    conn = psycopg2.connect(database="ddg1pjo52la6qm", user="qpbgbkjbwhryjo",
                            password="1960aac10b4729cca4ed82aec18bc6de7722dd77daeb95f195a6f5b7cf2cef01",
                            host="ec2-52-73-247-67.compute-1.amazonaws.com", port="5432")
    cursor = conn.cursor()

    mail=data['mail']
    name=data['new_name']
    password=data['password']


    print(password)
    if password=='':
        val1 = (name, mail)
        cursor.execute("update user_data set name = %s where mail = %s ", val1)
        conn.commit()
        cursor.close()
        conn.close()

        return 'success'

    else:
        val1=(name,password,mail)

        cursor.execute("update user_data set name = %s, password = %s where mail = %s ", val1)

        conn.commit()
        cursor.close()
        conn.close()

        return 'success'

@app.route('/Delete', methods=['POST']) #Article list
def delete():
    data = request.get_json(force=True)  # 獲取json資料

    main_mail=data['main_mail']
    del_mail=data['del_mail']

    val1=(main_mail,main_mail)
    val2=(del_mail,main_mail)

    conn = psycopg2.connect(database="ddg1pjo52la6qm", user="qpbgbkjbwhryjo",
                            password="1960aac10b4729cca4ed82aec18bc6de7722dd77daeb95f195a6f5b7cf2cef01",
                            host="ec2-52-73-247-67.compute-1.amazonaws.com", port="5432")
    cursor = conn.cursor()

    if main_mail == del_mail:
        cursor.execute("DELETE FROM user_data WHERE mail = %s or parent = %s",val1 )
    else :
        cursor.execute("DELETE FROM user_data WHERE mail = %s and parent = %s",val2)

    conn.commit()
    cursor.close()
    conn.close()


    return 'success'

@app.route('/Status', methods=['POST']) #Article list
def status():
    data = request.get_json(force=True)  # 獲取json資料

    mail=data['mail']
    number=data['number']
    article=data['article']
    time=data['time']
    category=data['category']

    val1=(mail,number,article,time,category)

    conn = psycopg2.connect(database="ddg1pjo52la6qm", user="qpbgbkjbwhryjo",
                            password="1960aac10b4729cca4ed82aec18bc6de7722dd77daeb95f195a6f5b7cf2cef01",
                            host="ec2-52-73-247-67.compute-1.amazonaws.com", port="5432")
    cursor = conn.cursor()

    cursor.execute("insert into read_status(mail,number,article,time,category) values(%s,%s,%s,%s,%s)", val1)

    conn.commit()
    cursor.close()
    conn.close()

    return 'success'

@app.route('/Data', methods=['POST']) #Article list
def data():
    data = request.get_json(force=True)  # 獲取json資料

    mail1=data['mail']

    conn = psycopg2.connect(database="ddg1pjo52la6qm", user="qpbgbkjbwhryjo",
                            password="1960aac10b4729cca4ed82aec18bc6de7722dd77daeb95f195a6f5b7cf2cef01",
                            host="ec2-52-73-247-67.compute-1.amazonaws.com", port="5432")
    cursor = conn.cursor()

    cursor.execute("select number,article,time,category from read_status where mail= '%s' " % mail1)
    data = cursor.fetchall()
    data = json.dumps(data)

    conn.commit()
    cursor.close()
    conn.close()

    return data

@app.route('/category', methods=['GET']) #Article list
def category():
    conn = psycopg2.connect(database="ddg1pjo52la6qm", user="qpbgbkjbwhryjo",
                            password="1960aac10b4729cca4ed82aec18bc6de7722dd77daeb95f195a6f5b7cf2cef01",
                            host="ec2-52-73-247-67.compute-1.amazonaws.com", port="5432")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(main_category) FROM category")
    count = cursor.fetchall()
    count1 = count[0][0]
    cursor.execute("select * from category")
    list = cursor.fetchall()

    for i in range(count1):

        list[i] = list[i][0]+"-"+list[i][1]

    list = json.dumps(list)
    conn.commit()
    cursor.close()
    conn.close()

    return list

@app.route('/Ans', methods=['POST']) #Article list
def Ans():
    data = request.get_json(force=True)  # 獲取json資料
    number = data['number']
    ans=data['ans']
    mail=data['mail']
    ans= ans.split(",")
    ans=list(ans)
    num=len(ans)

    conn = psycopg2.connect(database="ddg1pjo52la6qm", user="qpbgbkjbwhryjo",
                            password="1960aac10b4729cca4ed82aec18bc6de7722dd77daeb95f195a6f5b7cf2cef01",
                            host="ec2-52-73-247-67.compute-1.amazonaws.com", port="5432")
    cursor = conn.cursor()

    cursor.execute("select a1,a2,a3 from article_data where number= '%s' " % number)
    correct_ans = cursor.fetchall()

    count=0
    for i in range(num):
        if ans[i] == correct_ans[0][i]:
            count = count + 1

    correct_rate=round(count / num, 2)
    val1 = (number, mail, ans[0], ans[1], ans[2],correct_rate)
    cursor.execute("insert into answer_status(number,mail,user_a1,user_a2,user_a3,correct_rate) values(%s,%s,%s,%s,%s,%s)", val1)

    correct_ans=json.dumps(correct_ans)

    conn.commit()
    cursor.close()
    conn.close()

    return correct_ans



if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)