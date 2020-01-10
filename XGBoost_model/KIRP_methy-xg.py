
# coding: utf-8

import xgboost
from sklearn.model_selection import GridSearchCV
import numpy as np
from sklearn.model_selection import  KFold
from sklearn.metrics import accuracy_score, roc_auc_score

class GV:

    def xg_find_base(self, scoring, data_x, data_y, model_xg, params, overfit=None):
        kfold = KFold(n_splits=3, shuffle=False, random_state=7)
        params = {}
        params_test1 = {"max_depth": np.arange(3, 8, 1)}
        clf = GridSearchCV(model_xg, params_test1, cv=kfold, n_jobs=-1, scoring=scoring)
        clf.fit(data_x, data_y)
        params.update({'max_depth': clf.best_params_["max_depth"]})
        model_xg.max_depth = clf.best_params_["max_depth"]
        print(clf.best_params_)
        print("clf.best_score_", clf.best_score_)

        params_test1 = {"learning_rate": [0.005,0.01,0.03,0.05,0.07,0.1,0.13,0.15,0.2]}
        clf = GridSearchCV(model_xg, params_test1, cv=kfold, n_jobs=-1, scoring=scoring)
        clf.fit(data_x, data_y)
        params.update({'learning_rate': clf.best_params_["learning_rate"]})
        model_xg.learning_rate = clf.best_params_["learning_rate"]
        print(clf.best_params_)
        print("clf.best_score_", clf.best_score_)
        
        params_test1 = {"colsample_bytree": np.arange(0.3, 0.9, 0.1), 'subsample': np.arange(0.3, 0.9, 0.1)}
        clf = GridSearchCV(model_xg, params_test1, cv=kfold, n_jobs=-1, scoring=scoring)
        clf.fit(data_x, data_y)
        params.update({'colsample_bytree': clf.best_params_["colsample_bytree"]})
        params.update({'subsample': clf.best_params_["subsample"]})
        model_xg.colsample_bytree = clf.best_params_["colsample_bytree"]
        model_xg.subsample = clf.best_params_["subsample"]
        print(clf.best_params_)
        print("clf.best_score_", clf.best_score_)

        params_test1 = {"gamma": np.arange(0, 1.6, 0.1)}
        clf = GridSearchCV(model_xg, params_test1, cv=kfold, n_jobs=-1, scoring=scoring)
        clf.fit(data_x, data_y)
        params.update({'gamma': clf.best_params_["gamma"]})
        model_xg.gamma = clf.best_params_["gamma"]
        print(clf.best_params_)
        print("clf.best_score_", clf.best_score_)
        
       
        params_test1 = {"colsample_bylevel": np.arange(0.3, 0.7, 0.1), "colsample_bynode": np.arange(0.3, 0.7, 0.1)}
        clf = GridSearchCV(model_xg, params_test1, cv=kfold, n_jobs=-1, scoring=scoring)
        clf.fit(data_x, data_y)
        params.update({'colsample_bylevel': clf.best_params_["colsample_bylevel"]})
        params.update({'colsample_bynode': clf.best_params_["colsample_bynode"]})
        model_xg.colsample_bylevel = clf.best_params_["colsample_bylevel"]
        model_xg.colsample_bynode = clf.best_params_["colsample_bynode"]
        print(clf.best_params_)
        print("clf.best_score_", clf.best_score_)

        params_test1 = {'reg_lambda': np.arange(1, 1.6, 0.1), 'reg_alpha': np.arange(0, 1.6, 0.1)}
        clf = GridSearchCV(model_xg, params_test1, cv=kfold, n_jobs=-1, scoring=scoring)
        clf.fit(data_x, data_y)
        params.update({'reg_alpha': clf.best_params_["reg_alpha"]})
        params.update({'reg_lambda': clf.best_params_["reg_lambda"]})
        model_xg.reg_lambda = clf.best_params_["reg_lambda"]
        model_xg.reg_alpha = clf.best_params_["reg_alpha"]
        print(clf.best_params_)
        print("clf.best_score_", clf.best_score_)

        return model_xg, params


import pandas as pd
import xgboost as xgb
from xgboost.sklearn import XGBClassifier
from sklearn import metrics
from sklearn.preprocessing import Binarizer
from sklearn.metrics import matthews_corrcoef
from sklearn.metrics import confusion_matrix
scores_1=[]
scores_2=[]
scores_3=[]
scores_4=[]

data = pd.read_table("KIRP_methy.txt")
data.columns = [str(i) for i in range(data.shape[1])]
label = pd.read_table("KIRP_label.txt").values.reshape([-1, ])

kf = KFold(n_splits=10, shuffle=True, random_state=1)
y_valid_pred_total = np.zeros(data.shape[0])
score = []
print(data.shape, label.shape)
for train_ind, test_ind in kf.split(data, label):
    train_data = data.iloc[train_ind, :]
    train_y = label[train_ind]
    test_data = data.iloc[test_ind, :]
    test_y = label[test_ind]
    model = XGBClassifier()
    gv = GV()
    params = {}

    model, params = gv.xg_find_base('roc_auc', train_data, train_y, model, {})
   
    print(params)
    early_stop = 50
    verbose_eval = 20
    num_rounds = 500



    d_train = xgb.DMatrix(train_data, label=train_y)
    d_valid = xgb.DMatrix(test_data, label=test_y)

    watchlist = [(d_train, 'train')]

    
    params.update({'eval_metric': 'auc',
                   'objective': 'binary:logistic',
                  'seed':1})
    
    
    model = xgb.train(params, d_train, num_boost_round=num_rounds, early_stopping_rounds=early_stop, evals=watchlist)

    y_pre = model.predict(d_valid).reshape([-1,1])
    mms = Binarizer(0.5)
    y_pre_ = mms.fit_transform(y_pre)
    auc = metrics.roc_auc_score(test_y, y_pre) 
    acc = accuracy_score(test_y, y_pre_)
    
    precision, recall, _thresholds = metrics.precision_recall_curve(test_y, y_pre_)
    pr_auc = metrics.auc(recall, precision)
    mcc = matthews_corrcoef(test_y, y_pre_)
    
    tn, fp, fn, tp = confusion_matrix(test_y, y_pre_).ravel()
    total=tn+fp+fn+tp
    sen = float(tp)/float(tp+fn)
    sps = float(tn)/float((tn+fp))
    
    print ('AUC : %f' % auc)
    print ('ACC : %f' % acc) 
    print("PRAUC: %f" % pr_auc)
    print ('MCC : %f' % mcc)
    print ('SEN : %f' % sen)
    print ('SEP : %f' % sps)
    
    scores_1.append(auc)
    scores_2.append(acc)
    scores_3.append(pr_auc)
    scores_4.append(mcc)
    
print('auc-mean-score: %.3f' %np.mean(scores_1))
print('acc-mean-score: %.3f' %np.mean(scores_2))
print('pr-mean-score: %.3f' %np.mean(scores_3))
print('mcc-mean-score: %.3f' %np.mean(scores_4))

