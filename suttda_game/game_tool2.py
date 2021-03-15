import random

def random_get(user_num, cnt_num):
    card_id = dict()

    users = list()

    for i in range(1, 21):
        card_id[i] = 0


    for i in range(user_num):
        temp = list()
        j=0
        while j<cnt_num:
            rand_card_num = random.randint(1,20) #1부터 20까지 랜덤한 숫자.
            if card_id[rand_card_num] == 0:
                card_id[rand_card_num] = 1
                temp.append(rand_card_num)
                j+=1
            else:
                None
                #print('already selected')

        users.append(temp)

    rank = list()

    return users, rank

jokbo_name = {1: '삼팔광땡', 2: '광땡', 3:'장땡', 4:'구땡', 5:'팔땡',
              6: '칠땡', 7: '육땡', 8:'오땡', 9:'사땡', 10:'삼땡',
              11: '이땡', 12: '일땡', 13:'알리', 14:'독사', 15:'구삥',
              16: '장삥', 17: '장사', 18:'세륙', 19:'아홉끗', 20:'여덟끗',
              21: '일곱끗', 22: '여섯끗', 23: '다섯끗', 24: '사끗', 25: '삼끗',
              26: '두끗', 27: '한끗', 28: '망통'}


jokbo = dict()

jokbo['3,8'] = 1
jokbo['1,3'] = 2
jokbo['1,8'] = 2

j = 3
temp_index = list()
for i in range(1, 11):
    temp_index.append(i)

temp_index = sorted(temp_index, key=lambda x: -x)

for i in temp_index:
    tmp = str(i) + ',' + str(i+10)
    jokbo[tmp] = j
    j+=1

jokbo['1,2,'] = j
j+=1
jokbo['1,4,'] = j
j+=1
jokbo['1,9,'] = j
j+=1
jokbo['1,10,'] = j
j+=1
jokbo['4,10,'] = j
j+=1
jokbo['4,6,'] = j
j+=1
jokbo['9,,'] = j
j+=1
jokbo['8,,'] = j
j+=1
jokbo['7,,'] = j
j+=1
jokbo['6,,'] = j
j+=1
jokbo['5,,'] = j
j+=1
jokbo['4,,'] = j
j+=1
jokbo['3,,'] = j
j+=1
jokbo['2,,'] = j
j+=1
jokbo['1,,'] = j
j+=1
jokbo['0,,'] = j
j+=1
jokbo['4,9,'] = j
j+=1
jokbo['3,7,'] = j

def what_jokbo(inp1, jokbo_):
    inp1 = sorted(inp1, key=lambda x:x)
    inp1_str = str(inp1[0]) + ',' + str(inp1[1])

    b = jokbo_.get(inp1_str)

    if b==None:
        tmp_inp1 = inp1[0] % 10
        tmp_inp2 = inp1[1] % 10
        if tmp_inp1 == 0:
            tmp_inp1 +=10
        if tmp_inp2 == 0:
            tmp_inp2 +=10

        #작은걸 앞으로 해준다. 해서 족보 다 일치시키기
        if tmp_inp1 > tmp_inp2:
            temp = tmp_inp1
            tmp_inp1 = tmp_inp2
            tmp_inp2 = temp

        inp1_str = str(tmp_inp1) + ',' + str(tmp_inp2) + ','

        b = jokbo_.get(inp1_str)

        if b==None:
            tmp_inp3 = tmp_inp1 + tmp_inp2
            tmp_inp3 %= 10

            inp3_str = str(tmp_inp3) + ',,'
            b = jokbo_.get(inp3_str)


    return b


if __name__ == '__main__':

    index1 = []
    for i in range(3):  # 클라이언트가 아니라 이번 게임 멤버 수로
        index1.append(i)

    inp = [ 7, 13]
    a = what_jokbo(inp, jokbo)
    print(a)
