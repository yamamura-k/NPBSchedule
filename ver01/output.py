from ScheduleNPB import Output
from utils.utils import Load

from argparse import ArgumentParser

def argparser():
    parser = ArgumentParser()

    parser.add_argument(
        '-d','--distance',
        help='bool: display total distance of all team, or not',
        default=False,
        dest='d',
        type=bool
    )

    parser.add_argument(
        '-s','--schedule',
        help='bool: display whole schedule or not',
        default=False,
        dest='s',
        type=bool
    )

    parser.add_argument(
        '-t','--team',
        help='int: select Team\'s number(>=1)whose schedule you want to check.',
        default=-1,
        dest='t',
        type=int
    )
    return parser

def main(args):
    output = Output()
    leagues = ['p','s']
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

    if args.d:
        output.TotalDists()
        output.Ranking()

    if args.s:
        output.GameTables()
        output.Gameschedule()
    
    if args.t>0:
        output.GameTable(args.t)

if __name__ == "__main__":
    parser = argparser()
    args = parser.parse_args()
    main(args)
