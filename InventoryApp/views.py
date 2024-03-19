from django.shortcuts import render
from django.template import RequestContext
from django.contrib import messages
import pymysql
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage
import datetime

import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import LabelEncoder
from sklearn.svm import SVR
from sklearn.metrics import mean_squared_error
from sklearn.ensemble import RandomForestRegressor
import matplotlib.pyplot as plt

le1 = LabelEncoder()
le2 = LabelEncoder()

dataset = pd.read_csv("Dataset/OnlineRetail.csv",nrows=1000,encoding='iso-8859-1',usecols=['StockCode','Description','Quantity','UnitPrice','Country'])
dataset.fillna(0, inplace = True)

def PredictStockAction(request):
    if request.method == 'POST':
        item = request.POST.get('item', False)
        country = request.POST.get('location', False)
        dataset1 = pd.read_csv("Dataset/OnlineRetail.csv",encoding='iso-8859-1',usecols=['StockCode','Quantity','UnitPrice','Country'])
        dataset1.fillna(0, inplace = True)
        df = dataset1.loc[(dataset1['StockCode'] == item) & (dataset1['Country'] == country)]
        Y = df.values[:,1:2]
        df.drop(['Quantity'], axis = 1,inplace=True)
        df['StockCode'] = pd.Series(le1.fit_transform(df['StockCode'].astype(str)))
        df['Country'] = pd.Series(le2.fit_transform(df['Country'].astype(str)))
        df.fillna(0, inplace = True)
        X = df.values
        sc = MinMaxScaler(feature_range = (0, 1))
        X = sc.fit_transform(X)
        Y = sc.fit_transform(Y)
        size = len(X) - 30
        X_train = X[0:size,0:X.shape[1]-1]
        Y_train = Y[0:size]
        X_test = X[size:len(X),0:X.shape[1]-1]
        Y_test = Y[size:len(X)]

        rf_regression = RandomForestRegressor()
        rf_regression.fit(X_train, Y_train.ravel())
        predict = rf_regression.predict(X_test)

        predict1 = predict.reshape(predict.shape[0],1)
        predict1 = sc.inverse_transform(predict1)
        predict1 = predict1.ravel()
        labels = sc.inverse_transform(Y_test)
        labels = labels.ravel()
        output = '<table border=1><tr><th><font size="" color="black">Stock Code</th><th><font size="" color="black">Available Quantity</th>'
        output += '<th><font size="" color="black">Predicted Quantity</th></tr>'
        for i in range(len(predict1)):
            output += '<tr><td><font size="" color="black">'+item+'</td>'
            output += '<td><font size="" color="black">'+str(labels[i])+'</td>'
            output += '<td><font size="" color="black">'+str(predict1[i])+'</td></tr>'
        context= {'data':output}
        print(output)
        plt.plot(Y_test.ravel(), color = 'red', label = 'Available Quantity')
        plt.plot(predict.ravel(), color = 'green', label = 'Predicted Quantity')
        plt.title('Stock Trend Forecasting')
        plt.xlabel('Available Stock Quantity for Item '+item+" Store Location "+country)
        plt.ylabel('Predicted Stock Quantity for Item '+item+" Store Location "+country)
        plt.legend()
        plt.show()
        return render(request, 'ViewTransaction.html', context)

def PredictStock(request):
    if request.method == 'GET':
        items = np.unique(dataset['StockCode'])
        country = np.unique(dataset['Country'])
        output = '<tr><td><font size="" color="black">Choose&nbsp;Item&nbsp;Code</font></td><td><select name=item>'
        for i in range(len(items)):
            output += '<option value="'+str(items[i])+'">'+str(items[i])+'</option>'
        output += "</select></td></tr>"
        output += '<tr><td><font size="" color="black">Choose&nbsp;Store&nbsp;Location</font></td><td><select name=location>'
        for i in range(len(country)):
            output += '<option value="'+str(country[i])+'">'+str(country[i])+'</option>'
        output += "</select></td></tr>"  
        context= {'data1':output}
        return render(request, 'PredictStock.html', context)

