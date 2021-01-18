# -*- coding: utf-8 -*-
import ScheduleNPB
from utils.utils import Load

from argparse import ArgumentParser
def main(distance=False, tables=False,pen=''):
    output = ScheduleNPB.Output()
    leagues = ['s','p']
    for league in leagues:
        filename = pen+'r_pre_'+league+'.pkl'
        e = Load(filename)
        output.getSchedule(e, 'r_pre', league=league)

    e = Load(pen+'i_ps.pkl')
    output.getSchedule(e, 'i')

    for league in leagues:
        filename= pen+'r_post_'+league+'.pkl'
        e = Load(filename)
        output.getSchedule(e, 'r_post', league=league)
    output.getWholeSchedule()
    output.MergeRegularSchedule()
    
    if distance:
        dists = output.TotalDists()
        for team in range(12):
            print(dists[team])
    if tables:
        output.GameTables()
    output.checkAnswer()

def argparser():
    parser = ArgumentParser()

    parser.add_argument(
        '--table',
        help='display schedule table or not. default : True',
        default=True,
        dest='table',
        type=bool
    )

    parser.add_argument(
        '--diatance',
        help='display total distance or not. default : True',
        default=True,
        dest='distance',
        type=bool
    )
    parser.add_argument(
        '-pen',
        type=bool,
        default=False
    )
    return parser

if __name__ == "__main__":
    parser = argparser()
    args   = parser.parse_args()
    penal = ''
    if args.pen:
        penal = 'pen_'
    main(distance=args.distance, tables=args.table,pen=penal)
