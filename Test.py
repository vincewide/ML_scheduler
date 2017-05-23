import csv
import numpy as np

import Preprocessor as p
import Supervised as sv
import Unsupervised as uv
import matplotlib.pyplot as plt

from timeit import Timer

performance_time = 0
performance_start = 0

""""------------------------------------------------------------------------"""
def get_time(call,function,klass):
    """
    Returns the time it takes to complete the given method
    
    :param call: String specifing the call to the method (incl. parameters)
    :param function: The name of the method
    :param klass: The class which contains the method
    :return: Returns the time it took to execute the method
    """
    t = Timer(call,('from ' + str(klass) + ' import ' + str(function)) )
    return t.timeit(number=1)
""""------------------------------------------------------------------------"""

def DBSCAN(kalender,predicted_length,weekday):
    """
    Method used to test the DBSCAN prototype
    
    :param kalender: The calendar to use
    :param predicted_length: Duration of the predicted block
    :param weekday: The specific weekday to perform tests on
    """
    #If the suggested times are declined by the user -> increase minPts (k) with values being [3,5,10]
    dbscan = 0
    predicted_times = 0
    file = "scheman/" + str(kalender) + ".csv"
    n_timeblocks = p.Get_n_blocks(file)
    
    #6 månader test data
    last_testBlock = p.Get_Block_By_Index(file,n_timeblocks-30)
    if (last_testBlock[0][1] > 6):
        first_testBlock = p.Get_Index_By_Date(file,[last_testBlock[0][0],last_testBlock[0][1]-6,last_testBlock[0][2]])
        test_data = [first_testBlock, last_testBlock]
    else:
        first_testBlock = p.Get_Index_By_Date(file,[last_testBlock[0][0]-1,last_testBlock[0][1]+6,last_testBlock[0][2]])
        test_data = [first_testBlock, last_testBlock]
    
    """
    #Specific training and test interval
    test_startBlock = p.Get_Block_By_Index(file,np.floor(n_timeblocks*(2/3)))
    training_start = p.Get_Index_By_Date(file,[test_startBlock[0][0]-1,test_startBlock[0][1],test_startBlock[0][2]])
    one_year_training = [training_start, np.floor(n_timeblocks*(2/3))-1]
    """
    
    training_set = p.Fetch_Data(file,0, np.floor(n_timeblocks*(2/3))-1) #
    test_set = p.Fetch_Data(file, np.floor(n_timeblocks*(2/3)), n_timeblocks ) #
    p.InsertFreeSpace(training_set,[1,0]) #
    p.InsertFreeSpace(test_set,[1,0]) #
                     
    #Filter by a specific weekday
    filtered_training = p.GetBlocksByWeekday(training_set,weekday)
    filtered_test = p.GetBlocksByWeekday(test_set,weekday)
    n_of_days = p.GetNumberOfDays(filtered_test,weekday)+p.GetNumberOfDays(filtered_training,weekday)

    
    #Only freespace blocks
    training_startTimes = p.GetStartTimes_By_Classes(filtered_training,1)
    training_lengths = p.GetLengths_By_Classes(filtered_training,1)
    training_classes = []
    for i in range (0,len(training_startTimes)):
        training_classes.append(1)
    
    
    test_free_startTimes = p.GetStartTimes_By_Classes(filtered_test,1)
    test_free_lengths = p.GetLengths_By_Classes(filtered_test,1)
    test_free_classes = []
    for i in range (0,len(test_free_startTimes)):
        test_free_classes.append(1)
    test_occupied_startTimes = p.GetStartTimes_By_Classes(filtered_test,0)
    test_occupied_lengths = p.GetLengths_By_Classes(filtered_test,0)
    test_occupied_classes = []
    for i in range (0,len(test_occupied_startTimes)):
        test_occupied_classes.append(0)
    
    
        
    #Prepare the format of the points so they can be presented in the xy-plane
    training_points = p.Prepare_Plane(training_startTimes,training_lengths)
    test_free_points = p.Prepare_Plane(test_free_startTimes,test_free_lengths)
    test_occupied_points = p.Prepare_Plane(test_occupied_startTimes,test_occupied_lengths)
    #print(training_set)
    
    
    #Create the DBSCAN object
    dbscan = uv.DB_SCAN("Kalender " + str(1) + " , Dag: " + str(1) + " , K=" + str(3))
    DB_radius = dbscan.KNNdist_plot(training_points,10)
    dbscan.learn(training_points[:dbscan.n_trainingData],DB_radius,10,predicted_length)
    predicted_times = ( dbscan.predict() )    
    
    total_hours = 0
    free_hours = 0
    occupied_hours = 0
    successful_predictions = 0
    failed_predictions     = 0
    tid = 0
    pred_counter = 0
    
    
    for i in range (0,len(test_free_points)):
        total_hours += test_free_points[i][1]
        free_hours  += test_free_points[i][1]
    for i in range (0,len(test_occupied_points)):
        total_hours += test_occupied_points[i][1]
        occupied_hours += test_occupied_points[i][1]
    
    for i in range (0,len(test_free_points)):
        for j in range(0,len(predicted_times)):
            tid = 0
            #Store the start and end times in temporary variables
            pred_start = predicted_times[j][0]
            pred_end = pred_start+predicted_length
            start_time = test_free_points[i][0]
            end_time = start_time+test_free_points[i][1]
            
            if ((pred_start >= start_time) and (pred_start < end_time)):
            #true
                if (pred_end <= end_time):
                    #true
                    tid = pred_end - pred_start
                else:
                    #false
                    tid = end_time - pred_start
                    
            #false
            elif ((pred_start < start_time) and (pred_end >= start_time) and (pred_end <= end_time)):
                #true
                tid = pred_end - start_time
            if (tid != 0):
                successful_predictions += tid
            pred_counter += predicted_length
    
    
    print("--------------------------------------------")
    print (str(predicted_times) + '\n')
    print("Kalender: " + str(kalender) + " , Veckodag: " + str(weekday))
    print("Totala timmar [h]: " + str(total_hours))
    print ("Lediga timmar [h]: " + str(free_hours))
    print ("Upptagna timmar [h]: " + str(occupied_hours) + '\n')
    print("Lyckad prediktion [h]: " + str(successful_predictions))
    print("Totala prediktioner [h]: " + str(pred_counter) + '\n')
    
    return

