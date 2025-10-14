from botasaurus.profiles import Profiles
import json
import os 
import sys
import shutil

class ManageFiles:
    def __init__(self):
        
        
        if getattr(sys, 'frozen', False):
            base_path = os.path.dirname(sys.executable)
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))

        self.profile_path = os.path.join(base_path, "profiles")

        # تأكد إن المجلد موجود
        os.makedirs(os.path.dirname(self.profile_path), exist_ok=True)

        print(self.profile_path)

    def search_about_profiles(self, number:str) -> Profiles:
        profile = Profiles.get_profile(number)

        return profile
    

    def get_profiles(self):
        # Get all profiles
        self.all_profiles = Profiles.get_profiles()
        return json.dumps(self.all_profiles, indent=4)
        
    def add_profile(self, number:str):
            
        if self.search_about_profiles(number) != None:
            
            info_cards = {
                    'vodafone':"2010", 
                    "etisalat":"2011",
                    "orange":"2012", 
                    "we":"2015"}              
            for k, v in info_cards.items():
                if v == number[0:4]:
                    Profiles.set_profile(number, {'name':number, 'type_number':k})
        else:
            return ("Profile Created")
        
    def del_profile(self, numbers:list[str]):
        try:
            for number in numbers :
                path_number_file = os.path.join(self.profile_path, str(number))
                if os.path.exists(path_number_file):
                    shutil.rmtree(path_number_file)
                Profiles.delete_profile(number)
        except:
            pass
