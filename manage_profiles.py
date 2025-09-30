from botasaurus.profiles import Profiles


def search_about_profiles(number:str) -> Profiles:
    profile = Profiles.get_profile(number)
    
    
    print(type(profile))
    
    

# Profiles.set_profile('201289422813', {'name': '201289422813', 'type_number': "orange"})
# Profiles.set_profile('201103738707', {'name': '201103738707', 'type_number': "etisalat"})
# Profiles.set_profile("201068105917", {'name': "201068105917", 'type_number':"vodaphone"})
# Profiles.set_profile("201505177473", {'name': "201505177473", 'type_number':"we"}) #! Take ban 18/9/2025
# Profiles.set_profile("201505774702", {'name': "201505774702", 'type_number':"we"})
# Profiles.set_profile("201289427756", {'name': "201289427756", 'type_number':"orange"})
# Profiles.set_profile("201552694323", {'name': "201552694323", 'type_number':"we"})
# Profiles.set_profile("201010723014", {'name': "201010723014", 'type_number':"vodaphone"})
# Profiles.set_profile("201001766549", {'name': "201001766549", 'type_number':"vodaphone"})


# Profiles.set_profile("201206226048", {'name': "201206226048", 'type_number':"orange"})
# Profiles.set_profile("201205217358", {'name': "201205217358", 'type_number':"orange"})
# Profiles.set_profile("201280578648", {'name': "201280578648", 'type_number':"orange"})
# Profiles.set_profile("201278846164", {'name': "201278846164", 'type_number':"orange"})
# Profiles.set_profile("201289422415", {'name': "201289422415", 'type_number':"orange"})
# Profiles.set_profile("201289427756", {'name': "201289427756", 'type_number':"orange"})
# Profiles.set_profile("201280576245", {'name': "201280576245", 'type_number':"orange"})
# Profiles.set_profile("201221775260", {'name': "201221775260", 'type_number':"orange"})
# Profiles.set_profile("201507747891", {'name': "201507747891", 'type_number':"we"})
# Profiles.set_profile("201505377476", {'name': "201505377476", 'type_number':"we"})
# Profiles.set_profile("201550787747", {'name': "201550787747", 'type_number':"we"})
# Profiles.set_profile("201552436501", {'name': "201552436501", 'type_number':"we"})
# Profiles.set_profile("201505107747", {'name': "201505107747", 'type_number':"we"})
Profiles.set_profile("201552436501", {'name': "201552436501", 'type_number':"we"})
Profiles.set_profile("201208751824", {'name': "201208751824", 'type_number':"orange"})
Profiles.set_profile("201289427787", {'name': "201289427787", 'type_number':"orange"})


# # Get a profile
# profile = Profiles.get_profile('201289422813')
# print(profile)  # Output: {'name': 'Amit Sharma', 'age': 30}

# # Get all profiles
# all_profiles = Profiles.get_profiles()
# print(all_profiles)  # Output: [{'name': 'Amit Sharma', 'age': 30}, {'name': 'Rahul Verma', 'age': 30}]


# search_about_profiles("201289422813")


# Delete a profile
# Profiles.delete_profile('amit')