# -*- coding: utf-8 -*-
import ScheduleNPB
from utils.utils import Load, preserve

from argparse import ArgumentParser

def Solve(num_process=1,options=[],time_limit=None,solver=0):
    """
    This is a function of computing schedules with minimized traveling distance.
    Solutions are saved as .pkl files.
    Save directory path is "./result/pkl/"

    Parameters
    ----------
    num_process : int
        Number of threads.
        Default : 1
    options     : list
        Solve options
        Default : []
    time_limit  : int
        Maximum seconds for solver
        Default : None
    solver      : int
        Unique number of solver you use
        0 : CBC solver (default)
        1 : CPLEX
    Returns
    -------
    None
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
    """
    This is a function to compute post inter-league schedules.
    Solutions are saved as .pkl files.
    Save directory path is "./result/pkl/"

    Parameters
    ----------
    num_process : int
        Number of threads.
        Default : 1
    options     : list
        Solve options
        Default : []
    time_limit  : int
        Maximum seconds for solver
        Default : None
    solver      : int
        Unique number of solver you use
        0 : CBC solver (default)
        1 : CPLEX
    Returns
    -------
    None
    """
    initial_position = dict()
    sol = ScheduleNPB.Solve()
    leagues = ['p', 's']

    for league in leagues:
        e = Load('r_pre_'+league+'.pkl')
        initial_position[league] = sol.FinalPosition(e, league, 'r_pre')

    position_for_inter = sol.Merge(initial_position['p'],initial_position['s'])
    status, e = sol.Solve('i', initialPosition = position_for_inter, threads=num_process,timeLimit=time_limit,solverName=solver,option=options)
    preserve(e,'i_ps')


def argparser():
    parser = ArgumentParser()

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
    if args.sep:
        partSolve(num_process=num_process,time_limit=limit,solver=solver)
        exit()
    Solve(num_process=num_process,time_limit=limit,solver=solver)