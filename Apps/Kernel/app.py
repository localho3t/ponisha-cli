from Apps.Kernel.utils import Utils
import os
from Apps.WebApp.app import flask_app
class AppKernel:

    def __init__(self,mefile,profilefile):
        self.me_file = mefile
        self.profile_file = profilefile
        self.utils = Utils()
    
    def start(self):
        self.__file_settings()
        flask_app(self.profile_clean,self.me_clean)
        


    def __file_settings(self):
        self.me_clean =  self.utils.extract_users_from_file(self.me_file)
        self.profile_clean = self.utils.extract_from_profile_file(self.profile_file)
        self.__delete_file(self.me_file)
        self.__delete_file(self.profile_file)
        
    def get_me_data(self):
        return self.me_clean
    

    def __delete_file(self,file):
        master_path = "./sessions/"
        os.remove(f"{master_path}{file}")