
letters = [chr(i) for i in range(65, 91)]
staDic = dict(zip(letters, [0] * 26))
ins = [j for i in range(4) for j in input()]
for k in ins:
    if k in letters:
        staDic[k] += 1
maxValue = max(staDic.values())
ZDic = {'Z': staDic.pop('Z')}
while maxValue > 0:
    for value in staDic.values():
        if value >= maxValue:
            print('*', end=' ')
        else:
            print(' ', end=' ')
    if ZDic['Z'] >= maxValue:
        print('*')
    else:
        print(' ')
    maxValue -= 1
print(' '.join(letters))
