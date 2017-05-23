import csv
import numpy as np
from datetime import date
from enum import Enum

class State(Enum):
    """
    Enum representing if the motor is calculating a timeblock
    """
    STANDBY = 0
    RUNNING = 1
    COLLIDE = 2

"""CONSTANTS"""
#index 0 = hours , index 1 = minutes
EARLIESTTIME             = [7,59] #The earliest time a block can start
LATESTTIME               = [17,0] #The latest time a block can start

LONGESTDURATION_OCCUPIED = [6,0] #Longest duration a block can have
LONGESTDURATION_FREE     = [8,0] #Longest duration a free block can have
SHORTESTDURATION         = [0,5] #Shortest duration a block can have
"""------------"""

"""------------------------------------------------------------"""
def get_header(kalender):
    """
    Returns the header of the given calendar
    :param kalender: The calendar to get the header from
    :return: The header of the specific calendar
    """
    with open(kalender) as csvfile:
        csvReader = csv.reader(csvfile)
        header = next(csvReader)
    return header

"""------------------------------------------------------------"""
def get_firstDate(kalender):
    """
    Returns the first date of the given calendar
    :param kalender: The calendar to get the date from
    :return: The first date in the calendar
    """
    with open(kalender) as csvfile:
        csvReader = csv.reader(csvfile)
        next(csvReader)
        startDate = next(csvReader)       
    return startDate

"""------------------------------------------------------------"""
def InsertFreeSpace(lst,freeblock_length):
    """
    Calculate free spaces in the given list
    :param lst: The list where free blocks will be generated on
    :param freeblock_length: Maximum length of a free block
    :return: Returns nothing. All modifications takes place inside this method
    """
    filtlst = lst
    
    #Variable used to calculate free blocks
    freeBlock = State.STANDBY
    FREEBLOCK_COUNT = (LONGESTDURATION_FREE[0]*60)+LONGESTDURATION_FREE[1]
    start_time = [0,0,0]
    end_time   = [0,0,0]
    count = 0
    
    for i in range (0,len(lst)): #Loop through each day that contains timeblocks
            count = 0
            if (len(lst[i][1]) < 1):
                for x in range (8,17):
                    for y in range (0,60):
                        if ( [x,y] >= [16,59] and freeBlock == State.RUNNING):
                            FREEBLOCK_COUNT = (LONGESTDURATION_FREE[0]*60)+LONGESTDURATION_FREE[1]
                            end_time = [x,y]
                            filtlst[i][1].append( [start_time[0],start_time[1],0] )
                            filtlst[i][2].append( [end_time[0],end_time[1],0] )
                            filtlst[i][3].append(1)
                            freeBlock = State.STANDBY
                        elif (FREEBLOCK_COUNT  <= 0):
                            FREEBLOCK_COUNT = (LONGESTDURATION_FREE[0]*60)+LONGESTDURATION_FREE[1]
                            end_time = [x,y]
                            filtlst[i][1].append( [start_time[0],start_time[1],0] )
                            filtlst[i][2].append( [end_time[0],end_time[1],0] )
                            filtlst[i][3].append(1)
                            freeBlock = State.STANDBY
                        elif (FREEBLOCK_COUNT > 0 and freeBlock == State.RUNNING):
                            FREEBLOCK_COUNT -= 1
                        elif (FREEBLOCK_COUNT > 0 and freeBlock == State.STANDBY):
                            start_time = [x,y]
                            freeBlock = State.RUNNING
                            FREEBLOCK_COUNT -= 1
            freeBlock = State.STANDBY
            startEnd = []
            for j in range (8,18): #Hour of the day
                for k in range (0,13): #Minute of the current hour, every iteration = 5min
                    for l in range (0,len(lst[i][1])): #Loop through each timeblock
                        if ( ( str(int(lst[i][1][l][0])) + ':' + str(int(lst[i][1][l][1])) ) == (str(j) + ':' + str((k*5)))):
                            for m in range (0,len(lst[i][1])):
                                if ( ( ( str(int(lst[i][1][l][0])) + ':' + str(int(lst[i][1][l][1])) ) == ( str(int(lst[i][2][m][0])) + ':' + str(int(lst[i][2][m][1])) ) ) 
                                    and (m != l) ):
                                    #If both start and end of timeblock m and l
                                    startEnd.append([str(j),str(k*5),'00'])

            collide = 0
            for j in range (8,18): #Hour of the day
                for k in range (0,11): #Minute of the current hour, every iteration = 5min
                    for l in range (0,len(lst[i][1])): #Loop through each timeblock
                        if ( ( str(int(lst[i][2][l-1][0])) + ':' + str(int(lst[i][2][l-1][1])) ) == (str(j) + ':' + str((k*5)))):
                            #If end of timeblock l-1
                            for m in range (0,len(startEnd)):
                                if ( ( str(int(lst[i][2][l-1][0])) + ':' + str(int(lst[i][2][l-1][1])) ) == ( startEnd[m][0] + ':' + startEnd[m][1] ) ):
                                    collide = 1
                            if (collide != 1):
                                if (freeBlock == State.STANDBY and j < 17):
                                    start_time = [j,(k*5),0]
                                    freeBlock = State.RUNNING

                        elif ( ( str(int(lst[i][1][l-1][0])) + ':' + str(int(lst[i][1][l-1][1])) ) == (str(j) + ':' + str((k*5)))):
                           #Else if start of timeblock l-1
                           for m in range (0,len(startEnd)):
                                if ( ( str(int(lst[i][1][l-1][0])) + ':' + str(int(lst[i][1][l-1][1])) ) == ( startEnd[m][0] + ':' + startEnd[m][1] ) ):
                                   collide = 1
                           if (collide != 1):
                               if (freeBlock == State.RUNNING):
                                   end_time = [j,(k*5),0]
                                   if ( (end_time[0] - start_time[0]) < LONGESTDURATION_FREE[0] ):
                                       filtlst[i][1].append( [start_time[0],start_time[1],0] )
                                       filtlst[i][2].append( [j,(k*5),0] )
                                       filtlst[i][3].append(1)
                                       freeBlock = State.STANDBY                   
                        
                        else:
                            if (freeBlock == State.RUNNING and j >= 17):
                                end_time = [17,0,0]
                                if ( (end_time[0] - start_time[0]) < LONGESTDURATION_FREE[0] ):
                                    filtlst[i][1].append( [start_time[0],start_time[1],0] )
                                    filtlst[i][2].append( ['17','00','00'] )
                                    filtlst[i][3].append(1)
                                    freeBlock = State.STANDBY
                            
                            elif (freeBlock == State.STANDBY and j == 8 and k == 0):
                                count += 1
                                if (count >= len(lst[i][1]) ):
                                    start_time = [8,0,0]
                                    freeBlock = State.RUNNING
                    collide = 0
    return

