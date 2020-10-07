# -*- coding: utf-8 -*-
from ScheduleNPB import Output
from utils.utils import Load

def main(num_process=1,options=[],time_limit=None,solver=0):
    output = Output()
    leagues = ['p', 's']
    
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

    output.MergeRegularSchedule()
    
    output.Visualize()

if __name__ == "__main__":
    main()