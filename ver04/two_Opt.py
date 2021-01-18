from ScheduleNPB import Output
o = Output()
D = o.D
def isFeasible(schedule, day1, day2):
    if day1 > day2:
        day1, day2 = day2, day1
    elif day1 == day2:
        return True
    for team in range(6):
        if day1 >= 2 and schedule[day1-2][team]==schedule[day1-1][team]==schedule[day2][team]==1:
            return False
        if day2 <= len(schedule)-3 and schedule[day2+2][team]==schedule[day2+1][team]==schedule[day1][team]==1: 
            return False
    
    return True

def exchangeCost(schedule, day1, day2):
    """
    """
    if day1 > day2:
        day1, day2 = day2, day1
    elif day1 == day2:
        return 0    
    initial_cost = 0
    for team in range(6):
        cur1  = schedule[day1][team].index(1)
        post1 = schedule[day1+1][team].index(1)
        cur2  = schedule[day2][team].index(1)
        post2 = schedule[day2-1][team].index(1)
        initial_cost += D[cur1][post1]+D[cur2][post2]
        if day1 >= 1:
            initial_cost += D[schedule[day1-1][team].index(1)][cur1]
        if day2 < len(schedule)-1:
           initial_cost += D[schedule[day2+1][team].index(1)][cur2]

    for team in range(6):
        cur1  = schedule[day2][team].index(1)
        post1 = schedule[day1+1][team].index(1)
        cur2  = schedule[day1][team].index(1)
        post2 = schedule[day2-1][team].index(1)
        initial_cost -= D[cur1][post1]+D[cur2][post2]
        if day1 >= 1:
            initial_cost -= D[schedule[day1-1][team].index(1)][cur1]
        if day2 < len(schedule)-1:
           initial_cost -= D[schedule[day2+1][team].index(1)][cur2]
    
    return -initial_cost

def swap(schedule, day1, day2):
    if day1 > day2:
        day1, day2 = day2, day1
    elif day1 == day2:
        return schedule
    schedule[day1], schedule[day2] = schedule[day2], schedule[day1]

    return schedule

def two_Opt(schedule):
    """
    任意の二つの日程の順序入れ替えを考える。
    入れ替える際に、その日程の前後二日ずつを確認して、制約を違反しないか検証する。
    入れ替えコストを計算し、距離が短くなりそうなら入れ替える
    入力：各日の試合スケジュールが入ったリスト
    [一日目(6チーム分),...,n日目(6チーム分)]みたいな感じで。
    入れ替えコストが負なら入れ替える。
    最良のところで入れ替えることにする。
    """
    S = list(range(len(schedule)))
    best_cost = 0
    exchange  = [None, None]
    for day1 in S[:-1]:
        for day2 in S[day1+1:]:
            if isFeasible(schedule, day1, day2):
                tmp_cost = exchangeCost(schedule, day1, day2)
                if tmp_cost < best_cost:
                    best_cost = tmp_cost
                    exchange  = [day1, day2]
    if best_cost < 0:
        day1, day2 = exchange
        return swap(schedule, day1, day2)
    else:
        return schedule