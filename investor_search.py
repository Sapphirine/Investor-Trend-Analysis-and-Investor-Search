#input args: holder file name, non-holder file name, number of clusters
#required files in folder: sector.csv, holder_index.csv, sec_prop.csv, sec_fundamentals.csv
import sys
import numpy as np
from numpy import genfromtxt
from sklearn import preprocessing
from sklearn.linear_model import SGDClassifier
from sklearn.cluster import KMeans

holders_name_d = {}
holders_d = {}
holders_trans_d = {}

def read_dictionary(d, file_name):
        with open(file_name) as f:
                for line in f:
                        (key,val) = line.split(',')
                        d[str(key)] = val

def normalize_column(A, col):
        A[:,col] = (A[:,col] - np.min(A[:,col]))/(np.max(A[:,col])-np.min(A[:,col]))

def clone_rows(row, n_clone):
        new_array = [row]
        for i in range(1, n_clone):
                new_array = np.append(new_array, [row], 0)
        return new_array

#clustering security holdings for an investor
def get_clusters(data, lid, clusters, sec_prop):
        #print data[0]
        global holders_d
        categorical_features = data[:,0]
        #print categorical_features.shape, len(data)
        categorical_features = np.reshape(categorical_features, (len(data), 1))
        features = data[:,1:10]
        #print features.shape
        enc = preprocessing.OneHotEncoder(n_values=[len(sector_d)])
        enc.fit(categorical_features)
        cat_data=enc.transform(categorical_features).toarray()
        final_array = np.append(cat_data, features, 1)
        km = KMeans(init='k-means++', n_clusters=clusters, n_init=10)
        km.fit(final_array)
        holders_d[lid]=km.cluster_centers_
        prediction = km.predict(sec_prop)
        for k in prediction:
                center = km.cluster_centers_[k]
                center_array = clone_rows(center, clusters)
                holders_trans_d[lid] = center_array


print "reading sector dictionary"
sector_d = {}
read_dictionary(sector_d, "sector.csv")
print len(sector_d), "sectors loaded"

#reading input args
#------------------------------------
holders_file = 'holders.csv'
non_holders_file = 'non_holders.csv'
n_clusters = 10

if len(sys.argv)>2:
        holders_file = str(sys.argv[1])
        non_holders_file = str(sys.argv[2])
if len(sys.argv)>3:
        n_clusters = int(sys.argv[3])
print holders_file, non_holders_file
print "holdes file:", holders_file, " non-holders file:", non_holders_file, " num clusters:", n_clusters

#reading from input files
#------------------------------------
print "Reading from holders files"
read_dictionary(holders_name_d, holders_file)
read_dictionary(holders_name_d, non_holders_file)
holder_data = genfromtxt(holders_file, delimiter=',',dtype=str, usecols=[0])
non_holder_data = genfromtxt(non_holders_file, delimiter=',',dtype=str, usecols=[0])
holder_index = genfromtxt("holder_index.csv", delimiter=',')
all_holder_names = genfromtxt("sec_fundamentals.csv", delimiter=',', dtype=str, usecols=[0])
all_holders = genfromtxt("sec_fundamentals.csv", delimiter=',', usecols=[2,3,4,5,6,7,8,9,10,11])
all_holders[np.isnan(all_holders)]=0
normalize_column(all_holders, 9)
sec_prop_cat = genfromtxt("sec_prop.csv", delimiter=',', usecols=[0])
sec_prop_cat = np.reshape(sec_prop_cat, (1, 1))
sec_enc = preprocessing.OneHotEncoder(n_values=[len(sector_d)])
sec_enc.fit(sec_prop_cat)
sec_prop_cat1 = sec_enc.transform(sec_prop_cat).toarray()
sec_prop = genfromtxt("sec_prop.csv", delimiter=',', usecols=[1,2,3,4,5,6,7,8,9])
sec_prop = np.reshape(sec_prop, (1, 9))
sec_prop[np.isnan(sec_prop)]=0
sec_prop[0,8] = (sec_prop[0,8] - np.min(all_holders[:,9]))/(np.max(all_holders[:,9])-np.min(all_holders[:,9]))
sec_prop = np.append(sec_prop_cat1, sec_prop, 1)
#print "names.shape ", all_holder_names.shape, " all_holders ", all_holders.shape
#print "holders_d size", len(holders_d)
#print "holders size:", holder_data.shape, " non holders size:", non_holder_data.shape
#print holder_data[0]
#print non_holder_data[0]
#print "holder index size:", holder_index.shape
#print "all holders size:", all_holders.shape
#print "sec prop shape", sec_prop.shape
#print "holder name dict size:", len(holders_name_d)


