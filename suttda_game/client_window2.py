from PyQt5 import uic
from PyQt5 import QtGui
from PyQt5 import QtWidgets
from PyQt5.QtCore import QTimer
import sys
import client2
import pickle
import math
import playsound
from threading import Timer
import pymysql
import use_DB2

# 로그인화면, 게임 창 화면 폼을 불러옴.
form_class = uic.loadUiType("suttda_clinet_windowui2.ui")[0]
form_class_login = uic.loadUiType("sutdda_clinet_login.ui")[0]
form_class_show_your_card = uic.loadUiType("show_your_card.ui")[0]
#signup_class = uic.loadUiType("suttda_signup.ui")[0]

# 로그인 화면을 위한 클래스
class Login_class(QtWidgets.QMainWindow, form_class_login):
    def __init__(self):
        super().__init__()
        self.setupUi(self)


        #제목
        self.setWindowTitle('섯다!')

        # 닉네임 창, 접속 버튼
        self.user_id_1.returnPressed.connect(self.login_)
        self.wjqthr.clicked.connect(self.login_)
        self.ghldnjsrkdlq.clicked.connect(self.signup)

        self.show()


    def login_(self):
        #닉네임 창에 입력한 메시지
        login_nickname = self.user_id_1.text()
        login_pwd = self.user_pwd_1.text()
        if login_nickname: #입력된 메시지가 있으면
            #윈도우 클래스 객체 인스턴스를 만든다.

            # db 서버에 먼저 찾는걸 시도
            try:
                db1 = use_DB2.connectDB()
                info_dict = use_DB2.find1(db1, login_nickname)

                if type(info_dict) == dict:  # 일단 아이디가 있어, 비밀번호 확인
                    if info_dict['user_pwd'] == login_pwd:

                        this_money = info_dict['user_money']

                        #print('성공')
                        # 끝나고 처리

                        self.app2 = Client_Window_Class(login_nickname, this_money)

                        if self.app2.check_connect():  # 클라이언트가 서버에 연결되었는지를 확인. 연결되었다면
                            self.app2.show()  # 게임화면 창 show
                            self.hide()  # 로그인 창은 숨기기

                        else:  # 클라이언트가 서버에 연결되지 않았다면 에러 메시지.
                            self.error_message(2)

                    else:
                        self.error_message(4)

                else:  # 아이디 잘못했네 아이디도 없어
                    self.error_message(4)

            except:
                self.error_message(3)

        else: #메시지가 없다면 아무 글자도 없다는 에러 메시지
            self.error_message(1)

    def signup(self):
        self.sign_up = use_DB2.SignUp()

    def error_message(self, key):
        self.dialog = QtWidgets.QDialog()
        self.dialog.setWindowTitle('No!')
        self.dialog.resize(300, 200)

        msg1 = '안돼..'
        if key == 1:
            msg1 = '닉네임을 입력해.'
        if key == 2:
            msg1 = '서버가 꺼져있음.'
        if key == 3:
            msg1 = 'db 서버가 꺼져있음'
        if key == 4:
            msg1 = '아이디 혹은 비밀번호를 확인하세요'

        self.msg = QtWidgets.QLabel(msg1, self.dialog)
        self.msg.move(100, 50)
        self.btnDialog = QtWidgets.QPushButton("확인", self.dialog)
        self.btnDialog.move(100, 100)
        self.btnDialog.clicked.connect(self.dialog_close)
        self.dialog.show()

    #에러 메시지창 닫기.
    def dialog_close(self):
        self.dialog.close()



