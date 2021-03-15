import socket
import threading
import pickle
from PyQt5.QtCore import pyqtSignal, QObject
import time

class ClinetSocket:
    def __init__(self, parent, your_nickname, user_money):
        self.parent = parent
        self.bConnect = False                               #서버와 연결되었는지 확인하기 위한 bool
        self.id = your_nickname                             #너의 닉네임
        self.your_position_num = -1                         #너의 자리
        self.image_basic_path = "images/-1.png"             #카드의 뒷면을 위한 것.
        self.image_basic_path2 = "images/-1.png"            #너의 첫번째 카드를 위한 것.
        self.image_basic_path3 = "images/-1.png"            #너의 두번째 카드를 위한 것.
        self.image_basic_path4 = "images/-1.png"  # 너의 두번째 카드를 위한 것.
        self.image_basic_path5 = "images/-1.png"  # 너의 두번째 카드를 위한 것.
        self.image_basic_path_face = "images/characters/"   #너의 캐릭터 얼굴 이미지를 위한 것.

        self.game_ready_state = 0  #0 이 그냥 상태. 1 이 준비한 상태. 2 가 게임 중 상태. 3이 게임 중인데 너는 게임 아닌 상태. 4가 승부 상태
        self.game_ing_state = 0    #0이 초기 상태. 1이 패 받은 상태
        self.threads = []

        self.connectServer('1xx.xxx.xxx.xxx', 12346)


        self.member_state_list = dict()
        self.member_list_list_style = list()

        self.renew_pan_state = 0
        self.your_card_rank = -1
        self.call_state = 0                                 #1이 삥. 2가 쿼터. 3이 하프. 4가 콜. 5가 다이

        #돈
        self.your_money = user_money
        self.batting_money = 10
        self.player_money_client = list()

        self.player_money_client = []                       # 각 플레이어의 돈
        self.total_money_client = 0                         # 총 걸린 돈
        self.you_live_or_die = 0                            #너가 살았는지 die인지. 2면 죽은 상태야
        self.live_or_die_all = []                           #다른 플레이어까지 모두 살았는지 die인지 정보.
        self.clients_call_state = []

        self.now_turn = -1                                  #지금 누구 차례인지.
        self.now_show_msg = ''
        self.save_msg = ''


        self.phase = 0                  # 0 대기상태, 1,2 패 받고 어떤거 보여줄지 결정. 3, 겜시작, 첫 배팅 4. 세번째 카드 받고 두번째 배팅 5 배팅 다 끝나고 각자 자기 무슨 패 낼지 정하는 상태.    6이 마지막 상태. 내가 패 정하고 남은 나머지 한장 뒷면으로 바꿔주기.
        self.what_card_you_s = -1
        self.what_card_you_s2 = -1
        self.what_card_you_s1_tag = 0  # 두 번 보내는거 방지.
        self.what_card_you_s2_tag = 0   # 두 번 보내는거 방지.

    def __del__(self):
         self.stop()


    def connectServer(self, server_ip, server_port):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            self.client.connect((server_ip, server_port))
        except Exception as e:
            print('error code 101 : ', e )
        else:
            self.bConnect = True
            self.send(self.id)
            t = threading.Thread(target=self.receive, args=(self.client,))
            t.start()

    def stop(self):
        self.bConnect = False
        self.client.close()

    def receive(self, clinet_sock):
        while self.bConnect:
            try:
                recv = clinet_sock.recv(4096)
            except Exception as e:
                print('error code 103 : ', e )
                break
            else:
                try:
                    msg = str(recv, encoding='utf-8')
                    if msg:
                        #시스템 메시지는 중앙에
                        #채팅은 채팅창에
                        if self.game_ready_state ==2 and msg[:8] =='[SYSTEM]':
                            self.now_show_msg = msg
                        elif self.game_ready_state ==4 and msg[:8] =='[SYSTEM]':
                            self.now_show_msg = msg
                        else:
                            self.parent.update_conversation_window(msg)
                except:
                    # 서버로부터 온게 피클이면. 서버로부터 온 상태 명령으로 game_ready_state 상태를 바꿈.
                    pickle_msg = pickle.loads(recv)
                    if pickle_msg[0] == 51:   #게임 시작
                        self.game_ready_state = 2
                        self.member_list_list_style = pickle_msg[1]

                        #게임 시작 부분.
                        if self.game_ready_state ==2:
                            #내가 몇 번인지 알아야되는구나.
                            self.get_your_pos()

                    elif pickle_msg[0] == 52:  #누가 입장하면 갱신
                        self.member_state_list = pickle_msg[2]
                        self.member_list_list_style = pickle_msg[3]
                        self.clients_call_state = pickle_msg[4]
                        self.player_money_client = pickle_msg[5]

                    elif pickle_msg[0] ==53: #게임 중인지 물은 것.
                        self.game_ready_state = 3

                    elif pickle_msg[0] ==61: #니 카드 받아라.
                        self.this_game_card = pickle_msg[1]
                        self.your_card = self.this_game_card[self.your_position_num]
                        self.image_basic_path2 = "images/" + str(self.your_card[0]) + ".png"
                        self.image_basic_path3 = "images/" + str(self.your_card[1]) + ".png"
                        self.image_basic_path4 = "images/" + str(self.your_card[2]) + ".png"
                        self.now_turn = pickle_msg[3]
                        self.total_money_client += (self.batting_money * len(self.member_list_list_style))
                        for i in range(len(self.member_list_list_style)):
                            self.live_or_die_all.append(0)

                        if self.phase==0:
                            self.phase =1

                    elif pickle_msg[0] == 62:  # 니 카드 수정.
                        self.this_game_card = pickle_msg[1]
                        self.your_card = self.this_game_card[self.your_position_num]
                        self.image_basic_path2 = "images/" + str(self.your_card[0]) + ".png"
                        self.image_basic_path3 = "images/" + str(self.your_card[1]) + ".png"
                        self.image_basic_path4 = "images/" + str(self.your_card[2]) + ".png"
                        self.phase = 3

                    elif pickle_msg[0] == 63: #판돈이랑 애들 돈.
                        self.player_money_client = pickle_msg[1][0]
                        self.total_money_client = pickle_msg[1][1]
                        self.live_or_die_all = pickle_msg[4]

                        self.now_turn += 1
                        self.now_turn %= len(self.member_list_list_style)
                        while self.live_or_die_all[self.now_turn] !=0:
                            self.now_turn += 1
                            self.now_turn %= len(self.member_list_list_style)

                        ## 게임 중인 애들만 개수 쳐야되는데?
                        self.batting_money = pickle_msg[2]
                        self.call_state = pickle_msg[3]
                        self.clients_call_state = pickle_msg[5]


                    elif pickle_msg[0] == 64: #판 초기화
                        self.renew_pan_state = 1
                        self.player_money_client = pickle_msg[2]


                    elif pickle_msg[0] == 71:  #승부보는 상황
                        self.player_money_client = pickle_msg[1][0]
                        self.total_money_client = pickle_msg[1][1]
                        self.live_or_die_all = pickle_msg[4]

                        ## 게임 중인 애들만 개수 쳐야되는데?
                        self.batting_money = pickle_msg[2]
                        self.call_state = pickle_msg[3]
                        self.clients_call_state = pickle_msg[5]
                        self.this_game_card = pickle_msg[6]

                        #time.sleep(2)
                        if self.phase ==3:
                            self.now_turn += 1
                            self.now_turn %= len(self.member_list_list_style)
                            while self.live_or_die_all[self.now_turn] != 0:
                                self.now_turn += 1
                                self.now_turn %= len(self.member_list_list_style)
                            self.phase = 4

                    elif pickle_msg[0] == 72:  #77에 이어서 승부보는 상황
                        self.game_ready_state = 4

                        self.player_money_client = pickle_msg[1][0]
                        self.total_money_client = pickle_msg[1][1]
                        self.live_or_die_all = pickle_msg[4]

                        ## 게임 중인 애들만 개수 쳐야되는데?
                        self.batting_money = pickle_msg[2]
                        self.call_state = pickle_msg[3]
                        self.clients_call_state = pickle_msg[5]

                    #겜 종료. 다 초기화 시켜주기
                    elif pickle_msg[0] ==73:
                        self.reroll()

                    #무승부의 경우

                    elif pickle_msg[0] == 74:
                        self.phase = 5

    #기본 send
    def send(self, msg):
        if not self.bConnect:
            return

        try:
            self.client.send(msg.encode())
        except Exception as e:
            print('error code 104 : ', e)

    #pickle send
    def send_pickle(self, msg):
        if not self.bConnect:
            return

        try:
            self.client.send(msg)
        except Exception as e:
            print('error code 105 : ', e)

    #너의 자리 정해주기
    def get_your_pos(self):
        index = 0
        for value_nickname in self.member_list_list_style:
            if value_nickname == self.id:  # 닉네임이 아니라 포트 번호가 같은걸로 해야된다. 닉네임은 중복 가능.
                self.your_position_num = index

            index+=1

    def reroll(self):
        self.your_card_rank = -1
        self.batting_money = 10
        self.call_state = 0  # 1이 삥. 2가 쿼터. 3이 하프. 4가 콜. 5가 다이
        self.you_live_or_die = 0
        self.game_ready_state = 0  # 0 이 그냥 상태. 1 이 준비한 상태. 2 가 게임 중 상태. 3이 게임 중인데 너는 게임 아닌 상태. 4가 승부 상태
        self.game_ing_state = 0  # 0이 초기 상태. 1이 패 받은 상태
        self.renew_pan_state = 0
        self.your_money = self.player_money_client[self.your_position_num]
        self.now_show_msg = ''
        self.live_or_die_all = []
        self.clients_call_state = []
        self.phase = 0
        self.what_card_you_s = -1
        self.what_card_you_s2 = -1
        self.what_card_you_s1_tag = 0
        self.what_card_you_s2_tag = 0