"""------------------------------------------------------------"""
def find_n(lst, var, n):
    """
    Find at which index the given value occur
    
    :param lst: The given list to look at
    :param var: The value to search for
    :param n: the current index when iterating the list
    :return: Index of the value
    """
    start = lst.find(var)
    while start >= 0 and n > 1:
        start = lst.find(var, start+1)
        n -= 1
    return start

def Get_n_blocks(kalender):
    """
    Returns the number of blocks inside the given calendar
    
    :param kalender: The calendar to get the number of blocks from
    :return: Number of blocks inside the calendar
    """
    antal = 0
    with open(kalender) as csvfile:
            csvReader = csv.reader(csvfile)
            for row in csvReader:
                antal += 1
    return antal-1


def Fetch_Data(kalender,start,stop):
    """
    Returns a list in the format: [[date],[starttime],[endtime],[classes],[dayofweek]]
    
    :param kalender: The calendar to fetch the data from
    :param start: The row where the method will start reading from
    :param stop: The row where the method will stop reading
    :return: Returns a list containing the fetched blocks
    """
    with open(kalender) as csvfile:
            csvReader = csv.reader(csvfile)
            header = next(csvReader)
            
            #Indexes in the CSV-file
            #Index 0 = start , Index 1 = end
            dateIndex = np.array([header.index("startdatum") , header.index("slutdatum")])
            timeIndex = np.array([header.index("starttid") , header.index("sluttid")])
            DateList = []
            
            prev_block = [ [0,0,0],[0,0],[0,0] ]
            
            #FLAGS INDICATING ERRORS AND STATES
            DATE_EXIST = 0 #Flag representing if a date already exist in the list
            TOO_SHORT  = 0 #Flag representing if a timeblock is too short to be appended
            TOO_LONG   = 0 #Flag representing if a timeblock is too long to be appended
            TOO_EARLY  = 0 #Block starts to early
            TOO_LATE   = 0 #Block starts to late
            DONT_SAVE  = 0
            
            #Loop through the rows of the CSV-file
            for row in csvReader:
                #Stop fetching data if the current row is bigger than TIMEBLOCKS
                if (csvReader.line_num-1 > stop):
                    break
                
                if (csvReader.line_num-1 >= start-1):
                
                    """------------SIMPLIFY THE FORMAT OF THE FETCHED DATA------"""
                    #Save year,month and day in separate variables
                    block_date = row[dateIndex[0]]
                    year = int(block_date[:block_date.find('-')])
                    month = int(block_date[block_date.find('-')+1:find_n(block_date,"-",2)])
                    day = int(block_date[find_n(block_date,"-",2)+1:])
                    
                    #Save start_time and end_time in variables
                    start_time = row[timeIndex[0]]
                    start_hour = int(start_time[:start_time.find(":")])
                    start_minute = int(start_time[start_time.find(':')+1:find_n(start_time,":",2)])
                    end_time = row[timeIndex[1]]
                    end_hour = int(end_time[:end_time.find(":")])
                    end_minute = int(end_time[end_time.find(':')+1:find_n(end_time,":",2)])
                    
                    #Decide classification,calculate weekday and length of block
                    classification = 0
                    weekday = date(year,month,day).weekday()+1
                    length = [end_hour - start_hour,end_minute - start_minute]
                    """------------SIMPLIFY THE FORMAT OF THE FETCHED DATA------"""
                            
                    
                    """------------IF-CASES FILTERING OUT IRRELEVANT BLOCKS------"""
                    #If the timeblock is occurring between a time where another block is -> DO NOT SAVE IT
                    if ( [year,month,day] == prev_block[0] ):
                        if ( [start_hour,start_minute] >= prev_block[1] and [start_hour,start_minute] < prev_block[2] ):
                            if ( [end_hour,end_minute] >= prev_block[2] ):
                                DateList[-1][2][-1] = [end_hour,end_minute]
                                DONT_SAVE = 1
                    
                    
                    #If the timeblock is shorter than SHORTESTDURATION -> DO NOT SAVE IT
                    if ( (length[0] <= SHORTESTDURATION[0]) and (length[1] <= SHORTESTDURATION[1]) ):
                        TOO_SHORT = 1
                    
                    #If the timeblock is longer than LONGESTDURATION -> DO NOT SAVE IT
                    if ( (length[0] > LONGESTDURATION_OCCUPIED[0]) and (length[1] >= LONGESTDURATION_OCCUPIED[1]) ):
                        TOO_LONG = 1
                        
                    #If the timeblock starts earlier than EARLIESTTIME -> DO NOT SAVE IT
                    if ( (start_hour <= EARLIESTTIME[0]) ):
                        TOO_EARLY = 1
                        
                    #If the timeblock starts later than LATESTTIME -> DO NOT SAVE IT
                    if ( (start_hour >= LATESTTIME[0]) and (start_minute >= LATESTTIME[1]) ):
                        TOO_LATE = 1
                        
                    for i in range (0,len(DateList)):
                        if (DateList[i][0][0] == year and DateList[i][0][1] == month 
                            and DateList[i][0][2] == day):
                            DATE_EXIST = 1
                    """------------IF-CASES FILTERING OUT IRRELEVANT BLOCKS------"""
                        
                    
                    #If the timeblock is too short and the date doesn't exist -> Create the date
                    if ( (TOO_SHORT == 1 or TOO_LONG == 1 or TOO_EARLY == 1 or TOO_LATE == 1) and DATE_EXIST == 0 ):
                        if (DONT_SAVE == 0):
                            DateList.append([ [year,month,day] , [] , [] , [] , weekday])
                    
                    if (TOO_SHORT == 0 and TOO_LONG == 0 and TOO_EARLY == 0 and TOO_LATE == 0): #If the timeblocks duration is long enough
                        #Check if the date is in the list; if it is -> save the block in that index
                        for i in range (0,len(DateList)):
                            if (DateList[i][0][0] == year and DateList[i][0][1] == month 
                                and DateList[i][0][2] == day):
                                if (DONT_SAVE == 0):
                                    DateList[i][1].append([start_hour,start_minute])
                                    DateList[i][2].append([end_hour,end_minute])
                                    DateList[i][3].append(classification)
                                    DATE_EXIST = 1 #The date existed so the boolean turns to 1
                          
                        if (DATE_EXIST == 0): #If the date didn't exist
                           #Save all information to an array and then append it to the list
                           timeblock = [ [year,month,day],[[start_hour,start_minute]],[[end_hour,end_minute]],[classification],weekday]
                           if (DONT_SAVE == 0):
                               DateList.append(timeblock)
                               DATE_EXIST = 1
                    
                    #RESET THE FLAGS FOR THE NEXT ITERATION
                    if (TOO_SHORT == 0 and TOO_LONG == 0 and TOO_EARLY == 0 and TOO_LATE == 0):
                        prev_block = [ [year,month,day], [start_hour,start_minute], [end_hour,end_minute] ]
                    DATE_EXIST = 0
                    TOO_SHORT  = 0
                    TOO_LONG   = 0
                    TOO_EARLY  = 0
                    TOO_LATE   = 0
                    DONT_SAVE  = 0
    
    
    #After everything is done, before returning results
    newList = []
    for i in range(0,len(DateList)):
        if ( len(DateList[i][1]) >= 1 ):
            newList.append(DateList[i])
    return newList

