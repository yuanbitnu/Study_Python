import threading
import time

lis = []
lock = threading.RLock()
def add(item):
    current_thread = threading.current_thread()
    # lock.acquire() ## 方式一的加锁
    with lock:  ## 方式二
        print('线程**%s**开始执行'%current_thread.getName())
        lis.append(item)
        time.sleep(0.1)
        value = lis[-1]
        print(item,value,'---')
        print('线程**%s**执行结束'%current_thread.getName())
    # lock.release() ## 方式一的解锁

for i in range(1,11):
    thread = threading.Thread(target=add,args=(i,),name=str(i))
    thread.start()
