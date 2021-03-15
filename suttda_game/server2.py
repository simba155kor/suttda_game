import socket
import threading
import pickle
import game_tool2
import time
import random
import use_DB2

class ServerSocket:
    def __init__(self):
        self.bListen = False
        self.clients = []
        self.ip = []
        self.threads = []
        self.nickname_list = list()
        self.nickname = dict()
        self.nickname_state = dict()
        #0 은 준비 안된 상태. 1은 준비한 상태. 2는 게임 중인 상태. 3은 게임중인데 너는 게임 아닌 상태.
        self.live_or_die = []  # 0은 초기 상태. 1은 콜 상태. 2는 다이 상태.
        self.playing_state_server = 0  #도중 입장을 위해 겜 시작 중인지 아닌지. 1이 겜중인거 0이 겜 안하고있는거.
        self.random_start = -1
        self.batting_money_server = 10  #기본 배팅금
        self.server_call_state = 0      #제일 큰 배팅이 뭐였는지. 1이 삥, 2가 쿼터, 3이 하프
        self.player_money = list()
        self.game_num = 1
        self.total_money = 0
        self.clients_call_state = list()

        self.game_mode = 3 # 몇 장 모드인지.
        self.server_phase = 0      #0이면 첫 배팅, 1이면 세번째카드 받고 배팅.

        self.all_clients_set = list()
        self.all_clients_end = list()


    def start(self, ip, port):
        print('func 1 start')
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #IPv4, 스트림 소켓 타입을 이용.

        try:
            self.server.bind((ip, port))

        except Exception as e:
            print('error code 1 : ', e)
            #return False
        else:
            self.bListen = True
            self.t1 = threading.Thread(target=self.listening, args=(self.server,))
            self.t1.start()
            print('Server Listening..')

        #return True

    def stop(self):
        print('func 2 start')
        self.bListen = False
        #if hasattr(self, 'server'): #Object 내에 name에 해당하는 attribute가 있으면 True
        self.server.close()
        self.removeAllClients()
        print('Server stop')

    def listening(self, server):
        print('func 3 start')
        while self.bListen:
            server.listen(5)
            #소켓이 총 몇개의 동시접속까지를 허용할 것이냐는 : 5.
            try:
                client, addr = server.accept()
                print(str(client) + ' is connected')
            except Exception as e:
                print('error code 3 : ', e)
                break
            else:
                recv = client.recv(4096)
                your_nickname = str(recv, encoding='utf-8')
                print("id is " + your_nickname)
                self.clients.append(client)
                self.ip.append(addr)
                self.nickname_list.append(your_nickname)
                self.nickname[addr[1]] = your_nickname
                self.send_all('[SYSTEM] ' + your_nickname + '이 접속했습니다.')
                #self.player_money.append(300)  #qqq
                self.clients_call_state.append(0)

                self.live_or_die.append(0)
                self.all_clients_set.append(0)
                self.all_clients_end.append(0)

                if self.playing_state_server == 0:
                    self.nickname_state[your_nickname] = 0
                elif self.playing_state_server == 1:
                    self.nickname_state[your_nickname] = 3
                    msg1 = [53, '']
                    msg_pickle = pickle.dumps(msg1)
                    self.send_pickle(client, msg_pickle)

                time.sleep(2)
                # 모두에게 입장을 알린다.
                self.send_client_all_info()

                t = threading.Thread(target=self.receive, args=(addr, client))
                self.threads.append(t)
                t.start()

        # self.removeAllClients()
        # self.server.close()

    def receive(self, addr, client):
        print('func 4 start')
        while True:
            try:
                recv = client.recv(4096)
                status_code = 0
            except Exception as e:
                print('error code 4 :' , e)
                break
            else:
                try:
                    msg = str(recv, encoding='utf-8')
                    if msg:
                        # if status_code == 3:
                        #     time.sleep(1)
                        # print(self.ip[:][1].index(addr[1]))
                        print("[server_RECV] : ", addr, self.nickname[addr[1]], msg)
                        send_msgg = self.nickname[addr[1]] + " : " + msg
                        self.send_all(send_msgg)

                except:   # pickle 메세지 받는 곳. 그냥 메시지 말고.
                    pickle_msg = pickle.loads(recv)
                    msg = pickle_msg[1]
                    status_code = pickle_msg[0]  # 이걸로 준비나 뭐 클라이언트의 요청을 수행하자.
                                                 # status code 가 1이면 client의 ready를 위한 것. ready 해주자. nickname_ready dict의 ready 상태를 바꿔줘서 서버에서 각 클라이언트의 상태를 갱신해주자.
                                                 # 그냥 nickname_ready dict을 그냥 각 클라이언트의 상태로 정해주자.
                                                 # nickname_state로 바꿨다.
                #if status_code !=0:
                    if status_code ==1: #준비 취소
                        self.nickname_state[self.nickname[addr[1]]] = 0
                        print(self.nickname[addr[1]] + '이 준비취소')
                        self.send_client_all_info()

                    elif status_code == 2: #준비
                        self.nickname_state[self.nickname[addr[1]]] = 1
                        print(self.nickname[addr[1]] + '이 준비함')
                        self.send_client_all_info()

                    elif status_code == 3: #게임 시작
                        if self.check_all_ready():
                            for i in self.nickname_state.keys():
                                self.nickname_state[i] = 2

                            #애들 각자 돈정보 보내주기

                            for i in range(len(self.clients)):
                                self.player_money[i] -= self.batting_money_server

                            new_pan_msg = [64, '', self.player_money]
                            new_pan_msg_pickle = pickle.dumps(new_pan_msg)
                            for c in self.clients:
                                self.send_pickle(c, new_pan_msg_pickle)

                            ###################################

                            self.send_all('[SYSTEM] ' + str(self.game_num) + '번째 게임 시작!!')

                            #########이 receive를 처리 안하고 있으면 receive가 안되지.
                            time.sleep(1)
                            self.Game_start()

                            print("게임 시작~!")
                            time.sleep(1)
                            self.send_client_all_info()

                            time.sleep(1)

                        else:
                            msg = '[SYSTEM] 모두 준비 안됬습니다.'

                    elif status_code == 11: #애들 카드 보여줄거 정하고 다 정햇음 뿌려주기
                        if msg[1] == 2:
                            temp = self.this_game_card[msg[0]][0]
                            self.this_game_card[msg[0]][0] = self.this_game_card[msg[0]][1]
                            self.this_game_card[msg[0]][1] = temp

                        self.all_clients_set[msg[0]] = 1

                        msg=''

                        if self.check_all_set():
                            c_index = 0
                            for c in self.clients:
                                msg2 = [62, self.this_game_card, self.this_card_rank, self.random_start]
                                msg2_pickle = pickle.dumps(msg2)
                                self.send_pickle(c, msg2_pickle)
                                c_index += 1

                    elif status_code == 12: #마지막 어떤 패 낼지 정하는 요청.
                        tmp_list = []
                        if msg[1] == 1:
                            tmp_list.append(self.this_game_card[msg[0]][0])
                            tmp_list.append(self.this_game_card[msg[0]][1])
                        elif msg[1] ==2:
                            tmp_list.append(self.this_game_card[msg[0]][1])
                            tmp_list.append(self.this_game_card[msg[0]][2])
                        elif msg[1] ==3:
                            tmp_list.append(self.this_game_card[msg[0]][0])
                            tmp_list.append(self.this_game_card[msg[0]][2])

                        self.this_game_card[msg[0]] = tmp_list

                        self.all_clients_end[msg[0]] = 1

                        if self.check_all_end():
                            print('end~!')
                            self.end_Game()

                        msg=''

                    #삥, 쿼터, 하프, 콜을 받았을때
                    elif status_code == 21:
                        if self.live_or_die[msg[0]] !=2: # 다이 상태 아니면 콜 가능하게
                            if msg[3] !=4:
                                self.server_call_state = msg[3]

                            temp_liv_or_die = list()

                            if msg[3] <4:
                                for i in self.live_or_die:
                                    if i==2:
                                        temp_liv_or_die.append(i)
                                    else:
                                        temp_liv_or_die.append(0)
                            else:
                                temp_liv_or_die = self.live_or_die

                            self.player_money[msg[0]]-=msg[2]
                            #이때 애들 돈 상태 보내주자.
                            # 근데 보낸다고 아무 버튼 안누르면 최신화를 못해.
                            self.total_money += msg[2]
                            self.live_or_die = temp_liv_or_die
                            self.live_or_die[msg[0]] = 1
                            self.clients_call_state[msg[0]] = msg[3]


                            if msg[3] ==1 or msg[3] == 2 or msg[3] ==3 or msg[3] ==4:
                                self.batting_money_server = msg[2]

                            if self.check_all_call_or_die():
                                if self.server_phase == 0:
                                    self.round_1_end()
                                    msg = '가 콜, 모두 한 장 더!'
                                    send_msgg = '[SYSTEM] ' + self.nickname[addr[1]] + msg
                                    self.send_all(send_msgg)
                                else:
                                    # 이떄는 끝장본다는 메세지.
                                    msg = '가 콜!(+' + str(msg[2]) + '), 결과는?'
                                    print("[server_RECV] : ", addr, self.nickname[addr[1]], msg)
                                    send_msgg = '[SYSTEM] ' + self.nickname[addr[1]] + msg
                                    self.send_all(send_msgg)

                                    msg3_pickle = [74, '']
                                    msg3_pickle = pickle.dumps(msg3_pickle)
                                    for c in self.clients:
                                        self.send_pickle(c, msg3_pickle)
                                    #self.end_Game()
                                msg = ''

                            else:
                                msg2 = [63,  [self.player_money, self.total_money], self.batting_money_server, self.server_call_state, self.live_or_die, self.clients_call_state]
                                msg2 = pickle.dumps(msg2)
                                for c in self.clients:
                                    self.send_pickle(c, msg2)

                                if msg[3] ==1:
                                    msg = '가 삥!(+' + str(msg[2]) +')'
                                elif msg[3] ==2:
                                    msg = '가 쿼터!(+' + str(msg[2]) +')'
                                elif msg[3] ==3:
                                    msg = '가 하프!(+' + str(msg[2]) +')'
                                elif msg[3] ==4:
                                    msg = '가 콜!(+' + str(msg[2]) +')'

                                #msg = '가 콜했습니다. 남은돈 : ' + str(self.player_money[msg[0]])

                    #다이를 받았을때.
                    elif status_code == 22:
                        self.live_or_die[msg[0]] = 2
                        self.clients_call_state[msg[0]] = msg[3]

                        if msg[3] != 5:
                            self.server_call_state = msg[3]

                        if self.check_all_call_or_die():
                            if self.server_phase == 0:
                                self.round_1_end()
                                msg = '가 다이, 모두 한 장 더!'
                                send_msgg = '[SYSTEM] ' + self.nickname[addr[1]] + msg
                                self.send_all(send_msgg)

                            else:
                                # 이떄는 끝장본다는 메세지.
                                msg = '가 다이!, 결과는?'
                                print("[server_RECV] : ", addr, self.nickname[addr[1]], msg)
                                send_msgg = '[SYSTEM] ' + self.nickname[addr[1]] + msg
                                self.send_all(send_msgg)

                                if self.check_all_die():
                                    self.end_Game()
                                else:
                                    msg3_pickle = [74, '']
                                    msg3_pickle = pickle.dumps(msg3_pickle)
                                    for c in self.clients:
                                        self.send_pickle(c, msg3_pickle)
                                #self.end_Game()
                            msg = ''


                        else:
                            msg2 = [63, [self.player_money, self.total_money], self.batting_money_server, self.server_call_state, self.live_or_die, self.clients_call_state]
                            msg2 = pickle.dumps(msg2)
                            for c in self.clients:
                                self.send_pickle(c, msg2)

                            msg = '가 다이!'


                    if msg:
                        # if status_code == 3:
                        #     time.sleep(1)
                        # print(self.ip[:][1].index(addr[1]))
                        print("[server_RECV] : ", addr, self.nickname[addr[1]], msg)
                        send_msgg = '[SYSTEM] ' + self.nickname[addr[1]] + msg
                        if status_code == 3:
                            send_msgg = '[SYSTEM] ' + msg
                        if status_code != 1 and status_code !=2:
                            self.send_all(send_msgg)

    def send_client_all_info(self):
        print('func 5 start')
        self.player_money = []
        db1 = use_DB2.connectDB_local()
        for i in self.nickname_list:
            dict = use_DB2.find1(db1, i)
            user_money = dict['user_money']
            self.player_money.append(user_money)

        print(self.player_money)
        msg3 = [52, self.nickname, self.nickname_state, self.nickname_list, self.clients_call_state, self.player_money]
        msg3_pickle = pickle.dumps(msg3)
        try:
            for c in self.clients:
                self.send_pickle(c, msg3_pickle)
            # print('send pickle ok : ' + msg)
        except Exception as e:
            print("error code 5 : ", e)

    def send_all(self, msg):
        print('func 6 start')
        try:
            for c in self.clients:
                c.send(msg.encode())
            print('send : ' + msg)
        except Exception as e:
            print("error code 6 : ", e)

    def send_pickle(self, client, msg):
        print('func 7 start')
        try:
            client.send(msg)
            print('send pickle msg success')
        except Exception as e:
            print('error code 7 :', e)

    def check_all_ready(self):  #모두 준비가 되었는지.
        print('func 8 start')
        for i in self.nickname_state.values():
            print(i)
            if i ==0:
                return False
        # 모두 1인걸로 바꾸자. 0이 아닌게 아니라.
        return True

    def check_all_set(self): #무슨 카드 보여줄지 선택 다 했는지.
        print('func 9 start')
        for i in self.all_clients_set:
            print(i)
            if i ==0:
                return False
        # 모두 1인걸로 바꾸자. 0이 아닌게 아니라.
        return True

    def check_all_end(self):
        print('func 10 start')
        for i in self.all_clients_end:
            print(i)
            if i ==0:
                return False
        # 모두 1인걸로 바꾸자. 0이 아닌게 아니라.
        return True

    def check_all_call_or_die(self):
        print('func 11 start')
        die_cnt = 0
        no_do_cnt = 0
        for i in self.live_or_die:
            if i==0:
                no_do_cnt+=1
            elif i == 2:
                die_cnt+=1

        sum1 = die_cnt + no_do_cnt

        if no_do_cnt==1 and sum1 == len(self.clients):
            return True

        for i in self.live_or_die:
            if i ==0:
                return False

        return True

    def check_all_die(self):
        print('func 12 start')
        die_num = 0
        for i in self.live_or_die:
            if i == 2:
                die_num += 1

        if die_num == len(self.live_or_die) - 1:
            return True

        return False

    def check_draw(self, sort_zip):
        print('func 13 start')
        val = []
        for live, rank, index in sort_zip:
            if live == 1 or live == 0:
                val.append(rank)

        val = sorted(val)

        if len(val) == 1:
            return False

        ans = 0
        for i in range(len(val) - 1):
            if val[i] != val[i + 1]:
                if ans == 0:
                    return False
            else:
                ans += 1

        return ans

    def Game_start(self):
        print('func 14 start')
        msg = [51, self.nickname_list]
        msg_pickle = pickle.dumps(msg)
        try:
            for c in self.clients:
                self.send_pickle(c, msg_pickle)
            #print('send pickle ok : ' + msg)
        except Exception as e:
            print("Send() Error : ", e)

        self.jokbo = game_tool2.jokbo
        for c in self.clients:
            self.total_money += self.batting_money_server

        self.playing_state_server = 1
        self.this_game_card, self.this_card_rank = game_tool2.random_get(len(self.clients), self.game_mode)
        # this game card가 몇번째 순위인지 같이 넘겨주자. 그래야 족보에 하이라이트 칠 수 있다.
        #print(self.this_game_card)


        db1 = use_DB2.connectDB_local()
        for i in self.nickname_list:
            dict = use_DB2.find1(db1, i)
            user_money = dict['user_money']
            use_DB2.update_money1(db1, i, user_money-self.batting_money_server)

        self.random_start = random.randint(0, len(self.clients)-1)
        c_index=0
        for c in self.clients:
            msg2 = [61, self.this_game_card, self.this_card_rank, self.random_start]
            msg2_pickle = pickle.dumps(msg2)
            self.send_pickle(c, msg2_pickle)
            c_index+=1

        ###클라이언트들에게 모두의 카드정보 다 뿌려주기
        ###이거 받으면 phase가 1이 되고 1이 되면 각자 카드 뭐 보여줄지 고른다.

        print('game start!!!')

    def round_1_end(self):
        print('func 15 start')
        self.server_phase = 1

        if self.check_all_die():
            self.end_Game()


        for i in range(len(self.live_or_die)):
            if self.live_or_die[i]==1:
                self.live_or_die[i] = 0

        for i in range(len(self.clients_call_state)):
            if self.clients_call_state[i]!=5:
                self.clients_call_state[i] = 0


        msg2 = [71, [self.player_money, self.total_money], self.batting_money_server,
                self.server_call_state, self.live_or_die, self.clients_call_state, self.this_game_card]
        msg2 = pickle.dumps(msg2)
        for c in self.clients:
            self.send_pickle(c, msg2)

    def end_Game(self):
        print('func 16 start')
        for i in self.this_game_card:
            l = game_tool2.what_jokbo(i, game_tool2.jokbo)
            self.this_card_rank.append(l)

        msg2 = [71, [self.player_money, self.total_money], self.batting_money_server,
                self.server_call_state, self.live_or_die,  self.clients_call_state, self.this_game_card]
        msg2 = pickle.dumps(msg2)
        for c in self.clients:
            self.send_pickle(c, msg2)

        time.sleep(3) # 결과 발표 전에 마지막 상태 보여주려고
        self.send_all('[SYSTEM] 과연?!')

        print(self.this_card_rank)

        time.sleep(2)
        index1 = []
        for i in range(len(self.clients)):  #클라이언트가 아니라 이번 게임 멤버 수로
            index1.append(i)

        zip_c = zip(self.live_or_die, self.this_card_rank, index1)
        sort_zip_c = sorted(zip_c, key=lambda x: (x[0], x[1]))

        print(sort_zip_c)
        # 무승부.
        if self.check_draw(sort_zip_c) is not False: #무야호
            print('비겼어')
            idx = random.randint(0, self.check_draw(sort_zip_c))
            winner_num = sort_zip_c[idx][2]
            print('랜덤으로 정한다')
            print(self.check_draw(sort_zip_c))
            self.player_money[winner_num] += self.total_money
            self.total_money = 0

            msg2 = [72, [self.player_money, self.total_money], self.batting_money_server,
                    self.server_call_state, self.live_or_die, self.clients_call_state]
            msg2 = pickle.dumps(msg2)
            for c in self.clients:
                self.send_pickle(c, msg2)

            time.sleep(1)

            self.send_all('[SYSTEM] ' + '비겼습니다! 랜덤으로..')
            time.sleep(3)
            self.send_all('[SYSTEM] ' + self.nickname_list[winner_num] + '가 이겼습니다!')

            time.sleep(4)

            # 초기화 시켜주자.
            self.batting_money_server = 10
            self.server_call_state = 0
            self.playing_state_server = 0
            self.live_or_die = []
            self.server_phase = 0
            self.all_clients_set = []
            self.all_clients_end = []
            self.clients_call_state = []

            for i in range(len(self.clients)):
                self.live_or_die.append(0)
                self.all_clients_set.append(0)
                self.all_clients_end.append(0)
                self.clients_call_state.append(0)

            print(self.player_money)

            db1 = use_DB2.connectDB_local()
            idx2 = 0
            for i in self.nickname_list:
                use_DB2.update_money1(db1, i, self.player_money[idx2])
                idx2 += 1

            msg2 = [73, [self.player_money, self.total_money], self.batting_money_server,
                    self.server_call_state, self.live_or_die]
            msg2 = pickle.dumps(msg2)
            for c in self.clients:
                self.send_pickle(c, msg2)

            self.game_num += 1


        else: #결판 난 경우
            winner_num = sort_zip_c[0][2]
            #1등이 1떙에서 9땡 사이인 경우 만약 3 7 땡잡이가 있으면
            if sort_zip_c[0][1] <=12 and sort_zip_c[0][1]>=4:
                for l, rank, num in sort_zip_c:
                    if l==1 and rank == 30:
                        winner_num = num
                        print('땡잡이!')

            tempp = []
            #1등이 장땡 밑인데 사구파토면
            if sort_zip_c[0][1] >=3:
                for l, rank, num in sort_zip_c:
                    if l==1:
                        tempp.append(num)
                        if rank == 29:
                            winner_num = 5
                            print('49파토')

            if winner_num == 5:
                self.send_all('[SYSTEM] ' + '사구파토!')
                idx = random.randint(0, len(tempp)-1)
                winner_num = tempp[idx]
                print('랜덤으로 승자는')
                print(tempp)


            self.player_money[winner_num] += self.total_money
            self.total_money = 0

            msg2 = [72, [self.player_money, self.total_money], self.batting_money_server,
                    self.server_call_state, self.live_or_die,  self.clients_call_state]
            msg2 = pickle.dumps(msg2)
            for c in self.clients:
                self.send_pickle(c, msg2)

            time.sleep(1)

            self.send_all('[SYSTEM] ' + self.nickname_list[winner_num] + '가 이겼습니다!')

            time.sleep(4)

            #초기화 시켜주자.
            self.batting_money_server = 10
            self.server_call_state = 0
            self.playing_state_server = 0
            self.live_or_die = []
            self.server_phase = 0
            self.all_clients_set = []
            self.all_clients_end = []
            self.clients_call_state = []

            for i in range(len(self.clients)):
                self.live_or_die.append(0)
                self.all_clients_set.append(0)
                self.all_clients_end.append(0)
                self.clients_call_state.append(0)

            print(self.player_money)

            db1 = use_DB2.connectDB_local()
            idx2 = 0
            for i in self.nickname_list:
                use_DB2.update_money1(db1, i, self.player_money[idx2])
                idx2+=1

            msg2 = [73, [self.player_money, self.total_money], self.batting_money_server,
                    self.server_call_state, self.live_or_die]
            msg2 = pickle.dumps(msg2)
            for c in self.clients:
                self.send_pickle(c, msg2)

            self.game_num +=1

    def removeAllClients(self):
        print('func 17 start')
        for c in self.clients:
            c.close()

        self.ip.clear()
        self.clients.clear()
        self.threads.clear()
        self.nickname.clear()
        self.nickname_state.clear()
        #추가해야지 !


if __name__ == '__main__':
    s = ServerSocket()
    print('Process Start..')

    while True:
        inp1 = input()
        if inp1 == '1':
            s.start('1xx.xxx.xxx.xxx', 12346)
        elif inp1 == '2':
            s.listening(s.server)
        elif inp1 == '3':
            s.stop()
        elif inp1 == '4':
            s.send(inp1)
        elif inp1 == '5':
            inp2 = input()
        elif inp1 == '6':
            inp2 = input()
        elif inp1 == '7':
            s.receive(s.ip[0], s.clients[0])
        elif inp1 == '8':
            s.check_all_ready()
        elif inp1 == '9':
            print(s.live_or_die)

        else:
            break


    print('End..')









