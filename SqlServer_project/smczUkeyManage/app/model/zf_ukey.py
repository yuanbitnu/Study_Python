import os
import sys
import time
import datetime
project_path = os.path.dirname(os.path.dirname(__file__))
sys.path.append(project_path)
# print(sys.path)
# print(os.path.dirname(__file__))
# print(sys.modules)
from model import pool
from model import logging
from model import oracle
from exception.statuCode import StatuCode
from exception.tools import ToolsHelp

# 获取所有ukey的Id,按ID的值排序
def getUkeyIdLis():
    comStr = 'select ukey_id from zf_ukey order by ukey_id' # 查询字符串 select ukey_id from zf_ukey order by ukey_id
    try:
        connection = pool.acquire() # 对oracle连接对象池中获取连接
        cursor = connection.cursor() # 获取游标
        cursor.execute(comStr) # 执行SQL语句
        content = cursor.fetchall() # 获取行数据,返回一个元组类型的list列表
        cloumns = cursor.description # 获取当前表查询的列名
        return ToolsHelp.formateUkeyIds(content,cloumns) # 调用formateUkeyIds()工具方法格式化数据
    except oracle.DatabaseError as msg:
        logging.info(msg)
        return StatuCode.selectTabelError.value
    except Exception as e:
        logging.info(e)
        return StatuCode.unknowError.value
    finally:
        cursor.close() # 关闭游标
        pool.release(connection) # 释放连接对象回连接池

def getHasRoleIdLis(companyId:int):
    comStr = 'select role_id from zf_ukey where ownercompanynum = :companyId' # 查询字符串 select ukey_id from zf_ukey order by ukey_id
    try:
        connection = pool.acquire() # 对oracle连接对象池中获取连接
        cursor = connection.cursor() # 获取游标
        cursor.execute(comStr,(companyId,)) # 执行SQL语句
        content = cursor.fetchall() # 获取行数据,返回一个元组类型的list列表
        cloumns = cursor.description # 获取当前表查询的列名
        return ToolsHelp.formateUkeyIds(content,cloumns) # 调用formateUkeyIds()工具方法格式化数据
    except oracle.DatabaseError as msg:
        logging.info(msg)
        return StatuCode.selectTabelError.value
    except Exception as e:
        logging.info(e)
        return StatuCode.unknowError.value
    finally:
        cursor.close() # 关闭游标
        pool.release(connection) # 释放连接对象回连接池

def getUkeys():
    comStr = 'select * from zf_ukey' # 查询字符串
    try:
        connection = pool.acquire() # 对oracle连接对象池中获取连接
        cursor = connection.cursor() # 获取游标
        cursor.execute(comStr) # 执行SQL语句
        content = cursor.fetchall() # 获取行数据,返回一个元组类型的list列表
        cloumns = cursor.description # 获取当前表查询的列名
        return ToolsHelp.formateData(content,cloumns) # 调用formateData()工具方法格式化数据
    except oracle.DatabaseError as msg:
        logging.info(msg)
        return StatuCode.selectTabelError.value
    except Exception as e:
        logging.info(e)
        return StatuCode.unknowError.value
    finally:
        cursor.close() # 关闭游标
        pool.release(connection) # 释放连接对象回连接池

# 获取某个单位的ukey列表
def getUkeysBycompanyId(companyId:int = None): # 正在使用的Ukey
    if companyId != None:
        comStr = 'select u.ukey_id,u.ownername,u.ownermobile,u.ownercarnum,u.usetime,u.unusetime,u.isuse,u.isdestroy,r.r_name,c.compname from zf_companys c,zf_role r, zf_ukey u where u.ownercompanynum = :companyId and u.ownercompanynum = c.compid and u.role_id = r.r_id and u.isuse = 1 and u.isdestroy =0 order by u.ukey_id'
        paramers = {'companyId':companyId}
    else:
        comStr = 'select u.ukey_id,u.ownername,u.ownermobile,u.ownercarnum,u.usetime,u.unusetime,u.isuse,u.isdestroy,r.r_name,c.compname from zf_companys c,zf_role r, zf_ukey u where u.ownercompanynum = c.compid and u.role_id = r.r_id and u.isuse = 1 and u.isdestroy =0 order by u.ukey_id' # 查询字符串
        paramers = {}
    try:
        connection = pool.acquire() # 对oracle连接对象池中获取连接
        cursor = connection.cursor() # 获取游标
        cursor.execute(comStr,paramers) # 执行SQL语句
        content = cursor.fetchall() # 获取行数据,返回一个元组类型的list列表
        cloumns = cursor.description # 获取当前表查询的列名
        return ToolsHelp.formateData(content,cloumns) # 调用formateData()工具方法格式化数据
    except oracle.DatabaseError as msg:
        logging.info(msg)
        return StatuCode.selectTabelError.value
    except Exception as e:
        logging.info(e)
        return StatuCode.unknowError.value
    finally:
        cursor.close() # 关闭游标
        pool.release(connection) # 释放连接对象回连接池

