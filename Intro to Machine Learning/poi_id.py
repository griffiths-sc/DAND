#!/usr/bin/python

# Import required modules

import sys
import pickle
import pandas as pd
import numpy as np
from time import time
sys.path.append("../tools/")

from feature_format import featureFormat, targetFeatureSplit
from tester import test_classifier, dump_classifier_and_data

from sklearn.feature_selection import SelectKBest
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier,ExtraTreesClassifier,AdaBoostClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC,LinearSVC
from sklearn.pipeline import Pipeline
from sklearn.grid_search import GridSearchCV

from collections import OrderedDict

# Load the dictionary containing the dataset
with open("final_project_dataset.pkl", "r") as data_file:
    data_dict = pickle.load(data_file)

# Load the dictionary into a dataframe and examine it
dataset_df=pd.DataFrame.from_dict(data_dict,orient='index')

# Replace 'NaN' string with Null (NaN)
dataset_df.replace('NaN',np.nan,inplace=True)

### Task 1: Select what features you'll use.
### features_list is a list of strings, each of which is a feature name.
### The first feature must be "poi".
# You will need to use more features

POI_label=['poi'] # Boolean, represented as integer

financial_features=['salary','deferral_payments','total_payments','bonus','deferred_income',
                    'total_stock_value','expenses','exercised_stock_options','other',
                    'long_term_incentive','restricted_stock'] # Units are in US dollars

email_features=['to_messages','from_poi_to_this_person','from_messages',
                'from_this_person_to_poi','shared_receipt_with_poi'] # Units are number of emails messages

# We will ignore:
# 'email_address' - not numerical data
# 'restricted_stock_deferred' and 'director_fees' - less than 10% data for POI
# 'loan_advances' - less than 10% data

features_list=(POI_label+financial_features+email_features)
print '\nNumber of initial features: ',len(features_list)

### Task 2: Remove outliers

#Drop email address since we are not using it in this analysis
dataset_df.drop('email_address',axis=1,inplace=True)

#Read in data from supplied enron61702insiderpay.pdf file for comparison
#(edited so column names and employee names coincide and converted to csv)
pdf=pd.read_csv('PDF.csv',index_col=0)

#Calculate differences between initial dataset and correct data
df=dataset_df.rsub(pdf).fillna(0.0)

#Correct dataset
for row in range(len(df)):
    for col, vals in df.iteritems():
        if vals[row] != 0.0:
            old_val=dataset_df.loc[df.index[row],col]
            new_val=pdf.loc[df.index[row],col]
            dataset_df.loc[df.index[row],col]=new_val
            print '\n',df.index[row],col,'corrected from',old_val,'to',new_val

# Drop the following:
# TOTAL - Spreadsheet aggregation included by mistake (outlier)
# LOCKHART EUGENE E - Does not contain any numerical data
# THE TRAVEL AGENCY IN THE PARK - Not an individual (Alliance Worldwide - co-owned by the sister of Enron's former Chairman)

dataset_df.drop(['TOTAL','LOCKHART EUGENE E','THE TRAVEL AGENCY IN THE PARK'],axis=0,inplace=True)

### Task 3: Create new feature(s)

# New financial features:
dataset_df['fraction_bonus_salary']=dataset_df['bonus']/dataset_df['salary']
dataset_df['fraction_bonus_total']=dataset_df['bonus']/dataset_df['total_payments']
dataset_df['fraction_salary_total']=dataset_df['salary']/dataset_df['total_payments']
dataset_df['fraction_stock_total']=dataset_df['total_stock_value']/dataset_df['total_payments']

# New email features:
dataset_df['fraction_to_poi']=dataset_df['from_this_person_to_poi']/dataset_df['from_messages']
dataset_df['fraction_from_poi']=dataset_df['from_poi_to_this_person']/dataset_df['to_messages']

# Add new features to feature list
new_features_list=['fraction_bonus_salary',
                        'fraction_bonus_total',
                        'fraction_salary_total',
                        'fraction_stock_total',
                        'fraction_to_poi',
                        'fraction_from_poi']
