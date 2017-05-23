import numpy as np
from sklearn.linear_model import logistic
import Preprocessor as p

class LogRegression:
    lr = 0
    
    def __init__(self,inputArray,classes):
        """
        Initialize the log_reg object and fit the training_data into the algorithm
        
        :param self: The current object of the class
        :param inputArray: The array used to train the algorithm
        :param classes: Array containing the class of each input
        """
        self.lr = logistic.LogisticRegression()
        d90 = np.rot90(inputArray)
        d90 = np.rot90(d90)
        d90 = np.rot90(d90)        
        self.lr.fit(d90, classes)
        
    def Predict(self,predictInput):
        """
        Method to predict the probability that a point belongs to a class
        
        :param predictInput: A 2D-array containing a point in the xy-plane
        :return: The probability that the point belongs to a specific class
        """
        probs = self.lr.predict_proba( np.reshape((predictInput),([1,-1])) )*100
        return probs #index 0 = occupied , index 1 = free