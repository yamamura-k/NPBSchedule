from ScheduleNPB import Output
from utils.utils import Load

from matplotlib import pyplot as plt

def LoadData():
    output = Output()
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
    
    return output.schedules['all']

def CreateTable(schedules):
    output = Output()
    data = {output.Teams_name[i]:[output.Teams_name[s[1]]for s in schedules[i]]for i in range(12)}
    """
    for s in output.Teams_name.values():
        print(len(data[s]))
    """
    fig, ax = plt.subplots(figsize=(15,5))
    ax.axis('off')
    ax.axis('tight')
    tb = ax.table(cellText=[data[i]for i in data],
                  rowLabels=[i for i in data],
                  colLabels=list(map(str,list(range(1,49)))),
                  loc='center'
                  )
    for i in range(10,16):
       tb[0, i].set_facecolor('#FF0000') 
    for team in schedules:
        for index,v in enumerate(schedules[team]):
            if v[-1] == 'visitor':
                tb[team+1, index].set_facecolor('#FFFF00')
    plt.savefig("Table_of_Schedule.png")
    

def main():
    schedule = LoadData()
    CreateTable(schedule)

if __name__ == "__main__":
    main()