extended_features_list=features_list+new_features_list
print '\nNumber of extended features: ',len(extended_features_list)

# Replace Null (NaN) entries with 0.0 to prevent errors in algorithms
dataset_df.fillna(value=0.0,inplace=True)

### Store to my_dataset for easy export below.
my_dataset=dataset_df.to_dict('index')

### Extract original features and labels from dataset
#data=featureFormat(my_dataset,features_list,sort_keys=True)
#labels,features=targetFeatureSplit(data)

### Extract extended features and labels from dataset
data=featureFormat(my_dataset,extended_features_list,sort_keys=True)
labels2,features2=targetFeatureSplit(data)

### Task 4: Try a varity of classifiers
### Please name your classifier clf for easy export below.
### Note that if you want to do PCA or other multi-stage operations,
### you'll need to use Pipelines. For more info:
### http://scikit-learn.org/stable/modules/pipeline.html

def classify(clf):
    perf_labels=('Accuracy',
                 'Precision',
                 'Recall',
                 'F1',
                 'F2',
                 'Total predictions',
                 'True positives',
                 'False positives',
                 'False negatives',
                 'True negatives')
    t0=time()
    s='\nClassifier: '+str(clf.named_steps.clf)[:str(clf.named_steps.clf).find('(')]
    u='-'*len(s)
    print(s+'\n'+u)
    perf_metrics=test_classifier(clf,my_dataset,extended_features_list)
    print('Elapsed time: %0.3fs' % (time()-t0))
    return perf_labels,perf_metrics

#Decision Tree Classifier (Unscaled)
pipeline=Pipeline([('kbest',SelectKBest()),
                   ('clf',DecisionTreeClassifier())])
clf=pipeline.fit(features2,labels2)
perf_labels,perf_metrics=classify(clf)

#Decision Tree Classifier (Scaled)
pipeline=Pipeline([('scaler',StandardScaler()),
                   ('kbest',SelectKBest()),
                   ('clf',DecisionTreeClassifier())])
clf=pipeline.fit(features2,labels2)
perf_labels,perf_metrics=classify(clf)

#Random Forest Classifier (Unscaled)
pipeline=Pipeline([('kbest',SelectKBest()),
                   ('clf',RandomForestClassifier())])
clf=pipeline.fit(features2,labels2)
perf_labels,perf_metrics=classify(clf)

#Extra Trees Classifier (Unscaled)
pipeline=Pipeline([('kbest',SelectKBest()),
                   ('clf',ExtraTreesClassifier())])
clf=pipeline.fit(features2,labels2)
perf_labels,perf_metrics=classify(clf)

#AdaBoost Classifier (Unscaled)
pipeline=Pipeline([('kbest',SelectKBest()),
                   ('clf',AdaBoostClassifier())])
clf=pipeline.fit(features2,labels2)
perf_labels,perf_metrics=classify(clf)

#Support Vector Classifier (Scaled)
pipeline=Pipeline([('scaler',StandardScaler()),
                   ('kbest',SelectKBest()),
                   ('clf',SVC(kernel="linear"))])
clf=pipeline.fit(features2,labels2)
perf_labels,perf_metrics=classify(clf)

#Linear Support Vector Classifier (Scaled)
pipeline=Pipeline([('scaler',StandardScaler()),
                   ('kbest',SelectKBest()),
                   ('clf',LinearSVC())])
clf=pipeline.fit(features2,labels2)
perf_labels,perf_metrics=classify(clf)

#K Neighbors Classifier (Unscaled)
pipeline=Pipeline([('kbest',SelectKBest()),
                   ('clf',KNeighborsClassifier())])
clf=pipeline.fit(features2,labels2)
perf_labels,perf_metrics=classify(clf)

#K-Neighbors Classifier (Scaled)
pipeline=Pipeline([('scaler',StandardScaler()),
                   ('kbest',SelectKBest()),
                   ('clf',KNeighborsClassifier())])
clf=pipeline.fit(features2,labels2)
perf_labels,perf_metrics=classify(clf)

