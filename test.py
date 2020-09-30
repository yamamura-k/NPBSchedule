import SchesuleNPB

import os
import pickle
import datetime
from argparse import ArgumentParser

"""
5週間解く(セ・パ)->交流戦解く->残りの37週を解く
目的関数にw=0の項を追加すれば良いだけ
"""

def preserve(h, v, filename):
    with open(filename+"_h.pkl", 'wb') as f:
        pickle.dump(h,f)
    with open(filename+"_v.pkl", 'wb') as f:
        pickle.dump(v,f)

def Load(filename_h,filename_v):
    with open(filename_h,'rb') as f:
        h = pickle.load(f)
    with open(filename_v,'rb') as f:
        v = pickle.load(f)
    return h,v

def Solve(num_process=1,options=[],time_limit=None):
    initial_position = dict()
    sol = SchesuleNPB.Solve()
    leagues = ['p', 's']

    for league in leagues:
        status, h, v = sol.RegularGame(league,"r_pre",num_of_process=num_process,option=options,time_limit=time_limit)
        initial_position[league] = sol.FinalPosition(h, v, league, 'r_pre')
        preserve(h,v,'r_pre_'+league)

    position_for_inter = sol.Merge(initial_position['p'],initial_position['s'])
    status, h, v = sol.InterLeague(initial_position = position_for_inter, num_of_process=num_process,option=options,time_limit=time_limit)
    preserve(h,v,'i_ps')

    initial_position['r'] = sol.FinalPosition(h, v, None, 'i')
    for league in leagues:
        status, h, v = sol.RegularGame(league,"r_post",initial_position=initial_position['r'],num_of_process=num_process,option=options,time_limit=time_limit)
        preserve(h,v,'r_post_'+league)    
    
def main(num_process=1,options=[],time_limit=None):
    initial_position = dict()
    sol = SchesuleNPB.Solve()
    leagues = ['p', 's']
    h,v = Load('i_ps_h.pkl','i_ps_v.pkl')
    initial_position['r'] = sol.FinalPosition(h, v, None, 'i')
    for league in leagues:
        status, h, v = sol.RegularGame(league,"r_post",initial_position=initial_position['r'],num_of_process=num_process,option=options)
        preserve(h,v,'r_post_'+league)  

def check():
    out = SchesuleNPB.Output()
    filename_h = 'r_post_p_h.pkl'
    filename_v = 'r_post_p_v.pkl'
    h,v = Load(filename_h,filename_v)
    I = out.Teams['p']
    total = 0
    for d in [0,1]:
        for w in range(1,5):
            for i in I:
                home = sum([h[d][i][k][w] for k in I])
                for j in I:
                    if home == 1 and v[(d-1)%2][i][j][w-1] == 1:
                        total += out.D[i][j]
    for d in [0,1]:
        for w in range(1,5):
            for i in I:
                for j in I:
                    for team in I:
                        if v[d][team][i][w] == 1 and sum([v[(d-1)%2][k][j][w-1]+h[(d-1)%2][j][k][w-1]for k in I]) == 1:
                            total += out.D[i][j]
    print(total)


def _main(num_process=1,options=[],time_limit=None):
    output = SchesuleNPB.Output()
    leagues = ['p', 's']

    Solve(num_process,options,time_limit=time_limit)
    
    for league in leagues:
        filename_h = 'r_pre_'+league+'_h.pkl'
        filename_v = 'r_pre_'+league+'_v.pkl'
        h,v = Load(filename_h,filename_v)
        output.getSchesule(1, h, v, 'r_pre', league=league)

    h,v = Load('i_ps_h.pkl','i_ps_v.pkl')
    output.getSchesule(1, h, v, 'i')

    for league in leagues:
        filename_h = 'r_post_'+league+'_h.pkl'
        filename_v = 'r_post_'+league+'_v.pkl'
        h,v = Load(filename_h,filename_v)
        output.getSchesule(1, h, v, 'r_post', league=league)

    output.MergeRegularSchesule()
    output.Visualize()
    output.GameTables()
    output.GameSchesule()
    dists = output.TotalDists()
    output.Ranking()
    for dist in dists:
        print(dists[dist])


def argparser():
    parser = ArgumentParser()

    parser.add_argument(
        '-dbg','--debag',
        help='debag mode : if you want use debag mode, -dbg 1',
        default=False,
        dest='dbg',
        type=bool
    )

    parser.add_argument(
        '-t','--time',
        help='time limit of cbc solver. the format is [time limit]seconds.',
        default=None,
        dest='t',
        type=int
    )

    parser.add_argument(
        '--process',
        help='number of process',
        default=1,
        dest='process',
        type=int
    )

    return parser

if __name__ == "__main__":
    # 綺麗な結果出力用のプログラムも作成する
    parser = argparser()
    args   = parser.parse_args()
    num_process = args.process
    limit = args.t
    if args.dbg:
        dbg_option = ['maxsol 10']
        main(num_process=num_process,options=dbg_option)
    else: 
        main(num_process=num_process,time_limit=limit)