def PurchaseProduct(request):
    if request.method == 'GET':
        temp = dataset.values
        output = '<table border=1><tr><th><font size="" color=black>Stock Code</font></th>'
        output += '<th><font size="" color=black>Stock Name</font></th>'
        output += '<th><font size="" color=black>Available Quantity</font></th>'
        output += '<th><font size="" color=black>Unit Price</font></th>'
        output += '<th><font size="" color=black>Store Location</font></th>'
        output += '<th><font size="" color=black>Purchased Item</font></th><tr>'
        dup = []
        for i in range(len(temp)):
            if temp[i,0] not in dup:
                dup.append(temp[i,0])
                output += '<tr><td><font size="" color="black">'+str(temp[i,0])+'</font></td>'
                output += '<td><font size="" color="black">'+str(temp[i,1])+'</font></td>'
                output += '<td><font size="" color="black">'+str(temp[i,2])+'</font></td>'
                output += '<td><font size="" color="black">'+str(temp[i,3])+'</font></td>'
                output += '<td><font size="" color="blacke">'+str(temp[i,4])+'</font></td>'
                output += '<td><a href=\'Purchase?pid='+str(temp[i,0])+'&price='+str(temp[i,3])+'\'>Click Here</a></td></tr>'
        context= {'data1':output+"<br/><br/><br/><br/><br/>"}
        return render(request, 'PurchaseProduct.html', context)

def Purchase(request):
    if request.method == 'GET':
        pid = request.GET.get('pid', False)
        price = request.GET.get('price', False)
        output = '<tr><td><font size="" color="black">Product&nbsp;ID</b></td><td><input type="text" name="pid" style="font-family: Comic Sans MS" size="30" value='+pid+' readonly/></td></tr>'
        output += '<tr><td><font size="" color="black">Product&nbsp;Price</b></td><td><input type="text" name="price" style="font-family: Comic Sans MS" size="30" value='+price+' readonly/></td></tr>'
        output+='<tr><td><font size="" color="black">Quantity</b></td><td><input type="text" name="qty" style="font-family: Comic Sans MS" size="30"/></td></tr>'
        context= {'data1':output}
        return render(request, 'SaleProduct.html', context)


def SaleProductAction(request):
    if request.method == 'POST':
        pid = request.POST.get('pid', False)
        price = request.POST.get('price', False)
        qty = request.POST.get('qty', False)
        user = ""
        with open("session.txt", "r") as file:
            for line in file:
                user = line.strip('\n')
        file.close()
        amount = float(qty) * float(price)
        output = '<tr><td><font size="" color="black">Product&nbsp;ID</b></td><td><input type="text" name="pid" style="font-family: Comic Sans MS" size="30" value='+pid+' readonly/></td></tr>'
        output += '<tr><td><font size="" color="black">Product&nbsp;Price</b></td><td><input type="text" name="price" style="font-family: Comic Sans MS" size="20" value='+price+' readonly/></td></tr>'
        output+='<tr><td><font size="" color="black">Quantity</b></td><td><input type="text" name="qty" style="font-family: Comic Sans MS" size="20" value='+str(qty)+' readonly/></td></tr>'
        output+='<tr><td><font size="" color="black">Amount</b></td><td><input type="text" name="amt" style="font-family: Comic Sans MS" size="30" value='+str(amount)+' readonly/></td></tr>'
        output+='<tr><td><font size="" color="black">Username</b></td><td><input type="text" name="user" style="font-family: Comic Sans MS" size="30" value='+str(user)+' readonly/></td></tr>'
        context= {'data1':output}
        return render(request, 'Payment.html', context)


def ViewTransactions(request):
    if request.method == 'GET':
        output = ''
        output+='<table border=1 align=center width=100%><tr><th>Purchaser Name</th><th>Product ID</th><th>Price</th><th>Quantity</th>'
        output+='<th>Amount</th><th>Card No</th><th>CVV No</th><th>Purchase Date</th></tr>'
        con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = '', database = 'inventoryDB',charset='utf8')
        with con:
            cur = con.cursor()
            cur.execute("select * FROM customer_order")
            rows = cur.fetchall()
            for row in rows:
                output+='<tr>'
                output+='<td><font size="" color="black">'+row[0]+'</td><td><font size="" color="black">'+row[1]+'</td><td><font size="" color="black">'+str(row[2])+'</td><td><font size="" color="black">'+row[3]+'</td><td><font size="" color="black">'+row[4]+'</td>'
                output+='<td><font size="" color="black">'+row[5]+'</td><td><font size="" color="black">'+row[6]+'</td><td><font size="" color="black">'+str(row[7])+'</td>'
                output+='</tr>'
        #print(output)        
        context= {'data':output}
        return render(request, 'ViewTransaction.html', context)

