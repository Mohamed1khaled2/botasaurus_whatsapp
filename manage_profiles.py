from botasaurus.profiles import Profiles


def search_about_profiles(number:str) -> Profiles:
    profile = Profiles.get_profile(number)
    
    
    print(type(profile))
    
    

# Profiles.set_profile('201289422813', {'name': '201289422813', 'type_number': "orange"})
# Profiles.set_profile('201103738707', {'name': '201103738707', 'type_number': "etisalat"})
Profiles.set_profile("201552694323", {'name': "201552694323", 'type_number':"we"})
# # Get a profile
# profile = Profiles.get_profile('201289422813')
# print(profile)  # Output: {'name': 'Amit Sharma', 'age': 30}

# # Get all profiles
# all_profiles = Profiles.get_profiles()
# print(all_profiles)  # Output: [{'name': 'Amit Sharma', 'age': 30}, {'name': 'Rahul Verma', 'age': 30}]


# search_about_profiles("201289422813")


# Delete a profile
# Profiles.delete_profile('amit')