from utils import color
from base import Base

import os
import math
import pulp
from matplotlib import pyplot as plt
import japanize_matplotlib


class NPB(Base):
    """
    スケジュール作成において必要な定数や基本的な関数を定義するためのクラス。
    """
    def __init__(self):
        super().__init__()
        self.lat         = 90.38
        self.lon         = 111
        self.coordinates = {0:(43.014846,141.410007), 1:(38.256599,140.902609), 2:(33.595211,130.362182),
                            3:(35.768479,139.420484), 4:(35.645444,140.031186),5:(34.669359,135.476274),
                            6:(35.705471,139.751801), 7:(35.185805,136.947498), 8:(35.67452,139.717083),
                            9:(34.721394,135.361594), 10:(34.392028,132.484678), 11:(35.443086,139.64005)}
        self.Teams_name  = {0:'日ハ', 1:'楽天', 2:'S B ', 3:'西武', 4:'ロ　', 5:'オリ',
                            6:'巨人', 7:'中日', 8:'ヤク', 9:'阪神',10:'広島',11:'横浜'}
        self.stadium     = {0:'札幌ドーム', 1:'日本生命パーク宮城', 2:'福岡ドーム', 3:'メットライフドーム', 4:'ZOZOマリン', 5:'京セラ',
                            6:'東京ドーム', 7:'名古屋ドーム', 8:'神宮球場', 9:'甲子園',10:'MAZDA',11:'横浜スタジアム'}
        self.Teams["p"]  = [x for x in range(6)]
        self.Teams["s"]  = [x for x in range(6,12)]

        self.W['r']      = [w for w in range(21)]
        self.W["r_pre"]  = [w for w in range(5)]
        self.W["r_post"] = [w for w in range(16)]
        self.W["i"]      = [0,1,2]

        self.total_game['r']      = 42
        self.total_game['r_pre']  = 10
        self.total_game['r_post'] = 32
        self.total_game['i']      = 6

        self.lb["r_pre"]  = 1
        self.ub["r_pre"]  = 1
        self.lb["r_post"] = 3
        self.ub["r_post"] = 4

        self.D = [[0]*12 for _ in range(12)]
    
    def EuclidDistance(self, coord1, coord2):
        dist = math.sqrt(((coord1[0]-coord2[0])*self.lat)**2+((coord1[1]-coord2[1])*self.lon)**2)
        return dist 
    
    def DistMatrix(self):
        K = self.Teams['p']+self.Teams['s']
        for i in K:
            for j in K:
                self.D[i][j] = self.EuclidDistance(self.coordinates[i],self.coordinates[j])

    def Merge(self, list1, list2):
        if len(list1) != len(list2):
            print("Can't merge these!")
            return 
        return_list = [0]*len(list1)
        for i in range(len(list1)):
            return_list[i] = max(list1[i],list2[i])
        
        return return_list

