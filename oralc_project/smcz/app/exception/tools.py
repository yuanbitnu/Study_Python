import time
import datetime
from exception.myDict import MyDict

class ToolsHelp:
    @staticmethod
    def formateData(data:tuple,orclCloumnTitle:list):
        cloumnTitles = [item[0].lower() for item in orclCloumnTitle]
        formatedData = []
        for rowData in data:
            dictData = dict(zip(cloumnTitles,rowData))
            formatedData.append(dictData)
        return formatedData
    
    @staticmethod
    def formateUkeyIds(data:tuple,orclCloumnTitle:list):
        cloumnTitles = [item[0].lower() for item in orclCloumnTitle]
        lisData =[]
        dictData = {}
        for rowData in data:
            lisData.append(rowData[0])
        dictData = {cloumnTitles[0]:lisData}
        return dictData

    @staticmethod
    def getCurrentTime():
        timeStamp = int(time.time())
        timeArray = time.localtime(timeStamp)
        return time.strftime("%Y-%m-%d %H:%M:%S", timeArray)

    @staticmethod
    def dict_to_object(dictObj):
        if not isinstance(dictObj, dict):
            return dictObj
        inst=MyDict()
        for k,v in dictObj.items():
            inst[k] = ToolsHelp.dict_to_object(v)
        return inst

if __name__ == '__main__':
    res = ToolsHelp.getCurrentTime()
    print(res,type(res))