import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.neighbors import NearestNeighbors
import Preprocessor as p

"""------------------------------------------------------------"""
class K_Means:
    
    def __init__(self,training_data,nr_of_clusters):      
        # K-means
        model = KMeans(n_clusters=nr_of_clusters)
        model.fit(training_data) #inlärning
        model.labels_
        for i in range(0, len(training_data)):
            plt.scatter(training_data[i,0],training_data[i,1],c='b',marker='o')
        plt.title('Timeblocks: K-means')
        plt.show()
        print(model.cluster_centers_[0])




"""--------------------------------DB-SCAN---------------------------------"""
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
        self.close()
    
    def __init__(self,object_name):
        self.object_name = object_name
    
    #Method used to calculate the mean of the neighbors distances
    def Get_distanceMean(self,points,minPts,previous_distanceMean):
        if (minPts < len(points)):
            nbrs = NearestNeighbors(n_neighbors=minPts).fit(points)
            distances, indices = nbrs.kneighbors(points)
            d_mean = distances.mean()
            return d_mean
        else:
            return previous_distanceMean
            
    #Plot the K-NN distance with respect to the amount of training data
    def KNNdist_plot(self,points,minPts):
        epsPlot = []
        current_distanceMean = previous_distanceMean = 0
        knee_value = knee_found = 0
    
        for i in range (0,len(points),5):
            current_distanceMean = self.Get_distanceMean(points[i:],minPts,previous_distanceMean)
            df = current_distanceMean - previous_distanceMean
            
            if (df > 0.02 and i > 1 and knee_found == 0):
                knee_value = current_distanceMean
                knee_found = 1
                self.n_trainingData = i
                
            epsPlot.append( [i,current_distanceMean] )
            previous_distanceMean = current_distanceMean
        
        """
        #Plot the kNNdistPlot
        for i in range(0, len(epsPlot)):
                    plt.scatter(epsPlot[i][0],epsPlot[i][1],c='r',s=3,marker='o')
        plt.axhline(y=knee_value, color='g', linestyle='-')
        plt.axvline(x=self.n_trainingData , color='g', linestyle='-')
        plt.title(self.object_name)
        plt.show()
        print("Knee value: x=" + str(self.n_trainingData) + " , y=" + str(knee_value))
        #tm.Plot(epsPlot)
        """
        
        return knee_value
        
    #Method used to train the algorithm
    def learn(self,training_data,radius,min_samples,predictedLength):
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
        
        """
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
        """
        
        return
        
    def predict(self):
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
        
        
        filteredList = []   
        predictedList = []             
        for i in range (0,len(lst)):
            best = 0
            for j in range (0,len(lst[i][1])):
                if (lst[i][1][j] > best):
                    best = lst[i][1][j]
            filteredList.append([lst[i][0],best])
        for i in range (0,len(filteredList)):
            if (filteredList[i][1] > 0):
                predictedList.append(filteredList[i])        
        return predictedList
        