"""------------------------------------------------------------"""
def GetBlocksByDate(lst,year,month,day): #åååå-mm-dd
    """
    Returns all blocks at the specific date
    
    :param lst: The list to look at
    :return: Returns a list containing the blocks on the specific date
    """
    blocks = []
    for i in range(0,len(lst)):
        if (int(lst[i][0][0]) == year and int(lst[i][0][1]) == month and int(lst[i][0][2]) == day):
            blocks.append(lst[i])
    return blocks

"""------------------------------------------------------------"""
def GetNumberOfDays(lst,weekday): #weekday = int
    """
    Get the number of days filtered by weekday
    
    :param lst: The list to look at
    :param weekday: Weekday to filter blocks by
    :return: Returns the number of days by weekday
    """
    n_of_days = 0
    for i in range(0,len(lst)):
        if (lst[i][4] == weekday):
            n_of_days += 1
    return n_of_days

"""------------------------------------------------------------"""
def GetBlocksByWeekday(lst,weekday): #weekday = int
    """
    Get all blocks occurring on a specific weekday
    
    :param lst: The list to look at
    :param weekday: Weekday to filter blocks by
    :return: Returns a list of all the blocks occurring on the specific weekday
    """
    blocks = []
    n_of_days = 0
    for i in range(0,len(lst)):
        if (lst[i][4] == weekday):
            n_of_days += 1
            blocks.append(lst[i])
    return blocks

