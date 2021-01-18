from ScheduleNPB import Generate, Output
from LocalSearch import convert, calcDist
from localSearch import two_Opt
from utils.utils import stop_watch
from time import time

def generator(game_type,
              league='ps',
              timeLimit=None,
              solverName=None,
              threads=1,
              option=[],
              initialPosition=None,
              maxIter=2500):
    gen = Generate()
    for _ in range(maxIter):
        status, v = gen.GenerateFeasibleSolution(game_type,
              league=league,
              timeLimit=timeLimit,
              solverName=solverName,
              threads=threads,
              option=option,
              initialPosition=initialPosition)
        yield v

def listToDict(data, game_type, league, output):
    I = output.Teams[league]
    S = output.S[game_type]

    v = dict()
    for s in S:
        v[s] = dict()
        for i in I:
            v[s][i] = dict()
            for j in I:
                v[s][i][j] = data[s][i][j]
    
    return v
def main():
    for type in ['r_pre','r_post']:
        for league in ['p','s']:
            origin    = []
            two_opt   = []
            gen_time  = []
            opt_time  = []
            same_org  = []
            same_opt  = []
            iteration = 0
            type   = 'r_post'
            league = 'p'
            best_obj = float('inf')
            best_sol = None
            start0 = time()
            for solution in generator(type,league=league,solverName=0):
                start1 = time()
                gen_time.append(start1-start0)
                iteration += 1
                print(f'iter       : {iteration}')
                output = Output()
                D = output.D
                output.getSchedule(solution, 'r_post', league='p')
                data = convert(type, league, output)
                dist1 = calcDist(data, type, league, output)
        
                start1 = time()
                data = two_Opt.two_Opt(data)
                start0 = time()
        
                opt_time.append(start0-start1)
                dist2 = calcDist(data, type, league, output)
                if dist2 == 0:
                    start0 = time()
                    continue
                print(f'diff       : {dist2-dist1}')
                if dist1==dist2:
                    same_org.append(dist1)
                    same_opt.append(dist2)
                else:
                    print(f'original  : {dist1}')
                    print(f'with 2opt : {dist2}\n')
                    origin.append(dist1)
                    two_opt.append(dist2)
                if dist2 < best_obj:
                    best_sol = data
                    best_obj = dist2
                start0 = time()
            output = Output()
            v = listToDict(best_sol, type, league, output)
            output.getSchedule(v, type, league=league)
            output.MergeRegularSchedule()
            output.GameTables()
            print(best_obj)
            print(sum(gen_time)/len(gen_time))
            print(sum(opt_time)/len(opt_time))
            print(len(same_org), len(origin))
            from matplotlib import pyplot as plt
            fig = plt.figure()
            plt.scatter(same_org, same_opt, color='r')
            plt.scatter(origin, two_opt, color='b')
            plt.savefig(f'{league}_{type}_1.png')

def main2():
    origin    = []
    two_opt   = []
    gen_time  = []
    opt_time  = []
    same_org  = []
    same_opt  = []
    iteration = 0
    type   = 'r_post'
    league = 'p'
    best_obj = float('inf')
    best_sol = None
    start0 = time()
    for solution in generator(type,league=league,solverName=0):
        start1 = time()
        gen_time.append(start1-start0)
        iteration += 1
        print(f'iter       : {iteration}')
        output = Output()
        D = output.D
        output.getSchedule(solution, 'r_post', league='p')
        data = convert(type, league, output)
        dist1 = calcDist(data, type, league, output)

        start1 = time()
        data = two_Opt.two_Opt(data, storategy='first')
        start0 = time()

        opt_time.append(start0-start1)
        dist2 = calcDist(data, type, league, output)
        if dist2 == 0:
            start0 = time()
            continue
        print(f'diff       : {dist2-dist1}')
        if dist1==dist2:
            same_org.append(dist1)
            same_opt.append(dist2)
        else:
            print(f'original  : {dist1}')
            print(f'with 2opt : {dist2}\n')
            origin.append(dist1)
            two_opt.append(dist2)
        if dist2 < best_obj:
            best_sol = data
            best_obj = dist2
        start0 = time()
    output = Output()
    v = listToDict(best_sol, type, league, output)
    output.getSchedule(v, type, league=league)
    output.MergeRegularSchedule()
    output.GameTables()
    print(best_obj)
    print(sum(gen_time)/len(gen_time))
    print(sum(opt_time)/len(opt_time))
    print(len(same_org), len(origin))
    from matplotlib import pyplot as plt
    fig = plt.figure()
    plt.scatter(same_org, same_opt, color='r')
    plt.scatter(origin, two_opt, color='b')
    plt.savefig('tmp2.png')

if __name__ == "__main__":
    main()
