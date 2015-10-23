__author__ = 'Connor The Great'

import time

class simpleclass:
    def __init__(self):
        self.variable = '\033[92m' + "[*]: i belong to the class" + '\033[0m'

    def class_function(self):
        print(self.variable)

    @staticmethod
    def static_function():
        print('\033[92m' + "[*]: i don't need this class" + '\033[0m')

simpleclass.static_function()  # able to be called prior to class instantiation
time.sleep(.5)

try:
    simpleclass.class_function()  # attempts calling class function directly (it will fail)
except TypeError:  # the type of error that occured, you can create multiple excepts that handle different errors differently
    time.sleep(1)
    print('\033[91m' + '\n[X]: simpleclass.class_function() failed because no reference to self\n' + '\033[0m')
    time.sleep(1)
    print('\033[93m' + "[!]: instantiating class and trying again\n" + '\033[0m')
    time.sleep(1)
    x = simpleclass()  # instantiates class in memory assigning x as the reference to that instantiation of it
    x.class_function()  # calls the class_function from the in memory simple class object
except:  # this clause catches enything else that could happen, though nothing should cause this in this code
    print('\033[91m' + '\n[X]: some weird shit happened' + '\033[0m')
    exit(9001)