"""------------------------------------------------------------"""
def GetBlocksByMonthDay(lst,day_in_month): #day_in_month = int
    """
    Returns all blocks occuring at the specific monthday
    
    :param lst: The list to look at
    :param day_in_month: The day in month to filter blocks by
    :return: Returns a list containing all blocks on the specific day in month
    """
    blocks = []
    for i in range(0,len(lst)):
        if (int(lst[i][0][0][2]) == day_in_month):
            blocks.append(lst[i])
    return blocks

"""------------------------------------------------------------"""
def GetStartTimes(lst):
    """
    Returns the start times on every block in the list
    Format: [hh,mm]
    
    :param lst: The list to use
    :return: Returns a list of all the start times in the list
    """
    startTimes = []
    for i in range(0,len(lst)):
        for j in range (0,len(lst[i][1])):
            hours = int(lst[i][1][j][0])
            minutes = int(lst[i][1][j][1])
            if (lst[i][3][j] == 1): #If free block
                startTimes.append( [hours,minutes,'O'] )
            elif (lst[i][3][j] == 0): #If occupied block
                startTimes.append( [hours,minutes,'X'] )
    return startTimes

"""------------------------------------------------------------"""
def GetStartTimes_decimal(lst):
    """
    Returns the start times on every block in the list
    Format: hh,mm
    
    :param lst: The list to use
    :return: Returns a list containing all the start times in the list
    """
    startTimes = []
    for i in range(0,len(lst)):
        for j in range (0,len(lst[i][1])):
            hours = float(lst[i][1][j][0])
            minutes = float(int(lst[i][1][j][1])/60)
            startTimes.append( hours+minutes )
    return startTimes

