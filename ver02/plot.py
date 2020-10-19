# -*- coding: utf-8 -*-
import ScheduleNPB
from utils.utils import Load

from argparse import ArgumentParser

def main(m=False, p=False):
    output = ScheduleNPB.Output()
    leagues = ['s','p']
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
    output.getWholeSchedule()
    output.MergeRegularSchedule()
    #output.createMovie(0, 'i')
    if m:
        output.createMovies()
    if p:
        output.Visualize()

def argparser():
    parser = ArgumentParser()
    parser.add_argument(
        '-m', '--movie',
        help="make .gif or not.(default=False)",
        default=False,
        type=bool
    )
    parser.add_argument(
        '-p', '--picture',
        help="make .png or not.(default=False)",
        default=False,
        type=bool
    )
    return parser

if __name__ == "__main__":
    parser = argparser()
    args = parser.parse_args()
    main(m=args.movie, p=args.picture)