#게임 화면 창.
class Client_Window_Class(QtWidgets.QMainWindow, form_class):
    def __init__(self , nickname, user_money):
        super().__init__()
        self.setupUi(self)

        #클라이언트 소켓 인스턴스 생성
        self.c = client2.ClinetSocket(self, nickname, user_money)

        #창 제목
        self.setWindowTitle('섯다!')

        self.ghkrdls.clicked.connect(self.send_msg) # 대화창 확인 버튼
        self.qhsofeoghk.returnPressed.connect(self.send_msg) # 내가 쓰는 대화 메시지 창

        self.wnsql.clicked.connect(self.ready_for_click)  # 준비 버튼
        self.rpdlatlwkr.clicked.connect(self.game_start_for_click) # 게임 시작 버튼
        self.rpdlatlwkr.setEnabled(False)  # 게임 시작 버튼 활성화안되게. 방장만 활성화되게.

        self.your_name.setText('ID : ' + nickname)

        self.Qld.clicked.connect(self.click_game_Qld)       # 삥 버튼
        self.znjxj.clicked.connect(self.click_game_znjxj)   # 쿼터 버튼
        self.gkvm.clicked.connect(self.click_game_gkvm)     # 하프 버튼
        self.zhf.clicked.connect(self.click_game_call)      # 콜 버튼
        self.ekdl.clicked.connect(self.click_game_die)      # 다이 버튼

        self.whrqhqhrl.clicked.connect(self.jokbo_show)     # 족보 보기

        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.renewing)
        #상태를 갱신.

        self.timer2 = QTimer()
        self.timer2.setInterval(1000)
        self.timer2.timeout.connect(self.renewing2)
        #누가 입장했을때 상태를 갱신.

        self.timer2.start()

    def choose_your_card_set(self):
        self.dialog = QtWidgets.QDialog()
        self.dialog.setWindowTitle('No!')
        self.dialog.resize(800, 500)
        self.dialog_label1 = QtWidgets.QLabel('어떤 패로 낼꺼야?', self.dialog)
        self.dialog_label1.move(200, 30)
        self.dialog_label1.setFont(QtGui.QFont('궁서', 13))
        self.img1 = QtWidgets.QLabel('', self.dialog)
        self.img1.setPixmap(QtGui.QPixmap(self.c.image_basic_path2))
        self.img1.move(20, 100)
        self.img2 = QtWidgets.QLabel('', self.dialog)
        self.img2.setPixmap(QtGui.QPixmap(self.c.image_basic_path3))
        self.img2.move(140, 100)
        self.dialog_button1 = QtWidgets.QRadioButton('', self.dialog)
        self.dialog_button1.move(140, 400)
        self.dialog_button1.setChecked(True)
        self.img3 = QtWidgets.QLabel('', self.dialog)
        self.img3.setPixmap(QtGui.QPixmap(self.c.image_basic_path3))
        self.img3.move(280, 100)
        self.img4 = QtWidgets.QLabel('', self.dialog)
        self.img4.setPixmap(QtGui.QPixmap(self.c.image_basic_path4))
        self.img4.move(400, 100)
        self.dialog_button2 = QtWidgets.QRadioButton('', self.dialog)
        self.dialog_button2.move(400, 400)
        self.img5 = QtWidgets.QLabel('', self.dialog)
        self.img5.setPixmap(QtGui.QPixmap(self.c.image_basic_path2))
        self.img5.move(540, 100)
        self.img6 = QtWidgets.QLabel('', self.dialog)
        self.img6.setPixmap(QtGui.QPixmap(self.c.image_basic_path4))
        self.img6.move(660, 100)
        self.dialog_button3 = QtWidgets.QRadioButton('', self.dialog)
        self.dialog_button3.move(660, 400)


        self.dialog_end_button = QtWidgets.QPushButton('확인', self.dialog)
        self.dialog_end_button.move(380, 450)
        self.dialog_end_button.clicked.connect(self.dialog_close3)

        self.dialog.show()

    def dialog_close3(self):
        if self.c.what_card_you_s2_tag == 0:
            self.c.what_card_you_s2_tag =1

            if self.dialog_button1.isChecked():
                self.c.what_card_you_s2 = 1
            elif self.dialog_button2.isChecked():
                self.c.what_card_you_s2 = 2
                self.c.image_basic_path2 = self.c.image_basic_path3
                self.c.image_basic_path3 = self.c.image_basic_path4
            elif self.dialog_button3.isChecked():
                self.c.what_card_you_s2 = 3
                self.c.image_basic_path3 = self.c.image_basic_path4

            self.c.image_basic_path4 = self.c.image_basic_path

            msg = [12, [self.c.your_position_num, self.c.what_card_you_s2]]
            msg_pickle = pickle.dumps(msg)

            self.c.send_pickle(msg_pickle)
        self.dialog.close()


    def what_card_you_show(self):
        self.dialog = QtWidgets.QDialog()
        self.dialog.setWindowTitle('No!')
        self.dialog.resize(600, 400)
        self.dialog_label1 = QtWidgets.QLabel('보여줄 패를 고르세요.', self.dialog)
        self.dialog_label1.setFont(QtGui.QFont('궁서', 13))
        self.dialog_label1.move(130, 30)
        self.img1 = QtWidgets.QLabel('', self.dialog)
        self.img1.setPixmap(QtGui.QPixmap(self.c.image_basic_path2))
        self.img1.move(150, 100)
        self.dialog_button1 = QtWidgets.QRadioButton('', self.dialog)
        self.dialog_button1.move(200, 330)
        self.dialog_button1.setChecked(True)
        self.img2 = QtWidgets.QLabel('', self.dialog)
        self.img2.setPixmap(QtGui.QPixmap(self.c.image_basic_path3))
        self.img2.move(350, 100)
        self.dialog_button2 = QtWidgets.QRadioButton('', self.dialog)
        self.dialog_button2.move(400, 330)


        self.dialog_end_button = QtWidgets.QPushButton('확인', self.dialog)
        self.dialog_end_button.move(250, 360)
        self.dialog_end_button.clicked.connect(self.dialog_close2)

        self.dialog.show()


    def dialog_close2(self):
        if self.c.what_card_you_s1_tag == 0:
            self.c.what_card_you_s1_tag = 1
            if self.dialog_button1.isChecked():
                self.c.what_card_you_s = 1
            elif self.dialog_button2.isChecked():
                self.c.what_card_you_s = 2

            msg = [11, [self.c.your_position_num, self.c.what_card_you_s]]
            msg_pickle = pickle.dumps(msg)

            self.c.send_pickle(msg_pickle)

        self.dialog.close()


    def renewing2(self):
        self.eoghkckd.scrollToBottom()
        if self.c.game_ready_state >=2:
            if self.c.now_show_msg[:8] == '[SYSTEM]':
                self.tkdxoaptlwl.setText(self.c.now_show_msg[9:])
                if not self.c.now_show_msg[9:] == self.c.save_msg:
                    playsound.playsound('effect/2.wav')
                    self.c.save_msg = self.c.now_show_msg[9:]

        if self.c.game_ready_state ==0:
            self.wnsql.setText('준비')
            self.rpdlatlwkr.setEnabled(False)
            self.Qld.setText('삥')
            self.znjxj.setText('쿼터')
            self.gkvm.setText('하프')
            self.zhf.setText('콜')

        #판 초기 상태
        jj=0
        if self.c.renew_pan_state == 0:
            for nick in self.c.member_list_list_style:
                face_path = self.c.image_basic_path_face + str(jj) + '.png'
                face_path_ready = self.c.image_basic_path_face + str(jj) + '_ready.png'
                if jj == 0:
                    self.user_1_name.setText(nick)
                    self.user_1_money.setText(str(self.c.player_money_client[jj]))
                    if self.c.member_state_list[nick] == 0 or self.c.member_state_list[nick] == 2 or self.c.member_state_list[nick] == 3:
                        self.user_1_face.setPixmap(QtGui.QPixmap(face_path))
                    elif self.c.member_state_list[nick] == 1:
                        self.user_1_face.setPixmap(QtGui.QPixmap(face_path_ready))

                elif jj == 1:
                    self.user_2_name.setText(nick)
                    self.user_2_money.setText(str(self.c.player_money_client[jj]))
                    if self.c.member_state_list[nick] == 0 or self.c.member_state_list[nick] == 2 or self.c.member_state_list[nick] == 3:
                        self.user_2_face.setPixmap(QtGui.QPixmap(face_path))
                    elif self.c.member_state_list[nick] == 1:
                        self.user_2_face.setPixmap(QtGui.QPixmap(face_path_ready))
                elif jj == 2:
                    self.user_3_name.setText(nick)
                    self.user_3_money.setText(str(self.c.player_money_client[jj]))
                    if self.c.member_state_list[nick] == 0 or self.c.member_state_list[nick] == 2 or self.c.member_state_list[nick] == 3:
                        self.user_3_face.setPixmap(QtGui.QPixmap(face_path))
                    elif self.c.member_state_list[nick] == 1:
                        self.user_3_face.setPixmap(QtGui.QPixmap(face_path_ready))
                elif jj == 3:
                    self.user_4_name.setText(nick)
                    self.user_4_money.setText(str(self.c.player_money_client[jj]))
                    if self.c.member_state_list[nick] == 0 or self.c.member_state_list[nick] == 2 or self.c.member_state_list[nick] == 3:
                        self.user_4_face.setPixmap(QtGui.QPixmap(face_path))
                    elif self.c.member_state_list[nick] == 1:
                        self.user_4_face.setPixmap(QtGui.QPixmap(face_path_ready))
                jj += 1

        if self.c.renew_pan_state == 2:

            self.Qld.setText('삥(-' + str(self.c.batting_money + 1) + ')')
            self.znjxj.setText('쿼터(-' + str(math.floor(self.c.batting_money * 1.5)) + ')')
            self.gkvm.setText('하프(-' + str(self.c.batting_money * 2) + ')')
            self.zhf.setText('콜(-' + str(self.c.batting_money) + ')')


            if self.c.game_ready_state == 4: #승부 보는 상태니까
                image_card_path_ = 'images/'
                for i in range(len(self.c.member_list_list_style)):
                    if i == 0 and self.c.live_or_die_all[i] != 2:
                        self.user_1_card_1.setPixmap(QtGui.QPixmap(image_card_path_ + str(self.c.this_game_card[i][0]) + '.png'))
                        self.user_1_card_2.setPixmap(QtGui.QPixmap(image_card_path_ + str(self.c.this_game_card[i][1]) + '.png'))
                        self.user_1_card_3.setPixmap(QtGui.QPixmap(self.c.image_basic_path))
                    elif i == 1 and self.c.live_or_die_all[i] != 2:
                        self.user_2_card_1.setPixmap(QtGui.QPixmap(image_card_path_ + str(self.c.this_game_card[i][0]) + '.png'))
                        self.user_2_card_2.setPixmap(QtGui.QPixmap(image_card_path_ + str(self.c.this_game_card[i][1]) + '.png'))
                        self.user_2_card_3.setPixmap(QtGui.QPixmap(self.c.image_basic_path))
                    elif i == 2 and self.c.live_or_die_all[i] != 2:
                        self.user_3_card_1.setPixmap(QtGui.QPixmap(image_card_path_ + str(self.c.this_game_card[i][0]) + '.png'))
                        self.user_3_card_2.setPixmap(QtGui.QPixmap(image_card_path_ + str(self.c.this_game_card[i][1]) + '.png'))
                        self.user_3_card_3.setPixmap(QtGui.QPixmap(self.c.image_basic_path))
                    elif i == 3 and self.c.live_or_die_all[i] != 2:
                        self.user_4_card_1.setPixmap(QtGui.QPixmap(image_card_path_ + str(self.c.this_game_card[i][0]) + '.png'))
                        self.user_4_card_2.setPixmap(QtGui.QPixmap(image_card_path_ + str(self.c.this_game_card[i][1]) + '.png'))
                        self.user_4_card_3.setPixmap(QtGui.QPixmap(self.c.image_basic_path))

            elif self.c.game_ready_state == 2:  #게임 중 상태
                if self.c.phase == 1:
                    self.what_card_you_show()
                    self.c.phase = 2

                if self.c.phase == 5:
                    if self.c.you_live_or_die != 2:
                        self.choose_your_card_set()
                    else:
                        msg = [12, [self.c.your_position_num, 1]]
                        msg_pickle = pickle.dumps(msg)

                        self.c.send_pickle(msg_pickle)

                    self.c.phase = 6

                #세번째 카드 뒷면 보이기
                if self.c.phase == 4:
                    for i in range(len(self.c.member_list_list_style)):
                        if i==0:
                            self.user_1_card_3.setPixmap(QtGui.QPixmap(self.c.image_basic_path))
                        elif i==1:
                            self.user_2_card_3.setPixmap(QtGui.QPixmap(self.c.image_basic_path))
                        elif i==2:
                            self.user_3_card_3.setPixmap(QtGui.QPixmap(self.c.image_basic_path))
                        elif i==3:
                            self.user_4_card_3.setPixmap(QtGui.QPixmap(self.c.image_basic_path))

                if self.c.your_position_num == 0:
                    self.user_1_card_1.setPixmap(QtGui.QPixmap(self.c.image_basic_path2))
                    self.user_1_card_2.setPixmap(QtGui.QPixmap(self.c.image_basic_path3))
                    if self.c.phase == 4:
                        self.user_1_card_3.setPixmap(QtGui.QPixmap(self.c.image_basic_path4))
                    if self.c.phase == 6:
                        self.user_1_card_3.setPixmap(QtGui.QPixmap(self.c.image_basic_path))
                elif self.c.your_position_num == 1:
                    self.user_2_card_1.setPixmap(QtGui.QPixmap(self.c.image_basic_path2))
                    self.user_2_card_2.setPixmap(QtGui.QPixmap(self.c.image_basic_path3))
                    if self.c.phase == 4:
                        self.user_2_card_3.setPixmap(QtGui.QPixmap(self.c.image_basic_path4))
                    if self.c.phase == 6:
                        self.user_2_card_3.setPixmap(QtGui.QPixmap(self.c.image_basic_path))
                elif self.c.your_position_num == 2:
                    self.user_3_card_1.setPixmap(QtGui.QPixmap(self.c.image_basic_path2))
                    self.user_3_card_2.setPixmap(QtGui.QPixmap(self.c.image_basic_path3))
                    if self.c.phase == 4:
                        self.user_3_card_3.setPixmap(QtGui.QPixmap(self.c.image_basic_path4))
                    if self.c.phase == 6:
                        self.user_3_card_3.setPixmap(QtGui.QPixmap(self.c.image_basic_path))
                elif self.c.your_position_num == 3:
                    self.user_4_card_1.setPixmap(QtGui.QPixmap(self.c.image_basic_path2))
                    self.user_4_card_2.setPixmap(QtGui.QPixmap(self.c.image_basic_path3))
                    if self.c.phase == 4:
                        self.user_4_card_3.setPixmap(QtGui.QPixmap(self.c.image_basic_path4))
                    if self.c.phase == 6:
                        self.user_4_card_3.setPixmap(QtGui.QPixmap(self.c.image_basic_path))


                if self.c.phase == 3:
                    #첫번째 카드 다 보이기
                    for i in range(len(self.c.member_list_list_style)):
                        if i==0:
                            self.user_1_card_1.setPixmap(QtGui.QPixmap('images/' + str(self.c.this_game_card[i][0]) + '.png'))
                        elif i==1:
                            self.user_2_card_1.setPixmap(QtGui.QPixmap('images/' + str(self.c.this_game_card[i][0]) + '.png'))
                        elif i==2:
                            self.user_3_card_1.setPixmap(QtGui.QPixmap('images/' + str(self.c.this_game_card[i][0]) + '.png'))
                        elif i==3:
                            self.user_4_card_1.setPixmap(QtGui.QPixmap('images/' + str(self.c.this_game_card[i][0]) + '.png'))

                self.user_1_name.setStyleSheet("Color: black")
                self.user_2_name.setStyleSheet("Color: black")
                self.user_3_name.setStyleSheet("Color: black")
                self.user_4_name.setStyleSheet("Color: black")

                #자기 턴이면 빨간색
                if self.c.now_turn == 0:
                    self.user_1_name.setStyleSheet("Color: red")
                    self.user_1_call_state.setText('')
                elif self.c.now_turn == 1:
                    self.user_2_name.setStyleSheet("Color: red")
                    self.user_2_call_state.setText('')
                elif self.c.now_turn == 2:
                    self.user_3_name.setStyleSheet("Color: red")
                    self.user_3_call_state.setText('')
                elif self.c.now_turn == 3:
                    self.user_4_name.setStyleSheet("Color: red")
                    self.user_4_call_state.setText('')

                for i in range(len(self.c.clients_call_state)):
                    if i==0:
                        val = self.c.clients_call_state[i]
                        if val==1:
                            self.user_1_call_state.setText('삥!')
                        elif val==2:
                            self.user_1_call_state.setText('쿼터!')
                        elif val==3:
                            self.user_1_call_state.setText('하프!')
                        elif val==4:
                            self.user_1_call_state.setText('콜!')
                        elif val==5:
                            self.user_1_call_state.setText('다이!')
                        elif val==0:
                            self.user_1_call_state.setText(' ')

                    elif i==1:
                        val = self.c.clients_call_state[i]
                        if val==1:
                            self.user_2_call_state.setText('삥!')
                        elif val==2:
                            self.user_2_call_state.setText('쿼터!')
                        elif val==3:
                            self.user_2_call_state.setText('하프!')
                        elif val==4:
                            self.user_2_call_state.setText('콜!')
                        elif val==5:
                            self.user_2_call_state.setText('다이!')
                        elif val==0:
                            self.user_2_call_state.setText(' ')

                    elif i==2:
                        val = self.c.clients_call_state[i]
                        if val==1:
                            self.user_3_call_state.setText('삥!')
                        elif val==2:
                            self.user_3_call_state.setText('쿼터!')
                        elif val==3:
                            self.user_3_call_state.setText('하프!')
                        elif val==4:
                            self.user_3_call_state.setText('콜!')
                        elif val==5:
                            self.user_3_call_state.setText('다이!')
                        elif val==0:
                            self.user_3_call_state.setText(' ')


                    elif i==3:
                        val = self.c.clients_call_state[i]
                        if val==1:
                            self.user_4_call_state.setText('삥!')
                        elif val==2:
                            self.user_4_call_state.setText('쿼터!')
                        elif val==3:
                            self.user_4_call_state.setText('하프!')
                        elif val==4:
                            self.user_4_call_state.setText('콜!')
                        elif val==5:
                            self.user_4_call_state.setText('다이!')
                        elif val==0:
                            self.user_4_call_state.setText(' ')

                #레디로 된 얼굴 풀어줄라고
                kj =0
                for nick in self.c.member_list_list_style:
                    face_path = self.c.image_basic_path_face + str(kj) + '.png'
                    face_die_path = self.c.image_basic_path_face + str(kj) + '_die.png'
                    if kj == 0:
                        if self.c.live_or_die_all[kj] == 2:
                            self.user_1_face.setPixmap(QtGui.QPixmap(face_die_path))
                            self.user_1_call_state.setText('다이!')
                        else:
                            self.user_1_face.setPixmap(QtGui.QPixmap(face_path))
                    elif kj == 1:
                        if self.c.live_or_die_all[kj] == 2:
                            self.user_2_face.setPixmap(QtGui.QPixmap(face_die_path))
                            self.user_2_call_state.setText('다이!')
                        else:
                            self.user_2_face.setPixmap(QtGui.QPixmap(face_path))
                    elif kj == 2:
                        if self.c.live_or_die_all[kj] == 2:
                            self.user_3_face.setPixmap(QtGui.QPixmap(face_die_path))
                            self.user_3_call_state.setText('다이!')
                        else:
                            self.user_3_face.setPixmap(QtGui.QPixmap(face_path))
                    elif kj == 3:
                        if self.c.live_or_die_all[kj] == 2:
                            self.user_4_face.setPixmap(QtGui.QPixmap(face_die_path))
                            self.user_4_call_state.setText('다이!')
                        else:
                            self.user_4_face.setPixmap(QtGui.QPixmap(face_path))
                    kj+=1

        if self.c.renew_pan_state == 1:
            self.timer.start() #한번만 해야되니까
            self.c.renew_pan_state = 2
            self.user_1_name.setText('')
            self.user_2_name.setText('')
            self.user_3_name.setText('')
            self.user_4_name.setText('')
            self.user_1_card_1.setText('')
            self.user_1_card_2.setText('')
            self.user_1_card_3.setText('')
            self.user_1_card_3.setPixmap(QtGui.QPixmap('images/0.PNG'))
            self.user_1_call_state.setText('')
            self.user_2_card_1.setText('')
            self.user_2_card_2.setText('')
            self.user_2_card_3.setText('')
            self.user_2_card_3.setPixmap(QtGui.QPixmap('images/0.PNG'))
            self.user_2_call_state.setText('')
            self.user_3_card_1.setText('')
            self.user_3_card_2.setText('')
            self.user_3_card_3.setText('')
            self.user_3_card_3.setPixmap(QtGui.QPixmap('images/0.PNG'))
            self.user_4_card_1.setText('')
            self.user_4_card_2.setText('')
            self.user_4_card_3.setText('')
            self.user_4_card_3.setPixmap(QtGui.QPixmap('images/0.PNG'))
            self.user_1_money.setText('')
            self.user_2_money.setText('')
            self.user_3_money.setText('')
            self.user_4_money.setText('')
            jj = 0
            for nick in self.c.member_list_list_style:
                if jj == 0:
                    self.user_1_name.setText(nick)
                    self.user_1_card_1.setPixmap(QtGui.QPixmap(self.c.image_basic_path))
                    self.user_1_card_2.setPixmap(QtGui.QPixmap(self.c.image_basic_path))
                    self.user_1_money.setText(str(self.c.player_money_client[jj]))
                elif jj == 1:
                    self.user_2_name.setText(nick)
                    self.user_2_card_1.setPixmap(QtGui.QPixmap(self.c.image_basic_path))
                    self.user_2_card_2.setPixmap(QtGui.QPixmap(self.c.image_basic_path))
                    self.user_2_money.setText(str(self.c.player_money_client[jj]))
                elif jj == 2:
                    self.user_3_name.setText(nick)
                    self.user_3_card_1.setPixmap(QtGui.QPixmap(self.c.image_basic_path))
                    self.user_3_card_2.setPixmap(QtGui.QPixmap(self.c.image_basic_path))
                    self.user_3_money.setText(str(self.c.player_money_client[jj]))
                elif jj == 3:
                    self.user_4_name.setText(nick)
                    self.user_4_card_1.setPixmap(QtGui.QPixmap(self.c.image_basic_path))
                    self.user_4_card_2.setPixmap(QtGui.QPixmap(self.c.image_basic_path))
                    self.user_4_money.setText(str(self.c.player_money_client[jj]))
                jj += 1

            self.c.game_ing_state = 1



    def renewing(self):
        j = 0
        for i in self.c.player_money_client:
            if j ==0:
                self.user_1_money.setText(str(i))
            elif j==1:
                self.user_2_money.setText(str(i))
            elif j==2:
                self.user_3_money.setText(str(i))
            elif j==3:
                self.user_4_money.setText(str(i))
            j+=1

        self.vksehs.setText(str(self.c.total_money_client))

    def check_connect(self):
        if self.c.bConnect == True:
            return True
        else:
            return False

    def send_msg(self):
        sendmsg = self.qhsofeoghk.text()
        self.c.send(sendmsg)
        self.qhsofeoghk.clear()

    def update_conversation_window(self, msg):
        self.eoghkckd.addItem(msg)
        self.eoghkckd.scrollToBottom()

    def ready_for_click(self):
        if self.c.game_ready_state == 1:
            self.c.game_ready_state = 0
            self.wnsql.setText('준비')
            msg = [1, '가 준비를 취소하였습니다.']
            msg_pickle = pickle.dumps(msg)
            self.c.send_pickle(msg_pickle)
            self.rpdlatlwkr.setEnabled(False)

        elif self.c.game_ready_state == 0:
            self.c.game_ready_state = 1
            self.wnsql.setText('준비완료')
            msg = [2, '가 준비하였습니다.']
            msg_pickle = pickle.dumps(msg)
            self.c.send_pickle(msg_pickle)
            self.c.get_your_pos()
            if self.c.your_position_num == 0:
                self.rpdlatlwkr.setEnabled(True)

        else:
            self.error_message(1)

    def game_start_for_click(self):
        if self.c.game_ready_state == 1:
            msg = [3, '게임 시작!']
            msg_pickle = pickle.dumps(msg)
            self.c.send_pickle(msg_pickle)

        elif self.c.game_ready_state == 2 or self.c.game_ready_state == 3:
            self.error_message(1)
        elif self.c.game_ready_state == 0:
            self.error_message(2)

    def jokbo_show(self):
        self.dialog = QtWidgets.QDialog()
        self.dialog.setWindowTitle('족보')
        self.dialog.resize(700, 700)

        jokbo_image_path1 = "images/jokbo/jokbo1.png"

        self.jokbo_img1 = QtWidgets.QLabel('', self.dialog)
        self.jokbo_img1.setPixmap(QtGui.QPixmap(jokbo_image_path1))
        self.jokbo_img1.move(50, 20)

        jokbo_label = {1: '삼팔광땡(3광, 8광)', 2: '광땡((1광, 8광), (1광, 3광))', 3: '장땡(10, 10)', 4: '구땡(9, 9)', 5: '팔땡(8, 8)',
                      6: '칠땡(7, 7)', 7: '육땡(6, 6)', 8: '오땡(5, 5)', 9: '사땡(4, 4)', 10: '삼땡(3, 3)',
                      11: '이땡(2, 2)', 12: '일땡(1, 1)', 13: '알리(1, 2)', 14: '독사(1, 4)', 15: '구삥(1, 9)',
                      16: '장삥(1, 10)', 17: '장사(4, 10)', 18: '세륙(4, 6)', 19: '갑오(구끗)', 20: '여덟끗',
                      21: '일곱끗', 22: '여섯끗', 23: '다섯끗', 24: '사끗', 25: '삼끗',
                      26: '두끗', 27: '한끗', 28: '망통(0끗)'}

        jz = 0
        for jokbo_label_key, jokbo_label_name in jokbo_label.items():
            jokbo_label_instance_msg = str(jokbo_label_key) + '등 : ' + jokbo_label_name
            self.jokbo_label_instance = QtWidgets.QLabel(jokbo_label_instance_msg, self.dialog)
            self.jokbo_label_instance.move(450, 20+ jz*20)
            if self.c.your_card_rank == jokbo_label_key:
                font_bold = self.jokbo_label_instance.font()
                font_bold.setBold(True)
                self.jokbo_label_instance.setFont(font_bold)
            jz+= 1

        self.btnDialog = QtWidgets.QPushButton("확인", self.dialog)
        self.btnDialog.move(200, 500)
        self.btnDialog.clicked.connect(self.dialog_close)
        self.dialog.show()



    def click_game_Qld(self):
        if self.c.game_ready_state !=2:
            if self.c.game_ready_state == 3:
                self.error_message(1)
            else:
                self.error_message(3)
        else:
        #서버에서 콜 상태로.
        # 전부 다 콜인 경우 개봉박두. 개봉박두 버튼을 만들던지.
        #콜했을때 메세지 뜨게 하기.
        #플레이어 live die 상태 가지는 배열 하나 더 만들자.
            if self.c.you_live_or_die != 2:
                if self.c.now_turn == self.c.your_position_num:
                    #if self.c.call_state <=1:
                    self.c.you_live_or_die = 1
                    self.c.call_state = 1
                    msgg = [21, [self.c.your_position_num, '', (self.c.batting_money + 1), self.c.call_state]]
                    msgg_pickle = pickle.dumps(msgg)
                    self.c.send_pickle(msgg_pickle)
                    self.c.your_money -= (self.c.batting_money + 1)

                else:
                    self.error_message(5)
            else:
                self.error_message(4)
            # 이미 죽었으면 콜 못하게


    def click_game_znjxj(self):
        if self.c.game_ready_state !=2:
            if self.c.game_ready_state == 3:
                self.error_message(1)
            else:
                self.error_message(3)
        else:
        #서버에서 콜 상태로.
        # 전부 다 콜인 경우 개봉박두. 개봉박두 버튼을 만들던지.
        #콜했을때 메세지 뜨게 하기.
        #플레이어 live die 상태 가지는 배열 하나 더 만들자.
            if self.c.you_live_or_die != 2:
                if self.c.now_turn == self.c.your_position_num:
                    #if self.c.call_state <=2:
                    self.c.you_live_or_die = 1
                    self.c.call_state = 2
                    msgg = [21, [self.c.your_position_num, '', math.floor(self.c.batting_money * 1.5), self.c.call_state]]
                    msgg_pickle = pickle.dumps(msgg)
                    self.c.send_pickle(msgg_pickle)
                    self.c.your_money -= math.floor(self.c.batting_money * 1.5)

                else:
                    self.error_message(5)
            else:
                self.error_message(4)
            # 이미 죽었으면 콜 못하게

    def click_game_gkvm(self):
        if self.c.game_ready_state !=2:
            if self.c.game_ready_state == 3:
                self.error_message(1)
            else:
                self.error_message(3)
        else:
        #서버에서 콜 상태로.
        # 전부 다 콜인 경우 개봉박두. 개봉박두 버튼을 만들던지.
        #콜했을때 메세지 뜨게 하기.
        #플레이어 live die 상태 가지는 배열 하나 더 만들자.
            if self.c.you_live_or_die !=2:
                if self.c.now_turn == self.c.your_position_num:
                    #if self.c.call_state <=3:
                    self.c.you_live_or_die = 1
                    self.c.call_state = 3
                    msgg = [21, [self.c.your_position_num, '', self.c.batting_money * 2, self.c.call_state]]
                    msgg_pickle = pickle.dumps(msgg)
                    self.c.send_pickle(msgg_pickle)
                    self.c.your_money -= (self.c.batting_money * 2)

                else:
                    self.error_message(5)
            else:
                self.error_message(4)
            # 이미 죽었으면 콜 못하게



    def click_game_call(self):
        if self.c.game_ready_state !=2:
            if self.c.game_ready_state == 3:
                self.error_message(1)
            else:
                self.error_message(3)
        else:
        #서버에서 콜 상태로.
        # 전부 다 콜인 경우 개봉박두. 개봉박두 버튼을 만들던지.
        #콜했을때 메세지 뜨게 하기.
        #플레이어 live die 상태 가지는 배열 하나 더 만들자.
            if self.c.you_live_or_die !=2:
                if self.c.now_turn == self.c.your_position_num:
                    self.c.you_live_or_die = 1
                    self.c.call_state = 4
                    msgg = [21, [self.c.your_position_num, '', self.c.batting_money, self.c.call_state]]
                    msgg_pickle = pickle.dumps(msgg)
                    self.c.send_pickle(msgg_pickle)
                    self.c.your_money -= self.c.batting_money

                    # 서버에서 얼만지 받아야하나?
                    if self.c.your_position_num == 0:
                        self.user_1_money.setText(str(self.c.player_money_client[0]))
                    elif self.c.your_position_num == 1:
                        self.user_2_money.setText(str(self.c.player_money_client[1]))
                    elif self.c.your_position_num == 2:
                        self.user_3_money.setText(str(self.c.player_money_client[2]))
                    elif self.c.your_position_num == 3:
                        self.user_4_money.setText(str(self.c.player_money_client[3]))

                else:
                    self.error_message(5)
            else:
                self.error_message(4)
            # 이미 죽었으면 콜 못하게



    def click_game_die(self):
        if self.c.game_ready_state !=2:
            if self.c.game_ready_state == 3:
                self.error_message(1)
            else:
                self.error_message(3)
        else:
            #상태 바꾸기.
            #서버에서 죽은 상태로
            #플레이어 live die 상태 가지는 배열 하나 더 만들자.
            if self.c.you_live_or_die !=2:
                if self.c.now_turn == self.c.your_position_num:
                    self.c.you_live_or_die = 2
                    self.c.call_state = 5
                    msgg = [22, [self.c.your_position_num, '', 0, self.c.call_state]]
                    msgg_pickle = pickle.dumps(msgg)
                    self.c.send_pickle(msgg_pickle)

                else:
                    self.error_message(5)
            else:
                self.error_message(4)
            #다이 상태 처리하기기
            #이미 죽었으면 죽은거 못하게

    def error_message(self, key):
        self.dialog = QtWidgets.QDialog()
        self.dialog.setWindowTitle('No!')
        self.dialog.resize(300, 200)

        msg1 = '안돼..'
        if key == 1:
            msg1 = '게임 중이야!'
        if key == 2:
            msg1 = '준비를 해야지!'
        if key == 3:
            msg1 = '게임 중이 아니야!'
        if key == 4:
            msg1 = '너 죽었어..'
        if key == 5:
            msg1 = '니 차례가 아니야..'
        if key == 6:
            msg1 = '삥 못해'
        if key == 7:
            msg1 = '쿼터 못해'
        if key == 8:
            msg1 = '하프 못해'
        if key == 9:
            msg1 = '콜 못해'

        self.msg = QtWidgets.QLabel(msg1, self.dialog)
        self.msg.move(100, 50)
        self.btnDialog = QtWidgets.QPushButton("확인", self.dialog)
        self.btnDialog.move(100, 100)
        self.btnDialog.clicked.connect(self.dialog_close)
        self.dialog.show()

    def dialog_close(self):
        self.dialog.close()

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    client_login_window = Login_class()

    app.exec_()