"""
This module represents the DBSCAN algorithm. 
"""
import matplotlib.pyplot as plt
import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.neighbors import NearestNeighbors
import Preprocessor as p


class DB_SCAN:
    model = 0 #The algorithm model
    training_set = []
    n_trainingData = 0 #Amount of training data evaluated using KNNdistPlot
    clustered_data = []
    labels = 0 #Array containing the labels of every point on the plane
    n_clusters = 0 #Number of clusters
    object_name = "nil"
    predicted_length = 0 #The length of the block to be predicted
    
    def __exit__(self, *err):
        """
        This function closes the DBSCAN instances which are not in use
        """
        self.close()
    
    def __init__(self,object_name):
        """
        Initialize the object with an associated name
        
        :param object_name: The name of the object created
        """
        self.object_name = object_name
    
    
    def Get_distanceMean(self,points,minPts,previous_distanceMean):
        """
        Method used to calculate the mean of the neighbors distances
        
        :param points: List containing the training-points you want to use
        :param minPts: Minimum number of points to be considered a cluster
        :param previous_distanceMean: The previous mean of the distances
        :return: Average distance between the points
        """
        
        if (minPts < len(points)):
            nbrs = NearestNeighbors(n_neighbors=minPts).fit(points)
            distances, indices = nbrs.kneighbors(points)
            d_mean = distances.mean()
            return d_mean
        else:
            return previous_distanceMean
            
    
    def KNNdist_plot(self,points,minPts):
        """
        Calculate where the slope of the kNNdistPlot is higher than a user-defined
       value while plotting the K-NN distance with respect to the amount of 
       training data
       
       :param points: List containing the points you want to use
       :param minPts: Minimum number of points to be considered a cluster
       :return: The most optimal parameter-values i.e Knee point values
       """
        
        epsPlot = []
        current_distanceMean = previous_distanceMean = 0
        knee_value = knee_found = 0
    
        for i in range (0,len(points),5):
            current_distanceMean = self.Get_distanceMean(points[i:],minPts,previous_distanceMean)
            df = current_distanceMean - previous_distanceMean
            
            #print("x=" + str(i) + " , df=" + str(df))
            if (df > 0.02 and i > 1 and knee_found == 0):
                knee_value = current_distanceMean
                knee_found = 1
                self.n_trainingData = i
                #knee_x = i
                
            epsPlot.append( [i,current_distanceMean] )
            previous_distanceMean = current_distanceMean
        
        
        #Plot the kNNdistPlot
        for i in range(0, len(epsPlot)):
                    plt.scatter(epsPlot[i][0],epsPlot[i][1],c='r',s=3,marker='o')
        plt.axhline(y=knee_value, color='g', linestyle='-')
        plt.axvline(x=self.n_trainingData , color='g', linestyle='-')
        plt.title(self.object_name)
        plt.show()
        print("Knee value: x=" + str(self.n_trainingData) + " , y=" + str(knee_value))
        #tm.Plot(epsPlot)
        
        return knee_value
        
    def learn(self,training_data,radius,min_samples,predictedLength):
        """
        Method used to train the algorithm
        
        :param training_data: List containing the learning data
        :param radius: Radius around a point
        :param min_samples: Minimum samples to be considered a cluster
        :param predictedLength: The duration of the predicted block
        :return: returns nothing
        """
        
        self.predicted_length = predictedLength
        for i in range (0,len(training_data)):
            if (training_data[i][1] >= self.predicted_length):
                self.training_set.append(training_data[i])
        
        self.model = DBSCAN(eps=radius,metric='euclidean',min_samples=min_samples)
        self.labels = self.model.fit_predict(self.training_set)
        core_samples = np.zeros_like(self.labels, dtype = bool)
        core_samples[self.model.core_sample_indices_] = True
        
        # Calculate the number of clusters.
        self.n_clusters = len(set(self.model.labels_)) - (1 if -1 in self.model.labels_ else 0)
        
        
        #Plot the points and clusters on a xy-plane
        plt.xlim( (8,18) )
        plt.ylim( (0,10) )
        plt.ymin = 8
        #colors = "bgrcmykw"
        for i in range(0, len(self.training_set)):
            if self.model.labels_[i] == -1:
                plt.scatter(self.training_set[i][0],self.training_set[i][1],c='r',marker='x')
            elif self.model.labels_[i] >= 0:
                plt.scatter(self.training_set[i][0],self.training_set[i][1],c='g',marker='o')
                
        plt.title(self.object_name)
        plt.show()
        #print("Clusters: " + str(self.n_clusters))
        
        return
        
    def predict(self):
        """
        Method used to generate and save the predictions in a list from the clustering
        
        :return: A list containing the predictions
        """
        
        lst = [] #List containing the times and their longest length: i0 = time , i1 = length
        for i in p.decimal_range(8,17,0.25):
            lst.append([i,[]])
        for i in range (0,len(self.training_set)-1):
            if (self.labels[i] >= 0):
                #Only prints out 1 time on 1 x-coordinate (prints the one with the longest length)
                time = self.training_set[i][0]
                length = self.training_set[i][1]
                for j in range (0,len(lst)):
                    if (time == lst[j][0]):
                        lst[j][1].append(length)
        return lst