class Solve(NPB):
    """
    移動距離を最小化するようなスケジューリング問題を線形計画ソルバーを用いて解くためのクラス。
    """
    def __init__(self):
        super().__init__()

    def RegularGame(self, league, type, initial_position=None, num_of_process=1, option=[], time_limit=3600, solver=0):
        """
        league           : 'p'/'s'.
        type             : 'r_pre'/'r_post'. (交流戦前/交流戦後)
        initial_position : 直前に試合を行なった球場を表現するリスト(1x12).
        num_of_process   : 問題を解くさいの並列数
        option           : solverに渡すoption
        time_limit       : 制限時間(単位は秒)。デフォルトは3600s
        """
        if type not in ['r_pre','r_post']:
            print('key error')
            return 
        self.DistMatrix()# calc dist mat
        # set local variables
        I = self.Teams[league]
        W = self.W[type]
        D = self.D

        # declare problem type
        problem = pulp.LpProblem('GameSchesule')

        # set variables
        h    = pulp.LpVariable.dicts('home', ([0,1],I,I,W),0,1,'Integer')
        v    = pulp.LpVariable.dicts('visitor', ([0,1],I,I,W),0,1,'Integer')
        home = pulp.LpVariable.dicts('new_home', ([0,1],I,I,W),0,1,'Integer')
        vis  = pulp.LpVariable.dicts('new_vis', ([0,1],I,I,I,W),0,1,'Integer')
        
        # set objective function
        obj = [D[_from][to]*home[day][_from][to][w]for _from in I for to in I for w in W for day in [0,1]]
        obj += [D[_from][to]*vis[day][team][_from][to][w]for _from in I for to in I for w in W for day in [0,1]for team in I]
        if initial_position:
            obj += [D[initial_position[team]][team]*pulp.lpSum([h[0][team][j][0]for j in I])for team in I for to in I]
            obj += [D[initial_position[team]][to]*v[0][team][to][0]for team in I for to in I]
        obj = pulp.lpSum(obj)
        problem += obj
        
        # set constraints
        for i in I:
            # 総試合数に関する制約
            problem += pulp.lpSum([h[0][i][j][w]+v[0][i][j][w]+h[1][i][j][w]+v[1][i][j][w] for j in I for w in W]) == self.total_game[type]
            for w in W:
                # 1日あたりの試合数に関する制約
                problem += pulp.lpSum([h[0][i][j][w]+v[0][i][j][w] for j in I]) == 1
                problem += pulp.lpSum([h[1][i][j][w]+v[1][i][j][w] for j in I]) == 1
                
        for d in [0,1]:
            for w in W:                
                for i in I:
                    for j in I:
                        # iがホームでjと試合をする＝jはビジター(i)で試合をする
                        problem += h[d][i][j][w]-v[d][j][i][w] == 0

        # 非線形な目的関数を線形にするために導入した変数に関する制約 
        for _from in I:
            for to in I:
                # 1週目の金曜日に行われる試合について
                problem += (1-pulp.lpSum([h[1][to][j][0]for j in I])-v[0][to][_from][0]+home[1][_from][to][0]>=0)
                problem += (pulp.lpSum([h[1][to][j][0]for j in I])-home[1][_from][to][0]>=0)
                problem += (v[0][to][_from][0]-home[1][_from][to][0]>=0) 
                for w in W[1:]:
                    # 2週目以降
                    problem += (1-pulp.lpSum([h[0][to][j][w]for j in I])-v[1][to][_from][w-1]+home[0][_from][to][w]>=0)
                    problem += (pulp.lpSum([h[0][to][j][w]for j in I])-home[0][_from][to][w]>=0)
                    problem += (v[1][to][_from][w-1]-home[0][_from][to][w]>=0)
                    problem += (1-pulp.lpSum([h[1][to][j][w]for j in I])-v[0][to][_from][w]+home[1][_from][to][w]>=0)
                    problem += (pulp.lpSum([h[1][to][j][w]for j in I])-home[1][_from][to][w]>=0)
                    problem += (v[0][to][_from][w]-home[1][_from][to][w]>=0)

        for team in I:
            for _from in I:
                for to in I:
                    # 1週目の金曜日に行われる試合について
                    problem += (1-v[1][team][to][0]-h[0][_from][team][0]+vis[1][team][_from][to][0]>=0)
                    problem += (v[1][team][to][0]-vis[1][team][_from][to][0]>=0)
                    problem += (h[0][_from][team][0]-vis[1][team][_from][to][0]>=0)
                    for w in W[1:]:
                        # 2週目以降 
                        problem += (1-v[0][team][to][w]-h[1][_from][team][w-1]+vis[0][team][_from][to][w]>=0)
                        problem += (v[0][team][to][w]-vis[0][team][_from][to][w]>=0)
                        problem += (h[1][_from][team][w-1]-vis[0][team][_from][to][w]>=0)
                        problem += (1-v[1][team][to][w]-h[0][_from][team][w]+vis[1][team][_from][to][w]>=0)
                        problem += (v[1][team][to][w]-vis[1][team][_from][to][w]>=0)
                        problem += (h[0][_from][team][w]-vis[1][team][_from][to][w]>=0)
        
        for i in I:
            for j in I:
                for w in W:
                    if i != j:
                        #同じ対戦カードは一週間に一回以下である、という制約
                        problem += (h[0][i][j][w]+v[0][i][j][w]+h[1][i][j][w]+v[1][i][j][w] <= 1)
                    else:
                        # 自チームとの試合は行えない
                        problem += (h[0][i][i][w]+v[0][i][i][w]+h[1][i][i][w]+v[1][i][i][w] == 0)

        for i in I:
            for j in I:
                for w in W[1:]:
                    if i != j:
                        #同じ対戦カードは一週間に一回以下である、という制約
                        problem += (h[0][i][j][w]+v[0][i][j][w]+h[1][i][j][w-1]+v[1][i][j][w-1] <= 1)
                       

        for i in I:
            home_total = 0
            vist_total = 0
            for j in I:
                home_game = pulp.lpSum([h[0][i][j][w]+h[1][i][j][w] for w in W])
                visitor_game = pulp.lpSum([v[0][i][j][w]+v[1][i][j][w] for w in W])
                home_total += home_game
                vist_total += visitor_game
                if i != j:
                    # ホームとビジターの試合数を調整するための制約
                    problem += (self.lb[type] <= home_game <= self.ub[type])
                    problem += (self.lb[type] <= visitor_game <= self.ub[type])
                    if type == "r_post":
                        problem += (6 <= home_game+visitor_game <= 7)

            # トータルでホームゲームとビジターゲームをなるべく同数行う
            problem += home_total-vist_total == 0
    
        # solve this problem
        if solver == 0:
            solver = pulp.PULP_CBC_CMD(msg=1, options=option, threads=num_of_process, maxSeconds=time_limit)
        elif solver == 1:
            solver = pulp.CPLEX_CMD()
        status = problem.solve(solver)

        return status, h, v


    def InterLeague(self, initial_position=None, num_of_process=1, option=[], time_limit=3600, solver=0):
        """
        initial_position : 直前に試合を行なった球場を表現するリスト(1x12).
        num_of_process   : 問題を解くさいの並列数
        option           : solverに渡すoption
        time_limit       : 制限時間(単位は秒)。デフォルトは3600s
        """
        # set local variables
        self.DistMatrix()
        D = self.D
        I = self.Teams['p']
        J = self.Teams['s']
        W_I = self.W['i']
        K = I+J

        # declare problem type
        problem = pulp.LpProblem('GameSchesule')

        # set variables
        h = pulp.LpVariable.dicts('home', ([0,1],K,K,W_I),0,1,'Integer')
        v = pulp.LpVariable.dicts('visitor', ([0,1],K,K,W_I),0,1,'Integer')
        home = pulp.LpVariable.dicts('new_home', ([0,1],K,K,W_I),0,1,'Integer')
        vis = pulp.LpVariable.dicts('new_vis', ([0,1],K,K,K,W_I),0,1,'Integer')
        home_vis = pulp.LpVariable.dicts('new_home_vis',([0,1],K,K,W_I),0,1,'Integer')

        # set objective function
        
        obj = [D[_from][to]*home[day][_from][to][w]for _from in K for to in K for w in W_I for day in [0,1]]
        obj += [D[_from][to]*vis[day][team][_from][to][w]for _from in K for to in K for w in W_I for day in [0,1]for team in I]
        obj += [D[_from][to]*home_vis[day][_from][to][w]for _from in K for to in K for w in W_I for day in [0,1]]
        if initial_position:
            obj += [D[initial_position[team]][team]*pulp.lpSum([h[0][team][j][0]for j in K])+D[initial_position[team]][to]*v[0][team][to][0]for team in K for to in K]
        obj = pulp.lpSum(obj)
        problem += obj

        # set constraints
        # 自リーグとは試合をしない
        for d in [0,1]:
            for w in W_I:
                for i in I:
                    for j in I:
                        problem += h[d][i][j][w] == 0
                        problem += v[d][i][j][w] == 0
                for i in J:
                    for j in J:
                        problem += h[d][i][j][w] == 0
                        problem += v[d][i][j][w] == 0
                for i in I:
                    for j in J:
                        # iがホームでjと試合をする＝jはビジター(i)で試合をする
                        problem += h[d][i][j][w]-v[d][j][i][w] == 0
                        problem += h[d][j][i][w]-v[d][i][j][w] == 0
        for i in I:
            # 総試合数
            problem += pulp.lpSum([h[0][i][j][w]+v[0][i][j][w]+h[1][i][j][w]+v[1][i][j][w] for j in J for w in W_I]) == self.total_game["i"]
            for w in W_I:
                # 1日一試合
                # パ・リーグ
                problem += pulp.lpSum([h[0][i][j][w]+v[0][i][j][w] for j in J]) == 1
                problem += pulp.lpSum([h[1][i][j][w]+v[1][i][j][w] for j in J]) == 1
        # セ・リーグ
        for j in J:
            for w in W_I:
                for day in [0,1]:
                    # 1日一試合
                    problem += pulp.lpSum([h[day][i][j][w]+v[day][i][j][w] for i in I]) == 1

        # 非線形な目的関数を線形にするために導入した変数に関する制約 
        for _from in J:
            for to in I:
                # 1週目の金曜日に行われる試合について
                problem +=(1-pulp.lpSum([h[1][to][j][0]for j in J])-v[0][to][_from][0]+home[1][_from][to][0]>=0)
                problem +=(pulp.lpSum([h[1][to][j][0]for j in J])-home[1][_from][to][0]>=0)
                problem +=(v[0][to][_from][0]-home[1][_from][to][0]>=0)
                for w in W_I[1:]:
                    # 2週目以降
                    problem += (1-pulp.lpSum([h[0][to][j][w]for j in J])-v[1][to][_from][w-1]+home[0][_from][to][w]>=0)
                    problem += (pulp.lpSum([h[0][to][j][w]for j in J])-home[0][_from][to][w]>=0)
                    problem += (v[1][to][_from][w-1]-home[0][_from][to][w]>=0)
                    problem += (1-pulp.lpSum([h[1][to][j][w]for j in J])-v[0][to][_from][w]+home[1][_from][to][w]>=0)
                    problem += (pulp.lpSum([h[1][to][j][w]for j in J])-home[1][_from][to][w]>=0)
                    problem += (v[0][to][_from][w]-home[1][_from][to][w]>=0)
        
        for team in I:
            for _from in J:
                for to in J:
                    # 1週目の金曜日に行われる試合について
                    problem += (1-v[1][team][to][0]-v[0][team][_from][0]+vis[1][team][_from][to][0]>=0)
                    problem += (v[1][team][to][0]-vis[1][team][_from][to][0]>=0)
                    problem += (v[0][team][_from][0]-vis[1][team][_from][to][0]>=0)
                    for w in W_I[1:]:  
                        # 2週目以降                     
                        problem += (1-v[0][team][to][w]-v[1][team][_from][w-1]+vis[0][team][_from][to][w]>=0)
                        problem += (v[0][team][to][w]-vis[0][team][_from][to][w]>=0)
                        problem += (v[1][team][_from][w-1]-vis[0][team][_from][to][w]>=0)
                        problem += (1-v[1][team][to][w]-v[0][team][_from][w]+vis[1][team][_from][to][w]>=0)
                        problem += (v[1][team][to][w]-vis[1][team][_from][to][w]>=0)
                        problem += (v[0][team][_from][w]-vis[1][team][_from][to][w]>=0)
        
        for _from in I:
            for to in J:
                # 1週目の金曜日に行われる試合について
                problem += (1-pulp.lpSum([h[1][_from][j][0]for j in J])-v[0][_from][to][0]+home_vis[1][_from][to][0]>=0)
                problem += (pulp.lpSum([h[1][_from][j][0]for j in J])-home_vis[1][_from][to][0]>=0)
                problem += (v[0][_from][to][0]-home_vis[1][_from][to][0]>=0)                    
                for w in W_I[1:]:
                    # 2週目以降
                    problem += (1-pulp.lpSum([h[0][_from][j][w]for j in J])-v[1][_from][to][w-1]+home_vis[0][_from][to][w]>=0)
                    problem += (pulp.lpSum([h[0][_from][j][w]for j in J])-home_vis[0][_from][to][w]>=0)
                    problem += (v[1][_from][to][w-1]-home_vis[0][_from][to][w]>=0)
                    problem += (1-pulp.lpSum([h[1][_from][j][w]for j in J])-v[0][_from][to][w]+home_vis[1][_from][to][w]>=0)
                    problem += (pulp.lpSum([h[1][_from][j][w]for j in J])-home_vis[1][_from][to][w]>=0)
                    problem += (v[0][_from][to][w]-home_vis[1][_from][to][w]>=0)                    

        # 1週間のうち同一カードは一回のみ
        for i in I:
            for j in J:
                for w in W_I:
                    problem += (h[0][i][j][w]+v[0][i][j][w]+h[1][i][j][w]+v[1][i][j][w] <= 1)

        # 試合数を均等に
        # パ・リーグ
        for i in I:
            hh = 0
            vv = 0
            for j in J:
                home_game    = pulp.lpSum([h[0][i][j][w]+h[1][i][j][w] for w in W_I])
                visitor_game = pulp.lpSum([v[0][i][j][w]+v[1][i][j][w] for w in W_I])
                # もう一方のリーグの全チームと一回づつ試合をする
                problem += home_game+visitor_game==1
                hh      += home_game
                vv      += visitor_game
            problem += hh == 3
            problem += vv == 3

        # セ・リーグ
        for j in J:
            hh = 0
            vv = 0
            for i in I:
                home_game    = pulp.lpSum([h[0][i][j][w]+h[1][i][j][w] for w in W_I])
                visitor_game = pulp.lpSum([v[0][i][j][w]+v[1][i][j][w] for w in W_I])
                hh += home_game
                vv += visitor_game
            problem += hh == 3
            problem += vv == 3

        # solve this problem
        if solver == 0:
            solver = pulp.PULP_CBC_CMD(msg=1, options=option, threads=num_of_process, maxSeconds=time_limit)
        elif solver == 1:
            solver = pulp.CPLEX_CMD()
        status = problem.solve(solver)

        return status, h, v


    def FinalPosition(self, h, v, league, type):
        """
        スケジュール最後の試合をどこで行なったか、と言う情報をリスト型で返す関数
        h      : ホームで行う試合についての情報を含んだ、0-1の値を持つ辞書
        v      : ビジターで行う試合についての情報を含んだ、0-1の値を持つ辞書
        league : 対象となるリーグ. 'p'/'s'
        type   : 'r_pre'/'i'/'r_post'(交流戦前/交流戦/交流戦後)
        """
        initial_position = [0]*12
        if type in ["r_pre","r_post"]:
            I = self.Teams[league]
            W = self.W[type]
            w_end = W[-1]
            for i in I:
                for j in I:
                    if h[1][i][j][w_end] == 1:
                        initial_position[i] = i
                    elif v[1][i][j][w_end] == 1:
                        initial_position[i] = j
        else:
            I = self.Teams['p']
            J = self.Teams['s']
            W = self.W['i']
            w_end = W[-1]
            for i in I:
                for j in J:
                    if h[1][i][j][w_end] == 1:
                        initial_position[i] = i
                    elif v[1][i][j][w_end] == 1:
                        initial_position[i] = j
            for j in J:
                for i in I:
                    if h[1][i][j][w_end] == 1:
                        initial_position[j] = i
                    elif v[1][i][j][w_end] == 1:
                        initial_position[j] = j
        
        return initial_position



