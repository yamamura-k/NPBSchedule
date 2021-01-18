from ScheduleNPB import NPB, Output

import random
from deap import creator, base, tools

# 現状Feasible Solution が出てきてないので何らかの修正が必要。
# 以下未実装 or 要修正
# 連続でホームを使っていいのは2回まで
# どのチームとも同じくらい試合をしているか
# ホーム・ビジターの試合数は一緒にする

class GA(NPB):

    def __init__(self, game_type) -> None:
        super().__init__()
        self.game_type = game_type
        self.teamNumber = 6
        if game_type == 'i':
            self.teamNumber = 12
        self.tableSize = self.total_game[game_type]*self.teamNumber
    
    def isFeasible0(self, ind):
        """IPで入れた制約を満足するかどうか判定する
        """
        eval = 0
        game_type = self.game_type
        total_game = self.total_game[game_type]
        teamNumber = self.teamNumber
        teams = []
        index = 0
        tableSize = self.tableSize
        # 遺伝子が各チームの対戦表を表すように分割
        # [一日目, 二日目, ..., 最終日]みたいな感じで入ってるとする。 
        while index < len(ind):
            teams.append(ind[index:index+tableSize])
            index += tableSize

        for team in teams:
            # 試合数が一致しないとだめ
            if sum(team) != total_game:
                return 0
        return 1

    def isFeasible1(self, ind):
        """IPで入れた制約を満足するかどうか判定する
        """
        eval = 0
        game_type = self.game_type
        total_game = self.total_game[game_type]
        teamNumber = self.teamNumber
        teams = []
        index = 0
        tableSize = self.tableSize
        # 遺伝子が各チームの対戦表を表すように分割
        # [一日目, 二日目, ..., 最終日]みたいな感じで入ってるとする。 
        while index < len(ind):
            teams.append(ind[index:index+tableSize])
            index += tableSize
        for team in teams:
            # 一日1試合
            for start in range(0, tableSize-teamNumber, teamNumber):
                if sum(team[start:start+teamNumber]) != 1:
                    eval -= 1
                    return 0
        return 1

    def isFeasible2(self, ind):
        """IPで入れた制約を満足するかどうか判定する
        """
        eval = 0
        game_type = self.game_type
        total_game = self.total_game[game_type]
        teamNumber = self.teamNumber
        teams = []
        index = 0
        tableSize = self.tableSize
        # 遺伝子が各チームの対戦表を表すように分割
        # [一日目, 二日目, ..., 最終日]みたいな感じで入ってるとする。 
        while index < len(ind):
            teams.append(ind[index:index+tableSize])
            index += tableSize

        #print('step 1 passed')
        # 対戦相手とちゃんと試合をしているか？
        for day in range(0, tableSize, teamNumber):
            for i in range(teamNumber):
                for j in range(teamNumber):
                    if i==j:
                        continue
                    else:
                        if teams[i][j+day]== 1 and teams[j][j+day] == 0:
                            eval -= 1
                            #return 0
        return eval
        #print('step 2 passed')


    def isFeasible3(self, ind):
        """IPで入れた制約を満足するかどうか判定する
        """
        eval = 0
        game_type = self.game_type
        total_game = self.total_game[game_type]
        teamNumber = self.teamNumber
        teams = []
        index = 0
        tableSize = self.tableSize
        # 遺伝子が各チームの対戦表を表すように分割
        # [一日目, 二日目, ..., 最終日]みたいな感じで入ってるとする。 
        while index < len(ind):
            teams.append(ind[index:index+tableSize])
            index += tableSize

        # ホーム・ビジターの試合数は一緒にする
        for i, team in enumerate(teams):
            home = sum([team[i+step]for step in range(0, tableSize ,teamNumber)])
            if 2*home != total_game:
                eval -= 1
                #return 0
        #print('step 3 passed')
        return eval

    def totalDist(self, ind):
        eval = 0
        game_type = self.game_type
        total_game = self.total_game[game_type]
        teamNumber = self.teamNumber
        teams = []
        index = 0
        tableSize = self.tableSize
        # 遺伝子が各チームの対戦表を表すように分割
        # [一日目, 二日目, ..., 最終日]みたいな感じで入ってるとする。 
        while index < len(ind):
            teams.append(ind[index:index+tableSize])
            index += tableSize
        for team in teams:
            pre = team[0:teamNumber].index(1)
            for i in range(teamNumber-1, tableSize ,teamNumber):
                tmp = team[i:i+teamNumber]
                eval += self.D[pre][tmp.index(1)]
        return -eval

    def evalFunc(self, ind):
        return self.isFeasible0(ind),self.isFeasible1(ind),self.isFeasible2(ind),
        #self.isFeasible3(ind)

    def GA(self, CXPB=0.5, MUTPB=0.5, NGEN=500):
        """Main function to execute genetic algorithm

        Parameters
        ----------
        CBPX  : float
            Probability of crossover
            default : 0.5
        MUTPB : float
            Probability of mutation
            default : 0.2
        NGEN : int
            Number of populations
            default : 10

        Returns
        -------
        Value of objective function
        """
        geneLength = self.tableSize*self.teamNumber
        # 適応度を定義する
        creator.create("FitnessMax", base.Fitness, weights=(1.0,1.0,1.0,))

        # 個体を定義する。
        # 各個体の適応度は上記適応度によって判断される。
        creator.create("Individual", list, fitness=creator.FitnessMax)

        # 必要なものを作る
        toolbox = base.Toolbox()
        toolbox.register("rand", random.randint, 0, 1)# 引数なしでrandom.randintを使えるようにした
        toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.rand, geneLength)# 個体を作成
        toolbox.register("population", tools.initRepeat, list, toolbox.individual)# 個体群を作る

        toolbox.register("evaluate", self.evalFunc)# 評価関数の呼び方を変更
        toolbox.register("mate", tools.cxTwoPoint)# 交叉のさせ方
        toolbox.register("mutate", tools.mutFlipBit, indpb=0.05)# 突然変異のさせ方
        toolbox.register("select", tools.selTournament, tournsize=3)# 個体の選び方
        
        # 実際に問題を解き始める
        # まずは下準備
        random.seed(64)

        pop = toolbox.population(n=300)# 個体群を作成

        fitnesses = list(map(toolbox.evaluate, pop))# 各個体の適応度をリストに格納
        # オブジェクトに値を設定
        for ind, fit in zip(pop, fitnesses):
            ind.fitness.values = fit

        # GA
        for g in range(NGEN):
            # 子供たち
            offspring = toolbox.select(pop, len(pop))# 現在の個体群からいくつか選択
            offspring = list(map(toolbox.clone, offspring))# 選んだ個体を複製してリストに格納

            for child1, child2 in zip(offspring[::2], offspring[1::2]):
                # 確率的に交叉
                if random.random() < CXPB:
                    toolbox.mate(child1, child2)
                    del child1.fitness.values
                    del child2.fitness.values

            for mutant in offspring:
                # 確率的に突然変異
                # 各遺伝子の0-1が入れ替わる確率はindpbで与えられる・
                if random.random() < MUTPB:
                    toolbox.mutate(mutant)
                    del mutant.fitness.values
            # 無効な(?)個体に評価関数を作用させる
            invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
            fitnesses = map(toolbox.evaluate, invalid_ind)
            
            # 無効な(?)個体に適応度を設定する
            for ind, fit in zip(invalid_ind, fitnesses):
                ind.fitness.values = fit
            # 子孫を新たな個体群とする
            pop[:] = offspring
            if g%100:
                print(tools.selBest(pop, 1)[0].fitness.values)
            if tools.selBest(pop, 1)[0].fitness.values==(0,0,0):
                break
        
        best_ind = tools.selBest(pop, 1)[0]
        # 読みやすい出力
        print("Best individual is %s, %s" % (best_ind, best_ind.fitness.values))
        #print(len(best_ind))
        return best_ind
class OutputGA(Output):

    def __init__(self) -> None:
        super().__init__()