"""------------------------------------------------------------"""
def GetEndTimes(lst):
    """
    Returns the end_times of every block in the specified list
    Format: [hh,mm]
    
    :param lst: The list to use
    :return: Returns a list of every end_time in the specified list
    """
    endTimes = []
    for i in range(0,len(lst)):
        for j in range (0,len(lst[i][1])):
            hours = int(lst[i][2][j][0])
            minutes = int(lst[i][2][j][1])
            if (lst[i][3][j] == 1): #If free block
               endTimes.append( [hours,minutes,'O'] )
            elif (lst[i][3][j] == 0): #If occupied block
                endTimes.append( [hours,minutes,'X'] )
    return endTimes

"""------------------------------------------------------------"""
def GetEndTimes_decimal(lst):
    """
    Returns the end_times of every block in the specified list
    Format: hh,mm
    
    :param lst: The list to use
    :return: Returns a list of every end_time in the specified list
    """
    endTimes = []
    for i in range(0,len(lst)):
        for j in range (0,len(lst[i][1])):
            hours = float(lst[i][2][j][0])
            minutes = float(int(lst[i][2][j][1])/60)
            endTimes.append( hours+minutes )
    return endTimes

"""------------------------------------------------------------"""
def GetLengths(lst):
    """
    Returns the length of every block in the specified list
    Format: hh,mm
    
    :param lst: The list to use
    :return: Returns a list of every length in the specified list
    """
    lengths = []
    for i in range(0,len(lst)):
        for j in range (0,len(lst[i][1])):
            start = float(lst[i][1][j][0]) + float(int(lst[i][1][j][1])/60)
            end = float(lst[i][2][j][0]) + float(int(lst[i][2][j][1])/60)
            length = end-start
            lengths.append( length )
    return lengths

"""------------------------------------------------------------"""
def GetClasses(lst):
    """
    Returns the class of every block in the specified list
    
    :param lst: The list to use
    :return: Returns a list of every class in the specified list
    """
    classes = []
    for i in range(0,len(lst)):
        for j in range (0,len(lst[i][1])):
             classes.append( lst[i][3][j] )
    return classes

"""------------------------------------------------------------"""
def GetStartTimes_By_Classes(lst, classification):
    """
    Returns the start times of every block of a specific class in the list
    Format: hh,mm
    
    :param lst: The list to use
    :return: Returns a list of every start time of a specific class in the specified list
    """
    blocks = []
    for i in range(0,len(lst)):
        for j in range (0,len(lst[i][1])):
            if (lst[i][3][j] == classification):
                hours = float(lst[i][1][j][0])
                minutes = float(int(lst[i][1][j][1])/60)
                blocks.append( hours+minutes )
    return blocks

"""------------------------------------------------------------"""
def GetLengths_By_Classes(lst, classification):
    """
    Returns the lengths of every block of a specific class in the list
    Format: hh,mm
    
    :param lst: The list to use
    :return: Returns a list of every length of a specific class in the specified list
    """
    lengths = []
    for i in range(0,len(lst)):
        for j in range (0,len(lst[i][1])):
            if (lst[i][3][j] == classification):
                start = float(lst[i][1][j][0]) + float(int(lst[i][1][j][1])/60)
                end = float(lst[i][2][j][0]) + float(int(lst[i][2][j][1])/60)
                length = end-start
                lengths.append( length )
    return lengths

"""------------------------------------------------------------"""
def Prepare_Plane(start_times,lengths):
    """
    Preprare the data by pairing start_times with lengths
    
    :param start_times: List containing the start times
    :param lengths: List containing the lengths
    :return: Returns a list of points representing the start_times and lengths in the xy-plane
    """
    points = []
    for i in range(0,len(lengths)):
                #start = float(lst[i][1][j][0]) + float(int(lst[i][1][j][1])/60)
                #end = float(lst[i][2][j][0]) + float(int(lst[i][2][j][1])/60)
                #length = end-start
        points.append( [start_times[i],lengths[i]] )
    return points

"""------------------------------------------------------------"""
def GetNumber_Of_Blocks(lst,classification):
    """
    Returns the number of blocks of a specific class in the list
    
    :param lst: The list to use
    :param classification: The class to filter blocks by
    :return: Returns the number of blocks by the specified class
    """
    antal = 0
    for i in range(0,len(lst)):
        for j in range (0,len(lst[i][1])):
            if (lst[i][3][j] == classification):
                antal += 1
    return antal