class Output(NPB):
    """
    Solveクラスで解いた問題を、見やすい形に整形して出力するクラス。
    各チームのスケジュールを管理するためのschesulesと言う変数を新たに定義している。
    """
    def __init__(self):
        super().__init__()
        self.schesules = {"r":dict(), "r_pre":dict(), "r_post":dict(), "i":dict()}
        self.DistMatrix()
        self.dists = dict()
    
    def getSchesule(self, status, h, v, game_type, league='p'):
        """
        status    : ソルバーできちんと解けたか
        h         : ホームで行う試合についての情報を含んだ、0-1の値を持つ辞書
        v         : ビジターで行う試合についての情報を含んだ、0-1の値を持つ辞書
        game_type : 'r_pre'/'i'/'r_post'(交流戦前/交流戦/交流戦後)
        league    : 対象となるリーグ(デフォルトはパ・リーグ)
        """
        if status < 0:
            print('infeasible')
            return
        elif status == 0:
            print('not solved')
            return
        I = self.Teams[league]
        W = self.W[game_type]
        if game_type in ["r_pre","r_post"]:
            J = I                              
        else:
            if league == 'p':
                J = self.Teams["s"]
            else:
                J = self.Teams['p']
        for i in I:
            if i not in self.schesules[game_type].keys():
                self.schesules[game_type][i] = []
                for j in J:
                    for w in W:
                        for day in [0,1]:
                            if h[day][i][j][w].value() == 1:
                                self.schesules[game_type][i].append((w,day,j,'HOME'))
                            if v[day][i][j][w].value() == 1:
                                self.schesules[game_type][i].append((w,day,j,'VISITOR'))
                self.schesules[game_type][i].sort()  
        if game_type == 'i':
            for j in J:
                if j not in self.schesules[game_type].keys():
                    self.schesules[game_type][j] = []
                for i in I:
                    for w in W:
                        for day in [0,1]:
                            if h[day][i][j][w].value() == 1:
                                self.schesules[game_type][j].append((w,day,i,'VISITOR'))
                            if v[day][i][j][w].value() == 1:
                                self.schesules[game_type][j].append((w,day,i,'HOME'))
                self.schesules[game_type][j].sort()

    def MergeRegularSchesule(self):
        """
        交流戦前後のスケジュールを一つのリストにmergeする関数
        """
        schesule = self.schesules['r']
        leagues = ['p','s']
        for league in leagues:
            I = self.Teams[league]
            for i in I:
                schesule[i] = self.schesules['r_pre'][i]+self.schesules['r_post'][i]
        
 
    def GamePerDay(self, w, d, league, game_type='r'):
        """
        週と曜日を指定した際に行われる試合を出力する関数。
        w         : 週
        d         : 曜日
        league    : 考えるリーグ
        game_type : 通常/交流戦
        """
        pycolor = color.pycolor
        schesule = self.schesules[game_type]
        if game_type == 'r':
            I = self.Teams[league]
            for i in I:
                for k in range(len(schesule[i])):
                    if schesule[i][k][0] == w and schesule[i][k][1]==d and schesule[i][k][-1] == 'HOME':
                        place = self.Teams_name[i]
                        print(self.stadium[i])
                        print(pycolor.GREEN+self.Teams_name[i]+pycolor.END+":"+pycolor.PURPLE+self.Teams_name[schesule[i][k][2]]+pycolor.END)
                    
        else:
            I = self.Teams['p']
            J = self.Teams['s']
            for i in I:
                for k in range(len(schesule[i])):
                    if schesule[i][k][0] == w and schesule[i][k][1]==d and schesule[i][k][-1] == 'HOME':
                        place = self.Teams_name[i]
                        print(self.stadium[i])
                        print(pycolor.GREEN+self.Teams_name[i]+pycolor.END+":"+pycolor.PURPLE+self.Teams_name[schesule[i][k][2]]+pycolor.END)
            for i in J:
                for k in range(len(schesule[i])):
                    if schesule[i][k][0] == w and schesule[i][k][1]==d and schesule[i][k][-1] == 'HOME':
                        place = self.Teams_name[i]
                        print(self.stadium[i])
                        print(pycolor.GREEN+self.Teams_name[i]+pycolor.END+":"+pycolor.PURPLE+self.Teams_name[schesule[i][k][2]]+pycolor.END)

    def GameSchesule(self):
        """
        一年間のスケジュールを通常->交流戦の順番で日付順に出力する関数。
        """
        for game_type in ['r','i']:
            for w in self.W[game_type]:
                for d in [0,1]:
                    for league in ['p','s']:
                        self.GamePerDay(w,d,league,game_type=game_type)

    def GameTable(self, i):
        """
        チームiの一年間のスケジュールを出力する関数
        """
        bar = '==='
        pycolor = color.pycolor
        print(bar+self.Teams_name[i]+bar)
        for game_type in ['r','i']:
            h = 0
            v = 0
            if game_type == 'r':
                print('===通常試合===')
            else:
                print('===交流戦===')

            if game_type not in self.schesules.keys():
                print('None')
                continue

            for o in self.schesules[game_type][i]:
                if o[1] == 0:
                    day='(火)'
                else:
                    day = '(金)'
                if o[-1] == "HOME":
                    print(str(o[0]+1)+pycolor.GREEN+self.Teams_name[o[2]]+pycolor.END+day)
                    h += 1
                else:
                    print(str(o[0]+1)+pycolor.PURPLE+self.Teams_name[o[2]]+pycolor.END+day)
                    v += 1

            print("home:{}\nvisitor:{}".format(h,v))
    
    def GameTables(self):
        """
        全チームの一年間のスケジュールを順番に出力する関数
        """
        for i in range(12):
            self.GameTable(i)

    def CalcDist(self, team, type):
        """
        通常->交流戦
        交流戦->通常
        に切り替わるタイミングでの移動距離を計算する関数
        """
        post_stadium = None
        cur_stadium = None
        schesule_r = self.schesules['r'][team]
        schesule_i = self.schesules['i'][team]

        if type == 1:
            if schesule_i[0][-1] == 'HOME':
                cur_stadium = team
            else:
                cur_stadium = schesule_i[0][2]
            if schesule_r[9][-1] == 'HOME':
                post_stadium = team
            else:
                post_stadium = schesule_r[9][2]
        
        else:
            if schesule_i[-1][-1] == 'HOME':
                cur_stadium = team
            else:
                cur_stadium = schesule_i[-1][2]
            if schesule_r[10][-1] == 'HOME':
                post_stadium = team
            else:
                post_stadium = schesule_r[10][2]  

        return self.D[post_stadium][cur_stadium]                

    def TotalDist(self, team):
        """
        teamが一年間に移動した距離を計算・出力する関数
        """
        post_stadium = None
        cur_stadium = None
        total_dist = 0 
        D = self.D

        for game_type in ['r','i']:
            schesule = self.schesules[game_type][team]
            if schesule[0][-1] == 'HOME':
                post_stadium = team
            else:
                post_stadium = schesule[0][2]

            for t in range(1, len(schesule)):
                if schesule[t][-1] == 'HOME':
                    cur_stadium = team
                else:
                    cur_stadium = schesule[t][2]
                total_dist += D[post_stadium][cur_stadium]
                post_stadium = cur_stadium
        total_dist += self.CalcDist(team,1)+self.CalcDist(team,0)
        self.dists[team] = total_dist
        output = "{} : {}km".format(self.Teams_name[team], total_dist)
    
        return output
    
    def TotalDists(self):
        """
        全球団の年間の総移動距離を順に出力する関数。
        """
        dists = dict()
        for league in ['p', 's']:
            for team in self.Teams[league]:
                dists[team] = self.TotalDist(team)
        return dists

    def Ranking(self):
        """
        移動距離を多いほうから順番に出力する関数。
        """
        dists = list(self.dists.items())
        dists.sort(key=lambda x:x[1],reverse=True)
        for v in dists:
            i,d = v
            print(self.Teams_name[i]+':{}km'.format(d))

    def Plot(self, game_type, league):
        """
        各チームの移動経路を図示する関数
        """
        total_game = self.total_game[game_type]
        schesule = self.schesules[game_type]
        route_x = []
        route_y = []
        fig, axes= plt.subplots(3, 2)
        row = col = 0
        for team in self.Teams[league]:
            for k in range(total_game):
                _, _, j, stadium = schesule[team][k]
                if stadium == 'VISITOR':
                    route_x.append(self.coordinates[j][1])
                    route_y.append(self.coordinates[j][0])
                else:
                    route_x.append(self.coordinates[team][1])
                    route_y.append(self.coordinates[team][0])
            axes[row, col].plot(route_x, route_y, 'o-')
            axes[row,col].set_title(self.Teams_name[team])
            if row <= 1:
                row += 1
            elif col <= 0:
                col += 1
                row = 0
            route_x = []
            route_y = []
        save_dir = "./result/"
        plt.savefig(os.path.join(save_dir,'{}_{}.png'.format(game_type,league)))

    def Visualize(self):
        """
        全チーム、全試合形式の移動経路をプロット
        """
        for game_type in ['r','i']:
            for league in ['p','s']:
                self.Plot(game_type,league)
