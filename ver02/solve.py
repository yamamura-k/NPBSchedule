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
    initial_position = dict()
    sol = ScheduleNPB.Solve()
    leagues = ['p', 's']

    for league in leagues:
        status, obj, e = sol.Solve("r_pre",league=league,threads=num_process,timeLimit=time_limit,solverName=solver,option=options,initialSolution=True)
        if status==1:
            preserve(e,'r_pre_'+league)

        e = Load('r_pre_'+league+'.pkl')
        initial_position[league] = sol.FinalPosition(e, league, 'r_pre')

    position_for_inter = sol.Merge(initial_position['p'],initial_position['s'])
    status, obj, e = sol.Solve('i', initialPosition = position_for_inter, threads=num_process,timeLimit=time_limit,solverName=solver,option=options,initialSolution=True)
    if status==1:
        preserve(e,'i_ps')
    e = Load('i_ps.pkl')
    initial_position['r'] = sol.FinalPosition(e, None, 'i')

    for league in leagues:
        status, obj, e = sol.Solve("r_post",league=league,initialPosition=initial_position['r'],threads=num_process,timeLimit=time_limit,solverName=solver,option=options,initialSolution=True)
        if status==1:
            preserve(e,'r_post_'+league) 
                
def penSolve(num_process=1,time_limit=None,solver=0):

    sol = ScheduleNPB.Solve()
    leagues = ['p','s']
    initial_position = dict()

    for league in leagues:
        status, obj, e = sol.SolveWithReluxation("r_pre",league=league,threads=num_process,timeLimit=time_limit,solverName=solver)
        if status==1:
            preserve(e,'pen_r_pre_'+league)

        e = Load('pen_r_pre_'+league+'.pkl')
        initial_position[league] = sol.FinalPosition(e, league, 'r_pre')

    position_for_inter = sol.Merge(initial_position['p'],initial_position['s'])
    status, obj, e = sol.SolveWithReluxation('i', initialPosition = position_for_inter, threads=num_process,timeLimit=time_limit,solverName=solver)
    if status==1:
        preserve(e,'pen_i_ps')
    e = Load('pen_i_ps.pkl')
    initial_position['r'] = sol.FinalPosition(e, None, 'i')

    for league in leagues:
        status, obj, e = sol.SolveWithReluxation("r_post",league=league,initialPosition=initial_position['r'],threads=num_process,timeLimit=time_limit,solverName=solver)
        if status==1:
            preserve(e,'pen_r_post_'+league)     
    
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
        print(initial_position)
    position_for_inter = sol.Merge(initial_position['p'],initial_position['s'])
    #status, obj, e = sol.Solve('i', initialPosition = position_for_inter, threads=num_process,timeLimit=time_limit,solverName=solver,option=options,initialSolution=True)
    #if status==1:
    #    preserve(e,'i_ps')
        
    e = Load('i_ps.pkl')
    initial_position['r'] = sol.FinalPosition(e, None, 'i')
    for league in leagues:
        if league == 'p':continue
        status, obj, e = sol.Solve("r_post",league=league,initialPosition=initial_position['r'],threads=num_process,timeLimit=time_limit,solverName=solver,option=options,initialSolution=True)
        if status==1:
            preserve(e,'r_post_'+league)     



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

    parser.add_argument(
        '-pen',
        help="solve with penalty reluxation, default=false",
        type=bool,
        default=False
    )

    return parser


if __name__ == "__main__":
    parser = argparser()
    args   = parser.parse_args()

    num_process = args.th
    limit = args.t
    solver = args.s
    if args.pen:
        penSolve(num_process=num_process,time_limit=limit,solver=solver)
        exit()
    elif args.part:
        partSolve(num_process=num_process,time_limit=limit,solver=solver)
        exit()
    Solve(num_process=num_process,time_limit=limit,solver=solver)
