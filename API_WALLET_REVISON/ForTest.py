test = {'dict': 1, 'dictionary': 2}
my_new_dict = dict.fromkeys(key for key in test)
print(my_new_dict)