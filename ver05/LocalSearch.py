from localSearch import two_Opt
from utils.utils import Load
from ScheduleNPB import Output
"""
To Do : convert関数の作成
        結果描写用のプログラムを作成
        交流戦にも適用可能なように拡張
"""
def convert(game_type, league, output):
    schedule = output.schedules[game_type]
    I        = output.Teams[league]
    S        = output.S[game_type]
    data     = [[[0]*len(I)for _ in I]for _ in S]
    minus    = -I[0]
    for i in I:
        for v in schedule[i]:
            s,j,venue = v
            if venue == 'home':
                data[s][i+minus][i+minus] = 1
            else:
                data[s][i+minus][j+minus] = 1
    
    return data

def calcDist(data, game_type, league, output):
    schedule = output.schedules[game_type]
    I        = output.Teams[league]
    S        = output.S[game_type]
    D        = output.D
    start    = I[0]
    dist = 0
    for s in S[:-1]:
        for i in I:
            for j in I:
                for k in I:
                    dist += D[j][k]*data[s][i-start][j-start]*data[s+1][i-start][k-start]
    return dist

def main():
    output = Output()
    D = output.D
    leagues = ['s','p']
    for league in leagues:
        filename = 'r_pre_'+league+'.pkl'
        e = Load(filename)
        output.getSchedule(e, 'r_pre', league=league)

    e = Load('i_ps.pkl')
    output.getSchedule(e, 'i')

    for league in leagues:
        filename= 'r_post_'+league+'.pkl'
        e = Load(filename)
        output.getSchedule(e, 'r_post', league=league)
    output.MergeRegularSchedule()
    output.getWholeSchedule()

    data = convert('r_post', 'p', output)
    dist = calcDist(data,'r_post', 'p', output)
    print(dist)
    data = two_Opt.two_Opt(data)
    data = convert('r_post', 's', output)
    dist = calcDist(data,'r_post', 's', output)
    print(dist)
    data = two_Opt.two_Opt(data)
    dist = calcDist(data,'r_post', 's', output)
    print(dist)