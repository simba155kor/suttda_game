from PyQt5 import QtWidgets
from PyQt5 import uic


import pymysql

db1 = pymysql.connect(
    user='root',
    passwd='aktkdaktkd1@',
    host='127.0.0.1',
    db='suttda_member',
    charset='utf8'
)

cursor = db1.cursor(pymysql.cursors.DictCursor)

sql = "SELECT * FROM user_info;"
cursor.execute(sql)
result = cursor.fetchall()

aa = '\'ALb\''
bb = '\'12346\''

#sql21 = "INSERT into user_info(user_id, user_pwd) VALUES('ALpha', '12345');"
sql2 = "INSERT into user_info(user_id, user_pwd) VALUES(" + aa + ", " + bb + ");"
#print(sql21)
print(sql2)
cursor.execute(sql2)
db1.commit()
result2 = cursor.fetchall()

sql3 = "SELECT * FROM user_info;"
cursor.execute(sql3)
result3 = cursor.fetchall()

# sql4 = "DELETE FROM user_info WHERE user_money >= 300;"
# cursor.execute(sql4)
# db1.commit()
# result4 = cursor.fetchall()

print(result)
# print(result2)
print(result3)
#print(result4)

#mysql 서버가 꺼져있는데도 가능해???? mysql 서버 지금 켜있나?
# 서비스에서 실행, 중지, 종료 해야되네