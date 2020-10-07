import ScheduleNPB
from utils.utils import Load, preserve

from argparse import ArgumentParser

def Solve(num_process=1,options=[],time_limit=None,solver=0):
    """
    """
    with open('bestObjective.txt', 'r+') as f:
        best = [float(s.strip()) for s in f.readlines()]
        initial_position = dict()
        sol = ScheduleNPB.Solve()
        leagues = ['p', 's']
        index = 0

        for league in leagues:
            status, obj, e = sol.Solve("r_pre",league=league,threads=num_process,timeLimit=time_limit,solverName=solver,option=options,bestObj=best[index])
            if status==1:
                preserve(e,'r_pre_'+league)
                best[index] = min(best[index], float(obj))
            index += 1
            e = Load('r_pre_'+league+'.pkl')
            initial_position[league] = sol.FinalPosition(e, league, 'r_pre')

        position_for_inter = sol.Merge(initial_position['p'],initial_position['s'])
        status, obj, e = sol.Solve('i', initialPosition = position_for_inter, threads=num_process,timeLimit=time_limit,solverName=solver,option=options,bestObj=best[index])
        if status==1:
            preserve(e,'i_ps')
            best[index] = min(best[index], float(obj))
        index += 1
        e = Load('i_ps.pkl')
        initial_position['r'] = sol.FinalPosition(e, None, 'i')
        
        for league in leagues:
            status, obj, e = sol.Solve("r_post",league=league,initialPosition=initial_position['r'],threads=num_process,timeLimit=time_limit,solverName=solver,option=options,bestObj=best[index])
            if status==1:
                preserve(e,'r_post_'+league)     
                best[index] = min(best[index], float(obj))
            index += 1

    f = open('bestObjective.txt', 'w')
    best = list(map(lambda x: str(x)+'\n', best))
    f.writelines(best)
    f.close()

def partSolve(num_process=1,options=[],time_limit=None,solver=0):
    initial_position = dict()
    sol = ScheduleNPB.Solve()
    leagues = ['p', 's']

    for league in leagues:
        e = Load('r_pre_'+league+'.pkl')
        initial_position[league] = sol.FinalPosition(e, league, 'r_pre')

    position_for_inter = sol.Merge(initial_position['p'],initial_position['s'])
    status, e = sol.Solve('i', initialPosition = position_for_inter, threads=num_process,timeLimit=time_limit,solverName=solver,option=options)
    preserve(e,'i_ps')

def main(num_process=1,options=[],time_limit=None,solver=0):
    output = ScheduleNPB.Output()
    leagues = ['p', 's']

    Solve(num_process,options,time_limit=time_limit,solver=solver,option=options)
    
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
    #output.getWholeSchedule()
    print(len(output.schedules['all'][0]))
    output.MergeRegularSchedule()
    output.checkAnswer()
    dists = output.TotalDists()
    for team in range(12):
        print(dists[team])
    output.GameTables()
    #output.Visualize()

def argparser():
    parser = ArgumentParser()

    parser.add_argument(
        '-dbg','--debug',
        help='debug mode : if you want use debug mode, -dbg 1',
        default=False,
        dest='dbg',
        type=bool
    )

    parser.add_argument(
        '-t','--time',
        help='maximum time for solver in seconds.',
        default=None,
        dest='t',
        type=int
    )

    parser.add_argument(
        '-s','--solver',
        help='select solver to use.\n 0 : PULP_CBC_CMD\n 1 : CPLEX_CMD()',
        default=0,
        dest='s',
        type=int
    )

    parser.add_argument(
        '-th','--thread',
        help='number of threads',
        default=1,
        dest='th',
        type=int
    )

    parser.add_argument(
        '-par','--part',
        help='partly solve',
        default=False,
        dest='part',
        type=bool
    )

    return parser

if __name__ == "__main__":
    parser = argparser()
    args   = parser.parse_args()

    num_process = args.th
    limit = args.t
    solver = args.s

    if args.dbg:
        dbg_option = ['maxsol 1']
        #partSolve(num_process=num_process,options=dbg_option,time_limit=limit,solver=solver)
        #exit()
        main(num_process=num_process,options=dbg_option,time_limit=limit,solver=solver)
    else: 
        main(num_process=num_process,time_limit=limit,solver=solver)
