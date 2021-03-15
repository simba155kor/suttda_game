# suttda_game

20장의 화투패에서 각자 총 3장의 카드를 받고 배팅하여 누가 족보가 더 높은지로 승부하는 게임입니다. 각자 처음에 2장의 패를 받고 배팅한 후 1장을 더 받고나서 마지막으로 어떠한 족보를 선택할지 고릅니다.


# 개발 환경

ㆍPython 3.7
 
ㆍpickle
 
ㆍPyQt5

ㆍQt designer

ㆍMySQL 5.7

ㆍPycharm




# 명령어 코드
서버와 클라이언트가 주고 받는 메시지는 pickle이나 텍스트입니다. 
pickle의 경우 첫 번째 값은 status_code로 각 메시지가 하는 역할을 나타내기 위한 고유 번호입니다. 나머지는 전송하고자 하는 데이터입니다. 
텍스트의 경우 사용자가 채팅창을 이용하여 대화할때 용됩니다. 

서버 측이 받는 pickle 메시지의 status_code가

ㆍ1  : client의 준비 취소 요청

ㆍ2  : client의 준비 요청

ㆍ3  : 가장 처음 들어온 client의 게임 시작 요청

ㆍ45  : 처음에 공개할 카드를 선택하는 요청

ㆍ46  : 마지막에 어떤 패를 낼지 정하는 요청

ㆍ200  : client의 콜 요청

ㆍ300  : client의 다이 요청




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
![1](https://user-images.githubusercontent.com/66295630/111086241-6dc55100-855e-11eb-89ec-2f6caa82c8a8.PNG)


![2](https://user-images.githubusercontent.com/66295630/111086243-6f8f1480-855e-11eb-9901-7a3f0cff7f69.PNG)


![3](https://user-images.githubusercontent.com/66295630/111086077-c3e5c480-855d-11eb-8246-225bdf89db21.png)