""""------------------------------------------------------------------------"""
def wKNN(kalender,predicted_length,weekday):
    """
    Method used to test the wKNN prototype
    
    :param kalender: The calendar to use
    :param predicted_length: Duration of the predicted block
    :param weekday: The specific weekday to perform tests on
    """
    wknn = 0
    predicted_times = []
    file = "scheman/" + str(kalender) + ".csv"
    
    n_timeblocks = p.Get_n_blocks(file)
    thumb_rule = [np.floor(n_timeblocks*(2/3)),n_timeblocks]
    
    """
    #6 månad test data
    last_testBlock = p.Get_Block_By_Index(file,n_timeblocks-10)
    if (last_testBlock[0][1] > 6):
        first_testBlock = p.Get_Index_By_Date(file,[last_testBlock[0][0],last_testBlock[0][1]-6,last_testBlock[0][2]])
        test_data = [first_testBlock, last_testBlock]
    else:
        first_testBlock = p.Get_Index_By_Date(file,[last_testBlock[0][0]-1,last_testBlock[0][1]+6,last_testBlock[0][2]])
        test_data = [first_testBlock, last_testBlock]
    """
    
    """
    #Specific training and test interval
    test_startBlock = p.Get_Block_By_Index(file,np.floor(n_timeblocks*(2/3)))
    training_start = p.Get_Index_By_Date(file,[test_startBlock[0][0]-1,test_startBlock[0][1],test_startBlock[0][2]])
    one_year_training = [training_start, np.floor(n_timeblocks*(2/3))-1]
    """

    training_set = p.Fetch_Data(file,0, thumb_rule[0] ) #
    test_set = p.Fetch_Data(file, thumb_rule[0] , thumb_rule[1] ) #
    p.InsertFreeSpace(training_set,[1,0]) #
    p.InsertFreeSpace(test_set,[1,0]) #
                     
    #Filter by a specific weekday
    filtered_training = p.GetBlocksByWeekday(training_set,weekday)
    filtered_test = p.GetBlocksByWeekday(test_set,weekday)
    n_of_days = p.GetNumberOfDays(filtered_test,weekday)+p.GetNumberOfDays(filtered_training,weekday)
    
    #Both freespace and occupied blocks
    training_startTimes = p.GetStartTimes_decimal(filtered_training)
    training_lengths = p.GetLengths(filtered_training)
    training_classes = []
    for i in range (0,len(filtered_training)):
        for j in range (0,len(filtered_training[i][1])):
            training_classes.append( filtered_training[i][3][j] )
    
    
    #Save the free and occupied test times
    test_free_startTimes = p.GetStartTimes_By_Classes(filtered_test,1)
    test_free_lengths = p.GetLengths_By_Classes(filtered_test,1)
    test_free_classes = []
    for i in range (0,len(test_free_startTimes)):
        test_free_classes.append(1)
    test_occupied_startTimes = p.GetStartTimes_By_Classes(filtered_test,0)
    test_occupied_lengths = p.GetLengths_By_Classes(filtered_test,0)
    test_occupied_classes = []
    for i in range (0,len(test_occupied_startTimes)):
        test_occupied_classes.append(0)
        
    #Prepare the format of the points so they can be presented in the xy-plane
    training_points = p.Prepare_Plane(training_startTimes,training_lengths)
    test_free_points = p.Prepare_Plane(test_free_startTimes,test_free_lengths)
    test_occupied_points = p.Prepare_Plane(test_occupied_startTimes,test_occupied_lengths)
    
    #Create the wKNN object
    wknn = sv.wKNN(training_points,training_classes,predicted_length)
    probabilities = wknn.predict(predicted_length)
    
    total_training_hours = 0
    free_training_hours = 0
    occupied_training_hours = 0
    for i in range (0,len(training_points)):
        total_training_hours += training_points[i][1]
        if (training_classes[i] == 1):
            free_training_hours  += training_points[i][1]
    #threshold_value = (free_training_hours/total_training_hours)*100
   
    
    #Top3 method: Choosing the top3 highest probabilities
    top_3 = [0.003,0.002,0.001]
    new_value = 0
    for i in range (0,len(probabilities)):
        for j in range (0,3):
            if ( np.all(probabilities[i][1] >= top_3[j]) and new_value == 0 ):
                top_3[j] = probabilities[i]
                new_value = 1
        new_value = 0
    predicted_times.append(top_3[0])
    predicted_times.append(top_3[1])
    predicted_times.append(top_3[2])
    
    """     
    for i in range (0,len(probabilities)):
        #if (probabilities[i][1] >= threshold_value):
            predicted_times.append(probabilities[i])
    """
    
    total_test_hours = 0
    free_test_hours = 0
    occupied_test_hours = 0
    successful_predictions = 0
    pred_counter = 0
    
    for i in range (0,len(test_free_points)):
        total_test_hours += test_free_points[i][1]
        free_test_hours  += test_free_points[i][1]
    for i in range (0,len(test_occupied_points)):
        total_test_hours += test_occupied_points[i][1]
        occupied_test_hours += test_occupied_points[i][1]
    
    #Calculate predicted free-time
    for i in range (0,len(test_free_points)):
        for j in range(0,len(predicted_times)):
            tid = 0
            #Store the start and end times in temporary variables
            pred_start = predicted_times[j][0]
            pred_end = pred_start+predicted_length
            start_time = test_free_points[i][0]
            end_time = start_time+test_free_points[i][1]
            
            if ((pred_start >= start_time) and (pred_start < end_time)):
            #true
                if (pred_end <= end_time):
                    #true
                    tid = pred_end - pred_start
                else:
                    #false
                    tid = end_time - pred_start
                    
            #false
            elif ((pred_start < start_time) and (pred_end >= start_time) and (pred_end <= end_time)):
                #true
                tid = pred_end - start_time
            if (tid != 0):
                successful_predictions += tid
            pred_counter += predicted_length
    
    
    print("--------------------------------------------")
    print(str(predicted_times) + '\n')
    print("Kalender: " + str(kalender) + " , Veckodag: " + str(weekday))
    print("Totala timmar [h]: " + str(total_test_hours))
    print ("Lediga timmar [h]: " + str(free_test_hours))
    print ("Upptagna timmar [h]: " + str(occupied_test_hours) + '\n')
    print("Lyckad prediktion [h]: " + str(successful_predictions))
    print("Totala prediktioner [h]: " + str(pred_counter) + '\n')
    return

