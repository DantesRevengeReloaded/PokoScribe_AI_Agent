

'''
class parameters:
'''
#create the parameters class so they will be loaded to various models the following is incomplete
class AIParameters:
    def __init__(self):
        self.content=''
    
    def openainovel(self):
        with open('sources/testing/cont2.txt', 'r') as file:
            content = file.read()
        self.content = content
        return self.content
    
    def get_test_file(self):
        return self.test_file