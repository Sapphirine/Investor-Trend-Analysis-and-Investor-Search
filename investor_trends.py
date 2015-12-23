#input args: number of clusters, input file, mode
#requred files in folder: holder_country.csv, sec_country.csv, sector.csv, inst_type.csv
import sys
import copy
import locale
import numpy as np
from numpy import genfromtxt
from sklearn.cluster import MiniBatchKMeans
from sklearn import preprocessing

locale.setlocale(locale.LC_ALL, 'en_US.utf8')

def normalize_column(A, col):
        A[:,col] = (A[:,col] - np.min(A[:,col]))/(np.max(A[:,col])-np.min(A[:,col]))

#read dictionary for categorical features from input files
#-----------------------------
def read_dictionary(d, file_name):
        with open(file_name) as f:
                for line in f:
                        (val, key) = line.split(',')
                        d[int(key)] = val
print "reading investor country dictionary"
investor_country_d = {}
read_dictionary(investor_country_d, "holder_country.csv")
print len(investor_country_d), "investor countries loaded"

increasing_d = { 0: "holding", 1: "decreasing", 2: "increasing"}

print "reading security country dictionary"
sec_country_d = {};
read_dictionary(sec_country_d, "sec_country.csv")
print len(sec_country_d), " security countries loaded"

print "reading security gics sector dictionary"
sector_d = {}
read_dictionary(sector_d, "sector.csv")
print len(sector_d), " sectors loaded"

print "reading investor institution type dictionary"
inst_type_d = {}
read_dictionary(inst_type_d, "inst_type.csv")
print len(inst_type_d), " inst types loaded"
#-----------------------------

#process arguments
#-----------------------------
num_clusters = 5;
if len(sys.argv)>1:
        num_clusters = int(sys.argv[1])
print "num clusters ", num_clusters

file_name = 'out_file.csv'
if len(sys.argv)>2:
        file_name = str(sys.argv[2])
print "file_name:", file_name

#mode 1: 7 cols, 5 categorical cols, 2 mkt val & market cap
#mode 2: 10 additional cols, % portfolio in GICS sector
mode = 1
if len(sys.argv)>3:
        mode = int(sys.argv[3])
print "mode:", mode
#-----------------------------

#read data from input file and pre-process data
#-----------------------------
print "reading from input file"
#print "Reading first 5 cols from file into data1"
data1 = genfromtxt(file_name, delimiter=',', usecols = (0,1,2,3,4))
#print "data1.shape", data1.shape
data1[np.isnan(data1)] = 0
#print "Reading last 2 cols from file into data2"
data2 = genfromtxt(file_name, delimiter=',', usecols = (5, 6))
#print "data2.shape", data2.shape
data2[np.isnan(data2)] = 0

data3 = []
if mode==2:
        print "Reading percent portfolio cols from file"
        data3 = genfromtxt(file_name, delimiter=',', usecols = (7,8,9,10,11,12,13,14,15,16))
        #print "data3.shape", data3.shape
        data3[np.isnan(data3)]=0

#print "max values of data1"
print data1.max(axis=0)

#print "min values of data1"
print data1.min(axis=0)

#print "max values of data2"
print data2.max(axis=0)

#print "min values of data2"
print data2.min(axis=0)

print "Encoding categorical features"
enc = preprocessing.OneHotEncoder(n_values=[len(investor_country_d), len(increasing_d), len(sec_country_d), len(sector_d), len(inst_type_d)])
enc.fit(data1)
print "n_values_"
print  enc.n_values_
print "feature_indices_", enc.feature_indices_
categorical_features = enc.transform(data1).toarray()
#print "categorical_features.shape", categorical_features.shape

#print "raw data2 line 0"
#print data2[0]
original_data2 = copy.copy(data2)
print "normalizing market value and market cap"
normalize_column(data2, 0)
normalize_column(data2, 1)
#print "normalized data2 line 0"
#print data2[0]

if mode==2:
        #print "data3[0] before:", data3[0]
        print "reducing percent portfolio to percentages"
        data3/=100
        #print "data3[0] after:", data3[0]

#print "combining two arrays"
final_array = np.append(categorical_features, data2, 1)
print "final_array.shape", final_array.shape

if mode==2:
        #print "combining last array"
        final_array = np.append(final_array, data3, 1)
        print "final_array.shape", final_array.shape
#-----------------------------

#clustering with mini batch kmeans
#-----------------------------
print "clustering"
mbk = MiniBatchKMeans(n_clusters=num_clusters)
mbk.fit(final_array)

#print "labels:"
#print mbk.labels_
#print "cluster_centers:"
#print mbk.cluster_centers_

category_column_count = len(categorical_features[0])
centers = mbk.cluster_centers_
feature_indices = enc.feature_indices_
#-----------------------------

#interpreting results
#-----------------------------
def get_feature(row_index):
        global feature_indices
        global investor_country_d
        global increasing_d
        global sec_country_d
        global sector_d
        global inst_type_d
        if row_index<feature_indices[1]:
                print "Investor country:", investor_country_d[row_index-feature_indices[0]]
        elif row_index<feature_indices[2]:
                print "Change: ", increasing_d[row_index-feature_indices[1]]
        elif row_index<feature_indices[3]:
                print "Security Country:", sec_country_d[row_index-feature_indices[2]]
        elif row_index<feature_indices[4]:
                print "Security GICS sector:", sector_d[row_index-feature_indices[3]]
        elif row_index<feature_indices[5]:
                print "Investor Institution Type:", inst_type_d[row_index-feature_indices[4]]

def print_market_value(i, index):
        value=i*(np.max(original_data2[:,index]) - np.min(original_data2[:,index]))
        print "Investor Market Value:", locale.format("%d", value, grouping=True)

def print_market_cap(i, index):
        value=i*(np.max(original_data2[:,index]) - np.min(original_data2[:,index]))
        print "Security Market Cap:", locale.format("%d", value, grouping=True)
        

def undo_normalization(i, row_index):
        global data2
        global category_column_count
        global original_data2
        index = row_index-category_column_count
        if index==0:
                print_market_value(i, index)
        elif index==1:
                print_market_cap(i, index)
        elif index==2:
                print "Percent Portfolio in Consumer Discrtionary", i
        elif index==3:
                print "Percent Portfolio in Consumer Stapes", i
        elif index==4:
                print "Percent Portfolio in Energy", i
        elif index==5:
                print "Percent Portfolio in Financials", i
        elif index==6:
                print "Percent Portfolio in Healthcare", i
        elif index==7:
                print "Percent Portfolio in Industrials", i
        elif index==8:
                print "Percent Portfolio in Information Technology", i
        elif index==9:
                print "Percent Portfolio in Materials", i
        elif index==10:
                print "Percent Portfolio in Telecommunication Services", i
        elif index==11:
                print "Percent Portfolio in Utilities", i

def interpret_center(center):
        col_index = 0
        for i in center:
                global category_column_count
                if col_index<category_column_count:
                        if i>=0.5:
                                get_feature(col_index)
                else:
                        undo_normalization(i, col_index)
                col_index+=1

center_index = 0;
#sort centers by investor market value size
centers[np.argsort(centers[:,5])]
for center in centers:
        print "cluster center ", center_index
        interpret_center(center);
        center_index+=1;

