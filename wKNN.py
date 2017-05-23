import numpy as np
from sklearn.neighbors import KNeighborsClassifier
import Preprocessor as p

"""----------------------Weighted KNN---------------------------------------"""
class wKNN:
    wknn = 0
    training_set = []
    classes = [] #List containing the class of every point on the plane
    n_clusters = 0 #Number of clusters
    object_name = "nil"
    predicted_length = 1 #The length of the block to be predicted
    
    def __exit__(self, *err):
        self.close()
    
    def predict(self,predictedLength):
        """
        Predict probabilities throughout the day where the given block-duration is likely to be available
        
        :param predictedLength: The duration of the predicted block
        :return: A list containing the predicted probabilities
        """
        predicted_times = []
        current_prediction = 0
        for x in p.decimal_range(8,17,0.25):
            current_prediction = (self.wknn.predict_proba([[x,predictedLength]]))*100
            if (current_prediction[0][1] > 0):
                predicted_times.append( [x,current_prediction[0][1]] )
        return predicted_times
        
    
    def __init__(self,inputArray,classes,predictedLength):
        """
        Initialize the object and train it with the inputArray
        
        :param inputArray: Array containing the training data
        :param classes: Array containing the class of every data in the inputArray
        :param predictedLength: The duration of the predicted block
        """
        self.predicted_length = predictedLength
        for i in range (0,len(inputArray)):
            if (inputArray[i][1] >= self.predicted_length):
               self.training_set.append(inputArray[i])
               self.classes.append(classes[i])
        self.wknn = KNeighborsClassifier(n_neighbors = np.sqrt(len(self.training_set)), weights = 'uniform')
        self.wknn.fit(self.training_set,self.classes)