# 注册ukey并写入记录
def insertUkey(ukeyObj):
    # Ukey插入sql语句
    insertUkeyComStr = 'insert into zf_Ukey u (u.ukey_id,u.ownername,u.ownermobile,u.ownercarnum,u.ownercompanynum,u.role_id,u.usetime,u.isuse) values (:ukeyID,:ownName,:ownMobile,:ownCarNum,:ownCompanyNum,:roleId,:useTime,:isUse)' 
    # 参数化
    ukeyParamers = {'ukeyID':ukeyObj.ukeyId,'ownName':ukeyObj.name,'ownMobile':ukeyObj.mobile,'ownCarNum':ukeyObj.carNum,'ownCompanyNum':ukeyObj.companyId,'roleId':ukeyObj.roleId,'useTime':ukeyObj.useTime,'isUse':ukeyObj.isUse}
    # 添加记录语句
    inertUkeyRcordComStr= 'insert into zf_ukey_record r (r.ur_company_num,r.ur_role_num,r.ur_ukey_num,r.ur_action_num,r.ur_proposer,r.ur_application_content,r.ur_create_time) values (:companyId,:roleId,:ukeyId,:actionId,:proposer,:appContent,:creatTime)'
    # 参数化
    recordParamers = {'companyId':ukeyObj.companyId,'roleId':ukeyObj.roleId,'ukeyId':ukeyObj.ukeyId,'actionId':ukeyObj.actionId,'proposer':ukeyObj.name,'appContent':ukeyObj.appContent,'creatTime':ukeyObj.useTime}
    try:
        connection = pool.acquire()
        cursor = connection.cursor()
        connection.begin() # 事务开始
        cursor.execute(insertUkeyComStr,ukeyParamers) # 执行uekey插入语句
        cursor.execute(inertUkeyRcordComStr,recordParamers) # 执行添加注册Ukey记录语句
        return StatuCode.successCode.value
    except oracle.DatabaseError as msg:
        logging.info(msg)
        connection.rollback() # 报错回滚
        return StatuCode.insertDataError.value
    except Exception as e:
        logging.info(e)
        connection.rollback() # 报错回滚
        return StatuCode.unknowError.value
    finally:
        connection.commit() # 通过连接对象提交
        cursor.close() # 关闭游标
        pool.release(connection) # 释放连接对象回连接池

def delUkey(id:int): 
    comStr = 'delete from zf_ukey where ukey_id = :id'
    paramers = (id,)
    try:
        connection = pool.acquire()
        cursor = connection.cursor()
        cursor.execute(comStr,paramers) # 带参数的执行语句
        connection.commit() # 通过连接对象提交
        return StatuCode.successCode.value
    except oracle.DatabaseError as msg:
        logging.info(msg)
        return StatuCode.deleteDataError.value
    except Exception as e:
        logging.info(e)
        return StatuCode.unknowError.value
    finally:
        cursor.close() # 关闭游标
        pool.release(connection) # 释放连接对象回连接池
    
def updateUkey(id:int,phoneNum:str=None,companyId:int=None,roleId:int=None,useTime:str=None,unuseTime:str=None,isuse:int = None,isdestroy:int = None):
    comStr = '' # 更新语句
    paramers = None
    if phoneNum != None:
        comStr = 'update zf_ukey set ownermobile = :phoneNum where ukey_id = :id'
        paramers = {'phoneNum':phoneNum,'id':id}
    elif companyId != None and roleId != None:
        comStr = 'update zf_ukey set ownercompanynum = :companyId,role_id = :roleId where ukey_id = :id'
        paramers = {'companyId':companyId,'roleId':roleId,'id':id}
    elif useTime != None and isuse!= None:
        comStr = "update zf_ukey set usetime = :useTime,isuse= :isuse where ukey_id = :id"
        paramers = {'usetime':useTime,'isuse':isuse,'id':id}
    elif unuseTime != None and isdestroy != None:
        comStr = "update zf_ukey set unusetime = :unuseTime,isdestroy= :isdestroy where ukey_id = :id"
        paramers = {'unusetime':unuseTime,'isdestroy':isdestroy,'id':id}
    else:
        logging.info('zf_ukey update comStr is error')
    try:
        connection = pool.acquire()
        cursor = connection.cursor()
        cursor.execute(comStr,paramers) # 参数为dict的执行语句,通过key匹配值
        connection.commit() # 通过连接对象提交
        return StatuCode.successCode.value
    except oracle.DatabaseError as msg:
        logging.info(msg)
        return StatuCode.insertDataError.value
    except Exception as e:
        logging.info(e)
        return StatuCode.unknowError.value
    finally:
        cursor.close() # 关闭游标
        pool.release(connection) # 释放连接对象回连接池


if __name__ == "__main__":
    useTime = ToolsHelp.getCurrentTime()
    # ret = updateUkey(4002,useTime=useTime,isuse=1)
    # ret = insertUkey(4006,'王五','1412584485','43458598883353656',304,3,useTime=useTime,isUse=1)
    # ret = getUkeyIdLis()
    ret = getHasRoleIdLis(100)
    # ret =delUkey(4008)
    # res = getUkeys()
    # res = getUkeysBycompanyId(100)
    print(ret)