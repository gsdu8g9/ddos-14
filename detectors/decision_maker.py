#!/usr/bin/python
from storage import Storage
from sklearn.externals import joblib

#1.56
#100.57
class DecisionMaker():

    EMPTY_MALWARE_TABLE = (set([]), set([]))

    def __init__(self, config):

        self.storage = Storage(config)
        
        self.models = { 
            'd' : joblib.load('models_binary/100decisionTreeD.pkl'),
            's_d' : joblib.load('models_binary/100decisionTreeS_D.pkl'),
            'sp_d' : joblib.load('models_binary/100decisionTreeSP_D.pkl'),
            'sp_dp' : joblib.load('models_binary/100decisionTreeSP_DP.pkl'),
        }
        
        self.ip_list = set()

        with open('ip_list.txt') as f:
            self.ip_list = set(f.readlines())

        self.features = ['bcount', 'pcount']
        self.features_sp_dp = ['bcount', 'pcount', 'ucount']
        
        
    '''
    return tuple of adresses where predicted malware label
    df - current dataframe
    pred - predicted list
    '''
    def get_malware_tables(self, df, pred):

        if len(df) != len(pred):
            raise ValueError('Wrong length of dataframe or prediction!')

        table_src = set()
        table_dst = set()

        for i in xrange(len(pred)):
            if pred[i] != "BENIGN":
                #WARNING: 's' filter must contain "d"
                #if 'dst' in data.iloc[i]:
                table_dst.add(df.iloc[i].dst)
                table_src.add(df.iloc[i].src)

        return table_src , table_dst - self.ip_list


    def get_malware_tables_2(self, df, pred):

        if len(df) != len(pred):
            raise ValueError('Wrong length of dataframe or prediction!')

        df['pred'] = pred
        df_ = df[df.pred != 'BENIGN'][['dst', 'src']]
        
        return (set(df_.src), set(df_.dst))


    '''
    Make prediction by @data with filter @s and get src and dst addresses by @malware_tables
    '''
    def predict(self, data, s, malware_tables=None):
        
        df = self.storage.filter_data(data, nf_group_type=s, malware_tables=malware_tables)
        
        #print 'data len:', str(len(data))
        #print 'df len:', str(len(df))

        features = self.features[:]
        if s != "sp_dp":
            features.append('ucount')
        
        X = df[features]
        
        if X.shape[0] == 0 or X.shape[1] == 0:
            print "failed", s, "!!!!!!!"
            return self.EMPTY_MALWARE_TABLE

        #print "filtered, on prediction:", df[['dst', 'src']]

        pred = self.models[s].predict(df[features])
        #print pred

        a = self.get_malware_tables(df=df, pred=pred)

        #b = self.get_malware_tables_2(df=df, pred=pred)
        #print "\n_________________________________________________________________\n"
        #print a == b
        #print a
        #print b
        return a

    '''
    return list of addresses for judge
    '''
    def make(self, timestamp=None, depth=None):
        
        result = None
        
        # get data from DB by timestamp and depth
        data = self.storage.select(timestamp, depth)
        

        malware_tables_d = self.predict(data, "d")
        #print "d: ", malware_tables_d

        

        if malware_tables_d == self.EMPTY_MALWARE_TABLE:
            del data
            return result


        malware_tables_s_d = self.predict(data, "s_d", malware_tables_d)
        #print "s_d: ", malware_tables_s_d

        if malware_tables_s_d == self.EMPTY_MALWARE_TABLE:
            del data
            return result
        

        malware_tables_sp_d = self.predict(data, "sp_d", malware_tables_s_d)
        #print "sp_d: ", malware_tables_sp_d

        if malware_tables_sp_d == self.EMPTY_MALWARE_TABLE:
            del data
            return result
        
        
        malware_src, malware_dst = self.predict(data, "sp_dp", malware_tables_sp_d)
        #print "sp_dp: ", (malware_src, malware_dst)

        '''#!
        #s = 's_d'

        #df = self.storage.filter_data(data, s)
        #pred = self.models[s].predict(df[features])
        
        #src_list = sorted(self.storage.get_src_by_predict(df, pred))
        #if len(src_list) > 0:
        #    result = "', '".join(src_list)
        '''

        if len(malware_src) > 0:
            result = sorted(malware_src)
        
        del malware_tables_d
        del malware_tables_s_d
        del malware_tables_sp_d
        del data

        return result


    def end(self):

        self.storage.close()