def ViewUsers(request):
    if request.method == 'GET':
        output = ''
        output+='<table border=1 align=center width=100%><tr><th>Username</th><th>Password</th><th>Contact No</th>'
        output+='<th>Email ID</th><th>Address</th></tr>'
        con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = '', database = 'inventoryDB',charset='utf8')
        with con:
            cur = con.cursor()
            cur.execute("select * FROM register")
            rows = cur.fetchall()
            for row in rows:
                output+='<tr>'
                output+='<td><font size="" color="black">'+row[0]+'</td><td><font size="" color="black">'+row[1]+'</td><td><font size="" color="black">'+str(row[2])+'</td><td><font size="" color="black">'+row[3]+'</td><td><font size="" color="black">'+row[4]+'</td>'
                output+='</tr>'
        #print(output)        
        context= {'data':output}
        return render(request, 'ViewTransaction.html', context)    

def PaymentAction(request):
    if request.method == 'POST':
        pid = request.POST.get('pid', False)
        price = request.POST.get('price', False)
        qty = request.POST.get('qty', False)
        amt = request.POST.get('amt', False)
        user = request.POST.get('user', False)
        card = request.POST.get('card', False)
        cvv = request.POST.get('cvv', False)
        now = datetime.datetime.now()
        current_time = now.strftime("%Y-%m-%d %H:%M:%S")
        db_connection = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = '', database = 'inventoryDB',charset='utf8')
        db_cursor = db_connection.cursor()
        student_sql_query = "INSERT INTO customer_order(purchaser_name,product_id,price,qty,amount,cardno,cvv,purchase_date) VALUES('"+user+"','"+pid+"','"+price+"','"+qty+"','"+amt+"','"+card+"','"+cvv+"','"+str(current_time)+"')"
        db_cursor.execute(student_sql_query)
        db_connection.commit()
        print(db_cursor.rowcount, "Record Inserted")
        if db_cursor.rowcount == 1:
            context= {'data':'Order Confirmed'}
            return render(request, 'UserScreen.html', context)
        else:
            context= {'data':'Error in confirming order'}
            return render(request, 'UserScreen.html', context)


def index(request):
    if request.method == 'GET':
       return render(request, 'index.html', {})

def Login(request):
    if request.method == 'GET':
       return render(request, 'Login.html', {})

def Register(request):
    if request.method == 'GET':
       return render(request, 'Register.html', {})   


def Signup(request):
    if request.method == 'POST':
      username = request.POST.get('username', False)
      password = request.POST.get('password', False)
      contact = request.POST.get('contact', False)
      email = request.POST.get('email', False)
      address = request.POST.get('address', False)
      db_connection = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = '', database = 'inventoryDB',charset='utf8')
      db_cursor = db_connection.cursor()
      student_sql_query = "INSERT INTO register(username,password,contact,email,address) VALUES('"+username+"','"+password+"','"+contact+"','"+email+"','"+address+"')"
      db_cursor.execute(student_sql_query)
      db_connection.commit()
      print(db_cursor.rowcount, "Record Inserted")
      if db_cursor.rowcount == 1:
       context= {'data':'Signup Process Completed'}
       return render(request, 'Register.html', context)
      else:
       context= {'data':'Error in signup process'}
       return render(request, 'Register.html', context)    
        
def UserLogin(request):
    if request.method == 'POST':
        username = request.POST.get('username', False)
        password = request.POST.get('password', False)
        utype = 'none'
        if username == 'admin' and password == 'admin':
            utype = 'Admin'
        else:
            con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = '', database = 'inventoryDB',charset='utf8')
            with con:
                cur = con.cursor()
                cur.execute("select * FROM register")
                rows = cur.fetchall()
                for row in rows:
                    if row[0] == username and row[1] == password:
                        utype = 'User'
                        break
        if utype == 'Admin':
            file = open('session.txt','w')
            file.write(username)
            file.close()
            context= {'data':'welcome '+username}
            return render(request, 'AdminScreen.html', context)
        if utype == 'User':
            file = open('session.txt','w')
            file.write(username)
            file.close()
            context= {'data':'welcome '+username}
            return render(request, 'UserScreen.html', context)
        if utype == 'none':
            context= {'data':'Invalid login details'}
            return render(request, 'Login.html', context)        
        
        
