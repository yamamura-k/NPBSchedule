import ScheduleNPB
from utils.utils import preserve, Load

from argparse import ArgumentParser

"""
一応そこそこいい解は得られたので、ひとまずここまでとしておく。
"""

def Solve(num_process=1,options=[],time_limit=None,solver=0):
    initial_position = dict()
    sol = ScheduleNPB.Solve()
    leagues = ['p', 's']

    for league in leagues:
        status, h, v = sol.RegularGame(league,"r_pre",num_of_process=num_process,option=options,time_limit=time_limit,solver=solver)
        initial_position[league] = sol.FinalPosition(h, v, league, 'r_pre')
        preserve(h,v,'r_pre_'+league)

    position_for_inter = sol.Merge(initial_position['p'],initial_position['s'])
    status, h, v = sol.InterLeague(initial_position = position_for_inter, num_of_process=num_process,option=options,time_limit=time_limit,solver=solver)
    preserve(h,v,'i_ps')

    initial_position['r'] = sol.FinalPosition(h, v, None, 'i')
    for league in leagues:
        status, h, v = sol.RegularGame(league,"r_post",initial_position=initial_position['r'],num_of_process=num_process,option=options,time_limit=time_limit,solver=solver)
        preserve(h,v,'r_post_'+league)    
    
def separatelySolve(num_process=1,options=[],time_limit=None,solver=0):
    initial_position = dict()
    sol = ScheduleNPB.Solve()
    leagues = ['p', 's']
    h,v = Load('i_ps_h.pkl','i_ps_v.pkl')
    initial_position['r'] = sol.FinalPosition(h, v, None, 'i')
    for league in leagues:
        status, h, v = sol.RegularGame(league,"r_post",time_limit=time_limit,initial_position=initial_position['r'],num_of_process=num_process,option=options,solver=solver)
        preserve(h,v,'r_post_'+league)  

def debug(num_process=1,options=[],time_limit=None,solver=0):
    output = ScheduleNPB.Output()
    leagues = ['p', 's']

    Solve(num_process,options,time_limit=time_limit,solver = solver)
    
    for league in leagues:
        filename_h = 'r_pre_'+league+'_h.pkl'
        filename_v = 'r_pre_'+league+'_v.pkl'
        h,v = Load(filename_h,filename_v)
        output.getschedule(1, h, v, 'r_pre', league=league)

    h,v = Load('i_ps_h.pkl','i_ps_v.pkl')
    output.getschedule(1, h, v, 'i')

    for league in leagues:
        filename_h = 'r_post_'+league+'_h.pkl'
        filename_v = 'r_post_'+league+'_v.pkl'
        h,v = Load(filename_h,filename_v)
        output.getschedule(1, h, v, 'r_post', league=league)

    output.MergeRegularschedule()
    
    for game in ['r','r_pre','r_post','i']:
        for i in range(12):
            if len(output.schedules[game][i]) != output.total_game[game]:
                print(game,i)
                output.GameTable(i)
        
    for i in range(12):
        output.CountGames(i)
    
    output.Visualize()
    output.GameTables()
    output.Gameschedule()
    dists = output.TotalDists()
    output.Ranking()
    for dist in dists:
        print(dists[dist])

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
        '-sep','--separete',
        help='solve problem separately\n0:solve total problem\n1:solve problems to get regular schedule after inter league',
        default=0,
        dest='sp',
        type=int
    )
    return parser


if __name__ == "__main__":
    # 綺麗な結果出力用のプログラムも作成する
    parser = argparser()
    args   = parser.parse_args()

    num_process = args.th
    limit       = args.t
    solver      = args.s

    if args.dbg:
        dbg_option = ['maxsol 1']
        debug(num_process=num_process,options=dbg_option,time_limit=limit,solver=solver)
    elif args.sep:
        separatelySolve(num_process=num_process,time_limit=limit,solver=solver)
    else: 
        Solve(num_process=num_process,time_limit=limit,solver=solver)
