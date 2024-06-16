

'''
class parameters:
'''
#create the parameters class so they will be loaded to various models the following is incomplete
class AIParameters:
    def __init__(self):
        self.content=''
    
    def openainovel(self):
        with open('/mnt/cf36a2d7-ecf4-46c7-a76a-5defe1ad7659/my_ai/sources/projectacademus/content_par.txt', 'r') as file:
            content = file.read()
        self.content = content
        return self.content
    
    def get_test_file(self):
        return self.test_file
    
    def data_analysis(self):
        with open('/mnt/cf36a2d7-ecf4-46c7-a76a-5defe1ad7659/my_ai/gpt-openai_templ.py/data_analysis_params.txt', 'r') as file:
            content = file.read()
        self.content = content
        return self.content