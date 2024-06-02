

'''
class parameters:
'''
#create the parameters class so they will be loaded to various models the following is incomplete
class parameters:
    def __init__(self):
        self.data_dir = 'data/'
        self.train_data = 'train.csv'
        self.test_data = 'test.csv'
        self.train_file = self.data_dir + self.train_data
        self.test_file = self.data_dir + self.test_data
        self.model_dir = 'model/'
    
    def get_train_file(self):
        return self.train_file
    
    def get_test_file(self):
        return self.test_file