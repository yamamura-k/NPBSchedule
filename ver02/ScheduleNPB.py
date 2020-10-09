from utils import color

import os
import math
import pulp
from matplotlib import pyplot as plt
import japanize_matplotlib


class NPB():
    """
    This is a class to define some basic variables and functions.
    """
    def __init__(self):

        self.S          = dict()
        self.total_game = dict()
        self.Teams      = dict()
        self.lb         = dict()
        self.ub         = dict()

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
        self.K           = self.Teams['p']+self.Teams['s']

        self.S['r']      = [s for s in range(42)]
        self.S["r_pre"]  = [s for s in range(10)]
        self.S["r_post"] = [s for s in range(32)]
        self.S["i"]      = [s for s in range(6)]

        self.total_game['r']      = 42
        self.total_game['r_pre']  = 10
        self.total_game['r_post'] = 32
        self.total_game['i']      = 6

        self.lb["r_pre"]  = 1
        self.ub["r_pre"]  = 1
        self.lb["r_post"] = 3
        self.ub["r_post"] = 4
        self.lb["i"]      = 0
        self.ub["i"]      = 1

        self.D = [[0]*12 for _ in range(12)]
        self.DistMatrix()
    
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
    This is a class to compute schedules with minimized distance
    """
    def __init__(self) -> None:
        super().__init__()

    def Solve(self, game_type, league='p', timeLimit=None, solverName=None, threads=1, option=[], initialPosition=None, bestObj=2**30):
        """
        This is a function to solve 0-1 integer problem which aim to compute suchedule with minimized distance.

        Parameters
        ----------
        game_type  : str
            The type of played game.
            Regular Game before inter game : 'r_pre'
            Regular Game after inter game  : 'r_post'
            Inter league                   : 'i' 
        league     : str
            League name 
            Pacific league : 'p'
            Central league : 's'
        timeLimit  : int
            Time limit for solver in seconds.
        solverName : int
            Solver's name you use
            0 : CBC
            1 : CPLEX
        threads    : int
            Threads for solver(default : 1)
        options    : list
            Options for solver (default : [])
        initialPosition : list
            Initial position of every team (default : None)
        bestObjective : int
            Best objective value of this problem we found before (default : 2**30)

        Returns
        -------
        status    : int
            Status of solved problem
            1  : Optimal
            0  : Not solved
            -1 : Infeasible
            -2 : Unbounded
            -3 : Undefined
        objective : int
            Objective value of solved problem
        v         : list
            Solution of this problem.
        """
        # 定数
        I = self.Teams[league]
        S = self.S[game_type]
        D = self.D
        if game_type == 'i':
            I = self.K
        total_game = self.total_game[game_type]

        # 問題の宣言
        problem = pulp.LpProblem('scheduling', pulp.LpMinimize)
        # 変数の生成
        v = pulp.LpVariable.dicts('v',(S,I,I),0,1,'Integer')
        e = pulp.LpVariable.dicts('e',(S,I,I,I),0,1,'Integer')

        # 目的関数の設定
        obj = pulp.lpSum([D[j][k]*e[s][i][j][k] for i in I for j in I for k in I for s in S])
        if initialPosition:
            for i in I:
                obj += pulp.lpSum([D[initialPosition[i]][j]*v[0][i][j]for j in I])
        problem += obj

        # 制約式を入れる

        # 目的関数値が改善された時だけ答えを出力してもらう。
        problem += obj <= bestObj

        for i in I:
            for j in I:
                for k in I:
                    for s in S[1:]:
                        # e[s][i][j][k]が定義を満たすように制約を入れる
                        problem += 1-v[s-1][i][j]-v[s][i][k]+e[s][i][j][k] >= 0
                        problem += v[s-1][i][j]-e[s][i][j][k] >= 0
                        problem += v[s][i][k]-e[s][i][j][k] >= 0
        for s in S:
            for i in I:
                # 垂直に足して見てね！パワポの制約⑦
                problem += pulp.lpSum([v[s][j][i] for j in I])<=2
            
        for i in I:
            J = list(set(I)-{i})
            for s in S:
                # v[s][i][i]の決め方。パワポで言う制約①
                problem += v[s][i][i] - pulp.lpSum([v[s][j][i] for j in J]) == 0

        
        for i in I:
            J = list(set(I)-{i})
            # 総試合数に関する制約。パワポで言う制約②
            problem += pulp.lpSum([v[s][i][j]for j in I for s in S]) == total_game
            # ホームゲームとビジターゲームの試合数を揃える。パワポで言う制約③
            problem += (pulp.lpSum([v[s][i][j] for s in S for j in J])
                      - pulp.lpSum([v[s][i][i] for s in S]) == 0)
        
        for i in I:
            for j in I:
                # 各対戦カードにおけるホームとビジターの試合数をなるべく揃える。パワポで言う制約④
                if i != j:
                    problem += pulp.lpSum([v[s][i][j] for s in S])-pulp.lpSum([v[s][j][i] for s in S]) <= 1
                    problem += pulp.lpSum([v[s][i][j] for s in S])-pulp.lpSum([v[s][j][i] for s in S]) >= -1
                    problem += pulp.lpSum([v[s][i][j] for s in S]) <= self.ub[game_type]
                    problem += pulp.lpSum([v[s][i][j] for s in S]) >= self.lb[game_type]
        
        for s in S:
            for i in I:
                # 1日必ず1試合する。パワポで言う制約⑤
                problem += pulp.lpSum([v[s][i][j]for j in I]) == 1           
        
        for s in S[:-2]:
            for i in I:
                for j in I:
                    # 連戦はしない。パワポで言う制約⑥
                    if i!=j:
                        problem += pulp.lpSum([v[t][i][j]+v[t][j][i]for t in range(s,s+3)]) <= 1
        
        for s in S[:-2]:
            for i in I:
                # ホームは連続二連ちゃんまで！パワポの制約⑧
                problem += pulp.lpSum([v[t][i][i]for t in range(s,s+3)]) <= 2
        
        if game_type == 'i':
            L = self.Teams['p']
            J = self.Teams['s']
            for s in S:
                for i in L:
                    # 自分のリーグに属するチームとは試合を行わないと言う制約。パワポの制約⑨
                    for j in L:
                        if i != j:
                            problem += v[s][i][j] == 0
                    # もう一方のリーグのチームと一回ずつ試合をするという制約。パワポの制約11
                    for j in J:
                        problem += v[s][i][j] <= (1-pulp.lpSum([v[t][j][i]for t in range(s)]))
                for i in J:
                    # 自分のリーグに属するチームとは試合を行わないと言う制約。パワポの制約⑨
                    for j in J:
                        if i != j:
                            problem += v[s][i][j] == 0
                    # もう一方のリーグのチームと一回ずつ試合をするという制約。パワポの制約11
                    for j in L:
                        problem += v[s][i][j] <= (1-pulp.lpSum([v[t][j][i]for t in range(s)]))

            # ビジターで試合をしている時はホームで試合をしてはいけない。パワポの制約⑩
            # v[s][i][i]=1かv[s][i][j]=1の何か一方が成立する
            for s in S:
                for i in L:
                    problem += v[s][i][i]+pulp.lpSum([v[s][i][j]for j in J]) <= 1
                for j in J:
                    problem += v[s][j][j]+pulp.lpSum([v[s][j][i]for i in L]) <= 1

        # solverの設定
        # デフォルトは cbc solver
        if solverName == 0:
            solver = pulp.PULP_CBC_CMD(msg=1, threads=threads,options=option, maxSeconds=timeLimit)
        elif solverName == 1:
            solver = pulp.CPLEX_CMD(msg=1, timeLimit=timeLimit,options=option, threads=threads)
        
        status = problem.solve(solver)

        return status, pulp.value(problem.objective), v

    def FinalPosition(self, e, league, type):
        """
        スケジュール最後の試合をどこで行なったか、と言う情報をリスト型で返す関数

        Parameters
        ----------
        e      : dict
            Solution of solved problem
        league : str
            対象となるリーグ. 'p'/'s'
        type   : str
            'r_pre'/'i'/'r_post'(交流戦前/交流戦/交流戦後)

        Returns
        -------
        initial_position : list
            List of final position of each teams.
        """
        initial_position = [0]*12
        if type in ["r_pre","r_post"]:
            I = self.Teams[league]
            S = self.S[type]
            s_end = S[-1]
            for i in I:
                for j in I:
                    if e[s_end][i][j] == 1:
                        initial_position[i] = i
                        initial_position[j] = i
        else:
            I = self.K
            S = self.S[type]
            s_end = S[-1]
            for i in I:
                for j in I:
                    if e[s_end][i][j] == 1:
                        initial_position[i] = i
                        initial_position[j] = i
        
        return initial_position


class Output(NPB):
    """
    This is a class to output schedules / total distances / pictures of paths 
    """
    def __init__(self) -> None:
        super().__init__()
        self.schedules = {'all':{i:[]for i in self.K},'r':{i:[]for i in self.K},
                          'r_pre':{i:[]for i in self.K},'r_post':{i:[]for i in self.K},
                          'i':{i:[]for i in self.K}}
        self.dists     = dict()
    
    def getSchedule(self, v, game_type, league='p'):
        """
        This is a function to get schedules of each team.

        Parameters
        ----------
        v : dict
            Solution of the problem
        game_type  : str
            The type of played game.
            Regular Game before inter game : 'r_pre'
            Regular Game after inter game  : 'r_post'
            Inter league                   : 'i'
        league     : str
            League name 
            Pacific league : 'p'
            Central league : 's'
        Returns
        -------
        None         
        """
        I = self.Teams[league]
        if game_type == 'i':
            I = self.K
        for s in self.S[game_type]:
            for i in I:
                for j in I:
                    if v[s][i][j].value() == 1:
                        if i != j:
                            self.schedules[game_type][i].append((s,j,'visitor'))
                            self.schedules[game_type][j].append((s,i,'home'))

    def getWholeSchedule(self):
        """
        Get whole schedule for each team
        """
        for i in self.K:
            game_num = 1
            for game_type in ['r_pre','i','r_post']:
                for v in self.schedules[game_type][i]:
                    self.schedules['all'][i].append((game_num,v[1],v[2]))

#===========================================================#
# パパッとデバッグ    
    def checkAnswer(self):
        """
        Debugging tool.
        Display tuple of (game, team) if the team has annomary schedule.
        After that, print sum of home/visitor games and total nomber of games
        If we passed all of these tests, we get a messeage 'test1 passed'
        """
        ok = True
        print('Check total number of games')
        for game in ['r_pre','r_post','i']:
            for i in range(12):
                if len(self.schedules[game][i]) != self.total_game[game]:
                    ok = False
                    print('rethink your formulation!!')
                    print(game,i)
                x = 0
                y = 0
                for v in self.schedules[game][i]:
                    if v[-1]=='home':
                        x += 1
                    else:
                        y += 1
                print(game)
                print(x,y,x+y)

        if ok:
            print('test1 passed')

    def CountGames(self, team):
        """
        debugging tool
        試合数が意図通りかどうか確かめるために試合数を計算する関数
        Parameters
        ----------
        team : int
            Team ID
        """
        schedule_r = self.schedules['r_post'][team]
        schedule_i = self.schedules['i'][team]
        game_number_i = dict()
        game_number_r = dict()
        for v in schedule_i:
            j = v[-2]
            if j in game_number_i.keys():
                if v[-1] == 'home':
                    game_number_i[j][0] += 1
                else:
                    game_number_i[j][1] += 1
            else:
                game_number_i[j] = [0,0]
                if v[-1] == 'home':
                    game_number_i[j][0] += 1
                else:
                    game_number_i[j][1] += 1

        for v in schedule_r:
            j = v[-2]
            if j in game_number_r.keys():
                if v[-1] == 'home':
                    game_number_r[j][0] += 1
                else:
                    game_number_r[j][1] += 1
            else:
                game_number_r[j] = [0,0]
                if v[-1] == 'home':
                    game_number_r[j][0] += 1
                else:
                    game_number_r[j][1] += 1
        print('通常試合')
        for j in game_number_r:
            print(*game_number_r[j], sum(game_number_r[j]))

        print('交流戦')
        for j in game_number_i:
            print(*game_number_i[j], sum(game_number_i[j])) 

#======================================================================#
# 結果表示用。        

    def MergeRegularSchedule(self):
        """
        交流戦前後のスケジュールを一つのリストにmergeする関数
        """
        schedule = self.schedules['r']
        leagues = ['p','s']
        for league in leagues:
            I = self.Teams[league]
            for i in I:
                schedule[i] = self.schedules['r_pre'][i]+self.schedules['r_post'][i]
        
 
    def GameTable(self, i):
        """
        チームiの一年間のスケジュールを出力する関数
        Parameters
        ----------
        i : int
            Team ID
        Returns
        -------
        None
        (Display schedule as standard output)
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

            if game_type not in self.schedules.keys():
                print('None')
                continue

            for o in self.schedules[game_type][i]:
                if o[-1] == "home":
                    print(str(o[0]+1)+pycolor.GREEN+self.Teams_name[o[-2]]+pycolor.END)
                    h += 1
                else:
                    print(str(o[0]+1)+pycolor.PURPLE+self.Teams_name[o[-2]]+pycolor.END)
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
        Parameters
        ----------
        team : int
            Team ID
        type   : str
            'r_pre'/'i'/'r_post'(交流戦前/交流戦/交流戦後)
        Returns
        -------
        self.D[post_stadium][cur_stadium] : float
            Calculated distance
        """
        post_stadium = None
        cur_stadium = None
        schedule_r = self.schedules['r'][team]
        schedule_i = self.schedules['i'][team]

        if type == 1:
            if schedule_i[0][-1] == 'home':
                cur_stadium = team
            else:
                cur_stadium = schedule_i[0][-2]
            if schedule_r[9][-1] == 'home':
                post_stadium = team
            else:
                post_stadium = schedule_r[9][-2]
        
        else:
            if schedule_i[-1][-1] == 'home':
                cur_stadium = team
            else:
                cur_stadium = schedule_i[-1][-2]
            if schedule_r[10][-1] == 'home':
                post_stadium = team
            else:
                post_stadium = schedule_r[10][-2]  

        return self.D[post_stadium][cur_stadium]                

    def TotalDist(self, team):
        """
        teamが一年間に移動した距離を計算・出力する関数
        Parameters
        ----------
        team : int
            Team ID
        Returns
        -------
        output : str
            Total moving-distance of each team as strings in followed format :
            "{} : {}km".format(self.Teams_name[team], total_dist)
        """
        post_stadium = None
        cur_stadium = None
        total_dist = 0 
        D = self.D

        for game_type in ['r','i']:
            schedule = self.schedules[game_type][team]
            if schedule[0][-1] == 'home':
                post_stadium = team
            else:
                post_stadium = schedule[0][-2]

            for t in range(1, len(schedule)):
                if schedule[t][-1] == 'home':
                    cur_stadium = team
                else:
                    cur_stadium = schedule[t][-2]
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
        Save directory is "./result/png/"
        Parameters
        ----------
        game_type  : str
            The type of played game.
            Regular Game before inter game : 'r_pre'
            Regular Game after inter game  : 'r_post'
            Inter league                   : 'i'
        league     : str
            League name 
            Pacific league : 'p'
            Central league : 's'
        Returns
        -------
        None(save image file as .png)        
        """
        total_game = self.total_game[game_type]
        schedule = self.schedules[game_type]
        
        route_x = []
        route_y = []
        
        if game_type=='r':
            I = self.Teams[league]
            fig, axes = plt.subplots(3, 2)
            row_max   = 1
        else:
            I = self.Teams['p']+self.Teams['s']
            fig, axes = plt.subplots(6, 2)
            row_max   = 4
            league    = 'all'
        plt.subplots_adjust(wspace=0.4, hspace=0.6)

        row = col = 0

        for team in I:
            for k in range(total_game):
                if k >= len(schedule[team]):
                    break
                _, j, stadium = schedule[team][k]
                if stadium == 'visitor':
                    route_x.append(self.coordinates[j][1])
                    route_y.append(self.coordinates[j][0])
                else:
                    route_x.append(self.coordinates[team][1])
                    route_y.append(self.coordinates[team][0])
            axes[row, col].plot([self.coordinates[i][1]for i in range(6)],
                                [self.coordinates[i][0]for i in range(6)],'bo')

            axes[row, col].plot([self.coordinates[i][1]for i in range(6,12)],
                                [self.coordinates[i][0]for i in range(6,12)],'go')

            axes[row, col].plot(route_x, route_y, 'r-')
            axes[row,col].set_title(self.Teams_name[team])
            if row <= row_max:
                row += 1
            elif col <= 0:
                col += 1
                row = 0
            route_x = []
            route_y = []
        save_dir = "./result/png"
        plt.savefig(os.path.join(save_dir,'{}_{}.png'.format(game_type,league)))
        plt.close()

    def plotOnMap(self, team, game_type):
        """
        移動経路を日本地図上にプロットする関数
        Save directory is "./result/png/"
        
        Parameters
        ----------
        game_type  : str
            The type of played game.
            Regular Game before inter game : 'r_pre'
            Regular Game after inter game  : 'r_post'
            Inter league                   : 'i'
        league     : str
            League name 
            Pacific league : 'p'
            Central league : 's'
        Returns
        -------
        None(save image file as .png)     
        """
        # 定数の設定
        total_game = self.total_game[game_type]
        schedule = self.schedules[game_type][team]
        route_x = []
        route_y = []    
        from mpl_toolkits.basemap import Basemap
        # 地図の描画
        fig = plt.figure()
        m = Basemap(projection='lcc', lat_0 = 35.4, lon_0 = 136.7,
                    resolution = 'i', area_thresh = 0.1,
                    llcrnrlon=128., llcrnrlat=30.,
                    urcrnrlon=147., urcrnrlat=46.)
        # 各チームの本拠地をプロット
        # パ・リーグ
        x,y = m([self.coordinates[i][1]for i in range(6)],
                [self.coordinates[i][0]for i in range(6)])
        m.plot(x,y,'bo',markersize=5)
        # セ・リーグ
        x,y = m([self.coordinates[i][1]for i in range(6,12)],
                [self.coordinates[i][0]for i in range(6,12)]) 
        m.plot(x,y,'go',markersize=5)
        # 移動経路を求める
        for k in range(total_game):
            if k >= len(schedule):
                break
            _, j, stadium = schedule[k]
            if stadium == 'visitor':
                route_x.append(self.coordinates[j][1])
                route_y.append(self.coordinates[j][0])
            else:
                route_x.append(self.coordinates[team][1])
                route_y.append(self.coordinates[team][0])
        route_x,route_y = m(route_x, route_y)  
        # 移動経路の描画
        m.plot(route_x, route_y, 'r-')
        # 海岸線を描く、国境を塗る、海(背景)を塗る, 大陸を塗る
        m.drawcoastlines(linewidth=0.25)
        m.drawcountries(linewidth=0.25)
        m.drawmapboundary(fill_color='skyblue')
        m.fillcontinents(color='bisque',lake_color='skyblue')
        # 画像を保存
        save_dir = "./result/png"
        plt.savefig(os.path.join(save_dir,'{}_{}.png'.format(game_type,team)))
        plt.close()

    def Visualize(self):
        """
        全チーム、全試合形式の移動経路をプロット
        """
        for game_type in ['r','i']:
            for league in ['p','s']:
                self.Plot(game_type,league)
        for game_type in ['r','i']:
            for team in range(12):
                self.plotOnMap(team, game_type)
