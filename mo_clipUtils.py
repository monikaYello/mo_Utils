

import pymel.core as pm

class Character():
    def __init__(self):
        self.name = 'character1'
        self.members = []


    def __init__(self, name, addObj=None):
        self.name = name

    def create(self, name, t=1, r=1, s=0, addObj=None):
        self.name = name
        self.objList = addObj
        char = pm.character(name=name, excludeVisibility=1, excludeRotate=abs(r-1), excludeTranslate=abs(t-1), excludeScale=abs(s-1))
        if addObj is not None:
            pm.character(char, add=addObj)
            self.members.append(addObj)
        return char

    def add(self, addObj=None):
        if addObj is not None:
            pm.character(self.name, add=addObj)
            self.members.append(addObj)
        return self.name


    def getMembers(self):
        ''' Query the members of the character'''
        return pm.character(self.name, query=True)

class Clip():

    def __init__(self):
        self.name = 'clip1'
        self.members = []


    def create(self, name, character):
        self.name = name
        c = pm.clip(character, startTime=0, endTime=20, name=name)
        return c

    def add(self, addObj=None):
        if addObj is not None:
            pm.character(self.name, add=addObj)
            self.members.append(addObj)
        return self.name


    def getMembers(self):
        ''' Query the members of the character'''
        return pm.character(self.name, query=True)