#finding cluster centers for each investor
#------------------------------------
start_index = 0;
for i in holder_index:
        data = all_holders[start_index:i][:]
        lid = all_holder_names[start_index]
        get_clusters(data, lid, n_clusters, sec_prop)
        start_index=i


#shaping input
#------------------------------------
holder_center_array = []
holder_center_trans_array = []
index = 0;
for i in holder_data:
        #print i
        centers_trans = holders_trans_d[i]
        centers = holders_d[i]
        if index==0:
                holder_center_array = centers
                holder_center_trans_array = centers_trans
                index+=1
        else:
                holder_center_array = np.append(holder_center_array, centers, 0)
                holder_center_trans_array = np.append(holder_center_trans_array, centers_trans, 0)
#print "holder_center_array.shape", holder_center_array.shape
#print "holder_center_trans_array.shape", holder_center_trans_array.shape
#print holder_center_array[0]
#print holder_center_trans_array[0]

non_holder_center_array = []
index = 0
for i in non_holder_data:
        #print i
        centers = holders_d[i]
        if index==0:
                non_holder_center_array = centers
                index+=1
        else:
                non_holder_center_array = np.append(non_holder_center_array, centers, 0)
#print "non-holder_center_array.shape", non_holder_center_array.shape
#print non_holder_center_array[0]

holder_target = [1]*len(holder_center_array)
non_holder_target = [0]*len(non_holder_center_array)
target_data = np.append(holder_target, non_holder_target, 1)
#print "target_data.shape", target_data.shape
center_array = np.append(holder_center_trans_array, non_holder_center_array, 0)
#print "center_array.shape", center_array.shape


#testing data
test_count1 = int(len(holder_center_array)/n_clusters)
test_count2 = int(len(non_holder_center_array)/n_clusters)
#print "test_count1:", test_count1, " test_count2:", test_count2

test_data1 = holder_center_array[0:test_count1][:]
test_data2 = non_holder_center_array[0:test_count2][:]
#print "test_data1.shape", test_data1.shape
#print "test_data2.shape", test_data2.shape

#train classifier
#------------------------------------
clf = SGDClassifier(loss="hinge")
#clf.fit(data1, data_target)
clf.fit(center_array, target_data)

print "clf.coef_", clf.coef_
print "clf.intercept_", clf.intercept_

#testing classifier
#------------------------------------
wrong_count1 = 0
right_count1=0
count = 0
single_right_count1 = 0
count_array1 = [0]*(n_clusters+1)
for i in test_data1:
        value = clf.predict([i])
        #print value
        if value==1:
                single_right_count1+=1
        if count==(n_clusters-1):
                if single_right_count1>0:
                        right_count1+=1
                else:
                        wrong_count1+=1
                count = 0
                count_array1[single_right_count1]+=1
                single_right_count1=0
        else:
                count+=1
print "test holders:", count_array1

wrong_count2 = 0
right_count2 = 0
count = 0
single_right_count2 = 0
count_array2 = [0]*(n_clusters+1)
for i in test_data2:
        value = clf.predict([i])
        #print value
        if value==1:
                single_right_count2+=1
        if count==(n_clusters-1):
                if single_right_count2>0:
                        wrong_count2+=1
                else:
                        right_count2+=1
                count = 0
                count_array2[single_right_count2]+=1
                single_right_count2 = 0
        else:
                count+=1
print "test non-holders:", count_array2


#classify all non-holders
#------------------------------------
wrong_count3 = 0
right_count3 = 0
count = 0
single_right_count3 = 0
count_array = [0]*(n_clusters+1)
index_count=0
investor_array = []
for i in non_holder_center_array:
        value = clf.predict([i])
        if value==1:
                #print non_holder_names[rec_index]
                single_right_count3+=1
        if count==(n_clusters-1):
                if single_right_count3>0:
                        wrong_count3+=1
                else:
                        right_count3+=1
                count = 0
                count_array[single_right_count3]+=1
                lid = non_holder_data[index_count]
                name = holders_name_d[lid]
                if len(investor_array)==0:
                        investor_array = [[lid, int(single_right_count3), name]]
                else:
                        investor_array = np.append(investor_array, [[lid, int(single_right_count3), name]], 0)
                single_right_count3=0
                index_count+=1
        else:
                count+=1
print "all non-holders:", count_array
print "investor_array.shape", investor_array.shape
investor_array = investor_array[np.argsort(investor_array[:,1])]
investor_count = 0
for i in reversed(investor_array):
        print i
        if investor_count>10:
                break
        investor_count+=1







