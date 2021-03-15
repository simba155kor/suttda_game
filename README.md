# suttda_game

소켓 프로그래밍을 활용하여 서버와 클라이언트가 서로 메시지를 주고받으며 동작하는 화투패를 이용한 카드게임입니다. 20장의 화투패에서 각자 총 3장의 카드를 받고 배팅하여 누가 족보가 더 높은지 승부합니다. 


<b>server2.py</b> server 스크립트 

<b>client2.py, client_window2.py</b> client 스크립트 

<b>use_DB2.py</b> 데이터베이스와 연동하기 위한 모듈 

<b>game_tool2.py</b> 게임 족보를 위한 모듈 

Qt Designer로 만든 ui 파일

화투 패와 캐릭터 이미지, 음성 파일로 구성되어 있습니다.


# 개발 환경

ㆍPython 3.7

ㆍPycharm

ㆍQt designer
 
ㆍpickle
 
ㆍPyQt5 5.15.2

ㆍMySQL 5.7
 
ㆍplaysound 1.2.2


# 실행 방법
코드에 있던 제 ip를 1xx.xxx.xxx.xxx 로 변경해두었습니다. server와 client 스크립트, use_DB 모듈의 ip 부분을 환경에 맞게 설정해주어야 합니다. 
server 스크립트를 실행하고 터미널에서 1을 입력하여 서버를 구동합니다.
server가 켜져있다면 client_window2 스크립트를 실행하여 게임을 실행합니다. 


# 게임 방법
기존의 3장을 이용한 섯다게임과 규칙  족보가 똑같습니다. 먼저 2장의 화투패를 받고 둘 중 공개할 패를 정합니다. 이때 공개하는 패는 모두에게 공개되며 나머지 한 장은 공개되지 않습니다. 모든 플레이어가 정하였으면 배팅을 하거나 죽습니다. 모두 배팅이 끝나면 패를 한 장 더 받고 이어서 배팅한 후에 마지막에 3장 중에 자신이 내고 싶은 패 2장을  승부합니다. 


# 명령어 코드
서버와 클라이언트가 주고 받는 메시지는 pickle이나 텍스트입니다. 
pickle의 경우 첫 번째 값은 status_code로 각 메시지가 하는 역할을 나타내기 위한 고유 번호입니다. 나머지는 전송하고자 하는 데이터입니다. 
텍스트의 경우 사용자가 채팅창으로 대화할때 사용됩니다. 

-----------------------------------------------------------------------------------------------------------------------------------------
서버 측이 받는 pickle 메시지의 status_code가

ㆍ1  : client의 준비 취소 요청

ㆍ2  : client의 준비 요청

ㆍ3  : 가장 처음 들어온 client의 게임 시작 요청

ㆍ45  : 처음에 공개할 카드를 선택하는 요청

ㆍ46  : 마지막에 어떤 패를 낼지 정하는 요청

ㆍ200  : client의 콜 요청

ㆍ300  : client의 다이 요청



-----------------------------------------------------------------------------------------------------------------------------------------
클라이언트 측이 받는 pickle 메시지의 status_code가

ㆍ51  : server의 게임 시작을 알리는 메시지

ㆍ52  : server에 client가 입장하였을때 client의 정보를 전송

ㆍ53  : client에게 게임 도중임을 알리는 메시지

ㆍ61  : 각 client에게 카드 전달

ㆍ62  : 공개할 카드 선택 후 다시 카드 전달

ㆍ63  : 판돈과 client의 게임머니를 갱신해주는 메시지

ㆍ64  : 게임판을 초기화하라는 메시지

ㆍ71  : 승부보는 상황

ㆍ72  : 마지막 승부보는 상황

ㆍ73  : 게임종료를 알리는 메시지

ㆍ74  : 무승부를 알리는 메시지








# 게임 장면
client window 스크립트를 실행하면 처음 등장하는 화면입니다. 회원가입으로 MySQL server에 계정을 등록하고 성공하면 로그인하여 게임을 실행할 수 있습니다. MySQL server나 server 스크립트가 동작중이지 않으면 게임이 실행되지 않습니다.
![1](https://user-images.githubusercontent.com/66295630/111123080-3da79d80-85b2-11eb-87e8-b0f9625e0823.png)
![2](https://user-images.githubusercontent.com/66295630/111123084-3e403400-85b2-11eb-9304-bd79e0da7de6.png)

-------------------------------------------
게임 중인 화면입니다. 오른쪽 하단에 있는 채팅창을 이용하여 유저들과 대화할 수 있습니다. 
오른쪽 상단의 족보 보기를 통해 족보를 확인할 수 있습니다. 준비 버튼을 눌러 준비 상태가 될 수 있고 준비완료버튼을 누르면 취소할 수 있습니다. 모두 준비가 되었다면 처음 접속한 client가 게임 시작 버튼을 눌러서 게임을 시작할 수 있습니다. 
자신의 이름에 빨간불이 들어오는 것으로 내차례임을 알 수 있습니다. 자신의 차례일때 오른쪽 중단의 배팅 버튼을 이용해서 배팅을 할 수 있습니다. 현재 판돈에 맞춰서 얼마가 배팅되는지 금액이 함께 표시됩니다.
중앙의 상황판으로 방금 플레이어가 얼마나 배팅했는지를 알 수 있습니다.
게임이 종료되면 다시 모두 준비 버튼을 누르고 게임시작 버튼을 눌러야 새롭게 시작됩니다.

![3](https://user-images.githubusercontent.com/66295630/111122580-9460a780-85b1-11eb-95ce-22f02dd80beb.PNG)
![4](https://user-images.githubusercontent.com/66295630/111122584-9591d480-85b1-11eb-91dd-242034f7177d.PNG)
![5](https://user-images.githubusercontent.com/66295630/111122587-962a6b00-85b1-11eb-986a-5236721c0a05.PNG)
![6](https://user-images.githubusercontent.com/66295630/111122590-96c30180-85b1-11eb-854a-fe368c18a25a.PNG)


