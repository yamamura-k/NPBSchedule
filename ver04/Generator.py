from itertools import combinations,permutations
def generator(teams):# とりあえず一日分, タプルの左側がホームって意味
    data = dict()
    index = 0
    for v in combinations(teams,3):
        res = list(set(teams)-set(v))
        for u in permutations(res):
            data[index] = []
            for i in range(3):
                data[index].append((v[i],u[i]))
            index += 1
            data[index] = []
            for i in range(3):
                data[index].append((u[i],v[i]))
            index += 1
    data_split = dict()
    for i in teams[1:]:
        key1 = (teams[0],i)
        key2 = (i,teams[0])
        data_split[key1] = pack(key1, data)
        data_split[key2] = pack(key2, data)
    # なんか上手いこと実行可能な組み合わせだけ列挙したい
    return data_split

def pack(pair, data):
    lis = []
    for i in data:
        if pair in data[i]:
            lis.append(data[i])
    return lis

def convert(perm):
    one_hot = [[0]*6 for _ in range(6)]
    for v in perm:
        i, j = v
        one_hot[i][i] = one_hot[j][i] = 1
    return one_hot

if __name__ == "__main__":
    data = generator(list(range(6)))
    print(data)
    exit()
    p = pack((0,3),data)
    print(len(p))