### Task 5: Tune your classifier to achieve better than .3 precision and recall 
### using our testing script. Check the tester.py script in the final project
### folder for details on the evaluation method, especially the test_classifier
### function. Because of the small size of the dataset, the script uses
### stratified shuffle split cross validation. For more info: 
### http://scikit-learn.org/stable/modules/generated/sklearn.cross_validation.StratifiedShuffleSplit.html

#DecisionTree Classifier
pipeline=Pipeline([('scaler',StandardScaler()),
                   ('kbest',SelectKBest()),
                   ('clf',DecisionTreeClassifier())])
param_grid=([{'kbest__k':[6,12,18],
              'clf__max_depth':[None,1,2],
              'clf__min_samples_split':[10,20,30],
              'clf__class_weight':[None,'balanced']}])
clf=GridSearchCV(pipeline,param_grid,scoring='f1').fit(features2,labels2).best_estimator_
perf_labels,perf_metrics=classify(clf)

#AdaBoost Classifier
pipeline=Pipeline([('kbest',SelectKBest()),
                   ('clf',AdaBoostClassifier())])
param_grid=([{'kbest__k':[6,12,18],
              'clf__base_estimator':[DecisionTreeClassifier(class_weight='balanced',max_depth=1),
                                     DecisionTreeClassifier(class_weight='balanced',max_depth=2)],
              'clf__n_estimators':[25,50,75],
              'clf__learning_rate':[0.01,0.1,1.0],
              'clf__algorithm':['SAMME']}])
clf=GridSearchCV(pipeline,param_grid,scoring='f1').fit(features2,labels2).best_estimator_
perf_labels,perf_metrics=classify(clf)

#Store this classifiers parameters and scores
CLF=clf
final_kbest=CLF.named_steps.kbest
final_clf=CLF.named_steps.clf
final_perf_labels=perf_labels
final_perf_metrics=perf_metrics

#K Neighbors Classifier (Unscaled)
pipeline=Pipeline([('kbest',SelectKBest()),
                   ('clf',KNeighborsClassifier())])
param_grid=([{'kbest__k':[6,12,18],
              'clf__n_neighbors':[3,4,5]}])
clf=GridSearchCV(pipeline,param_grid,scoring='f1').fit(features2,labels2).best_estimator_
perf_labels,perf_metrics=classify(clf)

#Best performing algorithm - AdaBoost Classifier using SelectKBest to select features:

#Select K-Best
n=final_kbest.k
k_best=final_kbest
k_best.fit(features2,labels2)
feature_scores=zip(extended_features_list[1:],k_best.scores_)
k_best_features=OrderedDict(sorted(feature_scores,key=lambda x: x[1]))

#AdaBoost Classifier
clf=final_clf
clf=clf.fit(k_best.transform(features2),labels2)

feature_importances=zip(extended_features_list[1:],clf.feature_importances_)
important_features=OrderedDict(sorted(feature_importances,key=lambda x: x[1]))

#Output Classifier Parameters
print '\nBest performing classifier: '+str(final_clf)[:str(final_clf).find('(')]+'\n'
for k in CLF.named_steps.values():
    print k

#Output Performance Metrics
print '\nPerformance Metrics:\n'
print '{:25}{:15}'.format('Metric:','Score:')
for k in range(5):
    print('{:25}{:8.2%}'.format(final_perf_labels[k],final_perf_metrics[k]))
for k in range(5,10):
    print('{:25}{:8d}'.format(final_perf_labels[k],final_perf_metrics[k]))

#Output Feature Scores and Feature Importances
print '\nFeature Scores:\n'
print('{:30}{:15}{:15}'.format('Feature:','Score:','Importance:'))
for k in extended_features_list[1:]:
    print('{:29}{:8.4f}{:14.4f}'.format(k,k_best_features[k],(important_features[k] if (k in important_features) else 0.0)))

### Task 6: Dump your classifier, dataset, and features_list so anyone can
### check your results. You do not need to change anything below, but make sure
### that the version of poi_id.py that you submit can be run on its own and
### generates the necessary .pkl files for validating your results.

dump_classifier_and_data(CLF,my_dataset,extended_features_list)