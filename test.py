import SchesuleNPB

import os
import pickle
import datetime
from argparse import ArgumentParser

"""
5週間解く(セ・パ)->交流戦解く->残りの37週を解く
目的関数にw=0の項を追加すれば良いだけ
"""

def preserve(h, v, game_type, league, filename):
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

def Solve(num_process=1,options=[]):
    sol = SchesuleNPB.Solve()
    leagues = ['p', 's']
    options_cp = list(options)    
    for league in leagues:
        status, h, v = sol.RegularGame(league,num_of_process=num_process,option=options)
        preserve(h,v,'r',league,'r_'+league)   
    status, h, v = sol.InterLeague(num_of_process=num_process,option=options)
    preserve(h,v,'r','p','i_ps')

def main(num_process=1,options=[]):
    output = SchesuleNPB.Output()
    leagues = ['p', 's']

    #Solve(num_process,options)

    for league in leagues:
        filename_h = 'r_'+league+'_h.pkl'
        filename_v = 'r_'+league+'_v.pkl'
        h,v = Load(filename_h,filename_v)
        output.getSchesule(1, h, v, 'r', league=league)

    h,v = Load('i_ps_h.pkl','i_ps_v.pkl')
    output.getSchesule(1, h, v, 'i')
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

    if args.dbg:
        dbg_option = ['maxsol 1']
        main(num_process=num_process,options=dbg_option)
    else: 
        main(num_process=num_process)