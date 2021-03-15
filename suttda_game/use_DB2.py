from PyQt5 import uic
from PyQt5 import QtWidgets
import sys

import pymysql


def connectDB():
    db1 = pymysql.connect(
        user='noroot',
        passwd='122333',
        host='1xx.xxx.xxx.xxx',
        db='suttda_member',
        charset='euckr'
    )

    return db1

def connectDB_local():
    db1 = pymysql.connect(
        user='noroot',
        passwd='122333',
        host='1xx.xxx.xxx.xxx',
        db='suttda_member',
        charset='euckr'
    )

    return db1

def find1(db1, text):
    text = '\'' + text + '\''

    #print(text)
    cursor = db1.cursor(pymysql.cursors.DictCursor)

    sql3 = "SELECT * FROM user_info where user_id=" + text + ";"
    cursor.execute(sql3)
    result3 = cursor.fetchall()

    #print(result3)
    try:
        dict1 = result3[0]
        #print(dict1)
        money = dict1['user_money']
        #print(money)

        return dict1
    except:
        #print('no!')
        return None

def update_money1(db1, text, money1):
    text = '\'' + text + '\''

    cursor = db1.cursor(pymysql.cursors.DictCursor)

    sql3 = "UPDATE user_info set user_money=" + str(money1) + " where user_id=" + text + ";"
    cursor.execute(sql3)
    db1.commit()


signup_class = uic.loadUiType("suttda_signup.ui")[0]

class SignUp(QtWidgets.QMainWindow, signup_class):
    def __init__(self):
        super().__init__()  #부모 클래스의 init을 하겠다.
        self.setupUi(self)

        self.setWindowTitle('회원 가입')

        self.show()

        self.ghkrdls.clicked.connect(self.ok)
        self.cnlth.clicked.connect(self.exit)

    def connectDB(self):
        db1 = pymysql.connect(
            user='noroot',    #root2 로 하면 될듯. root는 로컬에서만 접근 가능. 안된대.
            passwd='122333',
            host = '1xx.xxx.xxx.xxx',
            db='suttda_member',
            charset='euckr'
        )


        return db1


    def ok(self):
        user_id = self.user_id.text()
        user_pwd = self.user_pwd.text()
        user_pwd2 = self.user_pwd2.text()

        if user_id == '':
            self.error_message(4)
        elif user_pwd == '' or user_pwd2 == '':
            self.error_message(5)
        elif user_pwd != user_pwd2:
            self.error_message(1)
        else:
            try:
                db1 = self.connectDB()

                #print(1)

                cursor = db1.cursor(pymysql.cursors.DictCursor)

                user_id = '\'' + user_id + '\''
                user_pwd = '\'' + user_pwd + '\''

                #print(user_id)
                #print(user_pwd)

                sql2 = "INSERT into user_info(user_id, user_pwd) VALUES(" + user_id + ", " +  user_pwd + ");"
                cursor.execute(sql2)
                db1.commit()
                #result2 = cursor.fetchall()

                self.error_message(3)

            except:
                self.error_message(2)

    def exit(self):
        self.close()

    def exit2(self):
        self.error_msg.close()

    def error_message(self, key):
        self.error_msg = QtWidgets.QDialog()
        if key != 3:
            self.error_msg.setWindowTitle('No!')
        else:
            self.error_msg.setWindowTitle('Great!')

        self.error_msg.resize(400,200)

        if key == 1:
            self.msg = QtWidgets.QLabel('비밀번호가 불일치', self.error_msg)
        elif key == 2:
            self.msg = QtWidgets.QLabel('등록 실패(중복된 이름 혹은 서버 오류)', self.error_msg)
        elif key == 3:
            self.msg = QtWidgets.QLabel('등록 성공!', self.error_msg)
        elif key == 4:
            self.msg = QtWidgets.QLabel('아이디를 입력해주세요', self.error_msg)
        elif key == 5:
            self.msg = QtWidgets.QLabel('비밀번호를 입력해주세요', self.error_msg)
        self.msg.move(90, 70)

        self.btn = QtWidgets.QPushButton('확인', self.error_msg)
        self.btn.clicked.connect(self.exit2)
        self.btn.move(100,130)

        self.error_msg.show()

        if key==3:
            self.close()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    signup = SignUp()

    app.exec_()