"""------------------------------------------------------------"""
def GetTimes_By_Blocks(lst,classification):
    """
    Returns the start and end of every block of a specific class
    Format: [[[hh,mm],[hh,mm]],[[hh,mm],[hh,mm]]...]
    
    :param lst: The list to use
    :param classification: The class to filter blocks by
    :return: Returns a list containing the start- and end time of every block of the specific class
    """
    hours = 0
    for i in range(0,len(lst)):
        for j in range (0,len(lst[i][1])):
            if (lst[i][3][j] == classification):
                start = float(lst[i][1][j][0]) + float(int(lst[i][1][j][1])/60)
                end = float(lst[i][2][j][0]) + float(int(lst[i][2][j][1])/60)
                length = end-start
                hours += length
    return hours

"""------------------------------------------------------------"""
def Get_Blocks_Between(lst,startDate,endDate):
    """
    Get every block between the given dates
    
    :param lst: The list to use
    :return: Returns a list containing every block between the given dates
    """
    result = []
    for i in range (0,len(lst)):
        if ( lst[i][0] >= startDate and lst[i][0] <= endDate ):
            result.append(lst[i])
    return result

"""------------------------------------------------------------"""
def Get_Index_By_Date(kalender,date):
    """
    Returns the index of the given date in the specified calendar-file
    
    :param kalender: The calendar to look at
    :param date: The date to search for
    :return: Returns the index of the first occurence of the specified date
    """
    with open(kalender) as csvfile:
        csvReader = csv.reader(csvfile)
        header = next(csvReader)
        dateIndex = np.array([header.index("startdatum") , header.index("slutdatum")])
        next(csvReader)
        for row in csvReader:
            block_date = row[dateIndex[0]]
            year = int(block_date[:block_date.find('-')])
            month = int(block_date[block_date.find('-')+1:find_n(block_date,"-",2)])
            day = int(block_date[find_n(block_date,"-",2)+1:])
            if (year == date[0] and month >= date[1] and day >= date[2]):
                return csvReader.line_num 
    return -1

"""------------------------------------------------------------"""
def Get_Block_By_Index(kalender,index):
    """
    Returns every block at the specified index in the calendar-file
    
    :param kalender: The calendar-file to look at
    :param index: The index of the block
    """
    with open(kalender) as csvfile:
        csvReader = csv.reader(csvfile)
        header = next(csvReader)
        dateIndex = np.array([header.index("startdatum") , header.index("slutdatum")])
        timeIndex = np.array([header.index("starttid") , header.index("sluttid")])
        
        for row in csvReader:
            
            """------------SIMPLIFY THE FORMAT OF THE FETCHED DATA------"""
            #Save year,month and day in separate variables
            block_date = row[dateIndex[0]]
            year = int(block_date[:block_date.find('-')])
            month = int(block_date[block_date.find('-')+1:find_n(block_date,"-",2)])
            day = int(block_date[find_n(block_date,"-",2)+1:])
            
            #Save start_time and end_time in variables
            start_time = row[timeIndex[0]]
            start_hour = int(start_time[:start_time.find(":")])
            start_minute = int(start_time[start_time.find(':')+1:find_n(start_time,":",2)])
            end_time = row[timeIndex[1]]
            end_hour = int(end_time[:end_time.find(":")])
            end_minute = int(end_time[end_time.find(':')+1:find_n(end_time,":",2)])
                    
            #Decide classification,calculate weekday and length of block
            classification = 0
            weekday = date(year,month,day).weekday()+1
            length = [end_hour - start_hour,end_minute - start_minute]
            """------------SIMPLIFY THE FORMAT OF THE FETCHED DATA------"""
            
            if (csvReader.line_num-1 == index):
                return [ [year,month,day],[[start_hour,start_minute]],[[end_hour,end_minute]],[classification],weekday]
    return -1
"""------------------------------------------------------------"""
def decimal_range(start, stop, step):
    """
    A for-loop incrementing decimal values
    
    :param start: Start of the for-loop
    :param stop: Stop of the for-loop
    :param step: How much to increment for every iteration
    :return: Returns nothing
    """
    while start < stop:
            yield start
            start += step