""""------------------------------------------------------------------------"""
def Logistic_Regression(kalender,predicted_length,weekday):
    """
    Method used to test the Logistic Regression prototype
    
    :param kalender: The calendar to use
    :param predicted_length: Duration of the predicted block
    :param weekday: The specific weekday to perform tests on
    """
    predicted_times = []
    file = "scheman/" + str(kalender) + ".csv"
    
    n_timeblocks = p.Get_n_blocks(file)
    thumb_rule = [np.floor(n_timeblocks*(2/3)),n_timeblocks]
    
    """
    #6 månad test data
    last_testBlock = p.Get_Block_By_Index(file,n_timeblocks)
    first_testBlock = p.Get_Index_By_Date(file,[last_testBlock[0][0],last_testBlock[0][1]-6,last_testBlock[0][2]])
    test_data = [first_testBlock, last_testBlock]
    """
    
    """
    #Specific training and test interval
    test_startBlock = p.Get_Block_By_Index(file,np.floor(n_timeblocks*(2/3)))
    training_start = p.Get_Index_By_Date(file,[test_startBlock[0][0]-1,test_startBlock[0][1],test_startBlock[0][2]])
    one_year_training = [training_start, np.floor(n_timeblocks*(2/3))-1]
    """

    training_set = p.Fetch_Data(file,0, thumb_rule[0] ) #
    test_set = p.Fetch_Data(file, thumb_rule[0] , thumb_rule[1] ) #
    p.InsertFreeSpace(training_set,[1,0]) #
    p.InsertFreeSpace(test_set,[1,0]) #
                     
    #Filter by a specific weekday
    filtered_training = p.GetBlocksByWeekday(training_set,weekday)
    filtered_test = p.GetBlocksByWeekday(test_set,weekday)
    n_of_days = p.GetNumberOfDays(filtered_test,weekday)+p.GetNumberOfDays(filtered_training,weekday)
    
    #Both freespace and occupied blocks
    training_startTimes = p.GetStartTimes_decimal(filtered_training)
    training_lengths = p.GetLengths(filtered_training)
    training_classes = []
    for i in range (0,len(filtered_training)):
        for j in range (0,len(filtered_training[i][1])):
            training_classes.append( filtered_training[i][3][j] )
    
    
    #Save the free and occupied test times
    test_free_startTimes = p.GetStartTimes_By_Classes(filtered_test,1)
    test_free_lengths = p.GetLengths_By_Classes(filtered_test,1)
    test_free_classes = []
    for i in range (0,len(test_free_startTimes)):
        test_free_classes.append(1)
    test_occupied_startTimes = p.GetStartTimes_By_Classes(filtered_test,0)
    test_occupied_lengths = p.GetLengths_By_Classes(filtered_test,0)
    test_occupied_classes = []
    for i in range (0,len(test_occupied_startTimes)):
        test_occupied_classes.append(0)
        
    #Prepare the format of the points so they can be presented in the xy-plane
    training_points = p.Prepare_Plane(training_startTimes,training_lengths)
    test_free_points = p.Prepare_Plane(test_free_startTimes,test_free_lengths)
    test_occupied_points = p.Prepare_Plane(test_occupied_startTimes,test_occupied_lengths)
    
    total_training_hours = 0
    free_training_hours = 0
    occupied_training_hours = 0
    for i in range (0,len(training_points)):
        total_training_hours += training_points[i][1]
        if (training_classes[i] == 1):
            free_training_hours  += training_points[i][1]
    threshold_value = (free_training_hours/total_training_hours)*100
    
    #Create the log_reg object
    lr = sv.LogRegression([training_startTimes,training_lengths],training_classes)
    prediction = 0
    for x in p.decimal_range(8,17,(0.25)):
        prediction = lr.Predict([x,predicted_length])
        #if (prediction[0][1] >= threshold_value):
        predicted_times.append( [x,prediction[0][1]] )
                      
    
    total_test_hours = 0
    free_test_hours = 0
    occupied_test_hours = 0
    successful_predictions = 0
    pred_counter = 0
    
    for i in range (0,len(test_free_points)):
        total_test_hours += test_free_points[i][1]
        free_test_hours  += test_free_points[i][1]
    for i in range (0,len(test_occupied_points)):
        total_test_hours += test_occupied_points[i][1]
        occupied_test_hours += test_occupied_points[i][1]
    
    #Calculate predicted free-time
    for i in range (0,len(test_free_points)):
        for j in range(0,len(predicted_times)):
            tid = 0
            #Store the start and end times in temporary variables
            pred_start = predicted_times[j][0]
            pred_end = pred_start+predicted_length
            start_time = test_free_points[i][0]
            end_time = start_time+test_free_points[i][1]
            
            if ((pred_start >= start_time) and (pred_start < end_time)):
            #true
                if (pred_end <= end_time):
                    #true
                    tid = pred_end - pred_start
                else:
                    #false
                    tid = end_time - pred_start
                    
            #false
            elif ((pred_start < start_time) and (pred_end >= start_time) and (pred_end <= end_time)):
                #true
                tid = pred_end - start_time
            if (tid != 0):
                successful_predictions += tid
            pred_counter += predicted_length
    
    print("--------------------------------------------")
    #print(str(predicted_times) + '\n')
    print("Kalender: " + str(kalender) + " , Veckodag: " + str(weekday))
    print("Threshold value: " + str(threshold_value))
    print("Totala timmar [h]: " + str(total_test_hours))
    print ("Lediga timmar [h]: " + str(free_test_hours))
    print ("Upptagna timmar [h]: " + str(occupied_test_hours) + '\n')
    print("Lyckad prediktion [h]: " + str(successful_predictions))
    print("Totala prediktioner [h]: " + str(pred_counter) + '\n')   
    
    #Plotta beslutslinjen
    first_prediction = 0
    for i in range(0, len(predicted_times)):
            if (first_prediction != 1):
                plt.scatter(predicted_times[i][0],predicted_times[i][1],c='r',s=3,marker='o', label="Prediction")
                first_prediction = 1
            else:
                plt.scatter(predicted_times[i][0],predicted_times[i][1],c='r',s=3,marker='o')
    plt.axhline(y=threshold_value, color='g', linestyle='-', label="Threshold")
    plt.title("Kalender " + str(kalender) + ": Beslutslinje")
    plt.xlabel('Tid på dygnet [h]')
    plt.ylabel('Sannolikhet att tiden är ledig [%]')
    
    # Now add the legend with some customizations.
    legend = plt.legend(loc='upper center', shadow=True, bbox_to_anchor=(1.0, 1.2))
    
    # The frame is matplotlib.patches.Rectangle instance surrounding the legend.
    frame = legend.get_frame()
    frame.set_facecolor('0.90')
    
    # Set the fontsize
    for label in legend.get_texts():
        label.set_fontsize('large')
    for label in legend.get_lines():
        label.set_linewidth(1.5)  # the legend line width
    plt.show()
    
    return