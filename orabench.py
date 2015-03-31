# coding=utf-8
import os
import time
import cx_Oracle
from multiprocessing import Pool
from ConfigParser import ConfigParser
import random
from datetime import datetime


def init(config):
    conn = cx_Oracle.connect(config.db)
    cursor = conn.cursor()
    ddl1 = ''' drop table orders'''
    ddl2 = '''
    create table orders
       (
         order_id     number(12) ,
         order_date   date,
         order_mode   varchar2(8),
         customer_id  number(6),
         order_status number(2),
         order_total  number(8,2),
         sales_rep_id number(6),
         promotion_id number(6),
         constraint pk_order_id primary key (order_id)
       ) '''
    try:
        cursor.execute(ddl1)
    except cx_Oracle.DatabaseErro as oerr:
        print oerr
    finally:
        cursor.execute(ddl2)

def benchmark(config):
    # 打印进程号：
    print 'Process (%s) start...' % os.getpid()

    # 连接数据库:
    conn = cx_Oracle.connect(config.db)
    cursor = conn.cursor()
    ins = 'insert into orders VALUES (:order_id,:order_date,:order_mode,:customer_id,:order_status,:order_total,:sales_rep_id,:promotion_id)'

    # 记录启动时间:
    start = time.time()

    for i in xrange(1, config.requests + 1):
        # 生成一条随机记录
        rec = {
            'order_id': str(os.getpid()) + str(i),
            'order_date': datetime.now(),
            'order_mode': random.choice(["direct", "online"]),
            'customer_id': random.randint(100, 250),
            'order_status': random.randint(1, 11),
            'order_total': random.uniform(6, 2),
            'sales_rep_id': random.randint(100, 207),
            'promotion_id': random.randint(33, 534)
        }
        cursor.execute(ins, rec)
        conn.commit()
        # 思考时间0.01秒
        time.sleep(config.think_time)

    # 记录完成时间:
    end = time.time()
    conn.close()

    # print worker process end message
    print 'Process %s process %s requests during %02f seconds' % (os.getpid(), config.requests, (end - start))
    return end - start


class Orabench(object):
    def __init__(self, filename):
        # read config from file
        config = ConfigParser()
        config.read(filename)
        self.db = config.get('config', 'db')
        self.concurrency = config.getint('config', 'concurrency')
        self.requests = config.getint('config', 'requests')
        self.think_time = config.getfloat('config', 'think_time')
        self.init = config.get('config', 'init')

        print time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        print 'Connect to %s , Concurrency: %s , Requests: %d ,Think Time: %0.4f second' % (
            self.db, self.concurrency, self.requests, self.think_time)

        # 判断是否需要初始化表:
        if self.init == 'y':
            print 'Initializing table '
            init(self)
            print 'Initialized table '

    def run(self):
        try:
            # start a process pool
            pool = Pool(processes=self.concurrency)
            print 'concurrency: %s processes.' % self.concurrency
            result = pool.map_async(
                benchmark, [self] * self.concurrency)
            l = result.get()
            pool.close()
            pool.join()

            # 平均每个进程执行时间:
            avg_run = sum(l) / self.concurrency

            # 平均执行时间/平均执行次数 = 平均每次响应  ， 总执行次数/总执行时间(约等等与平均运行时间）
            print "Results: Average_Response_Time =%.4f second , Average_TPS= %.2f " % (
                avg_run / self.requests, (self.concurrency * self.requests) / avg_run )
        finally:
           print time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
           exit()

if __name__ == "__main__":
    orabench = Orabench('orabench.cfg')
    orabench.run()

