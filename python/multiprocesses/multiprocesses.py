#!/usr/bin/env python
# -*- coding:utf-8 -*-

from multiprocessing import Process, Queue, managers
from multiprocessing.managers import SyncManager
import time
import signal
import os


def mgr_init():
    # ignore the interrupt of Ctrl-C
    signal.signal(signal.SIGINT, signal.SIG_IGN)

def put_data_proc(queue):

    pid = os.getpid()
    i = 0 
    dict = {'id':0}
    try:
        while True:
            dict['a'] = i
            dict['b'] = i
            dict['c'] = i
            print "Current value is: ", dict
            queue.put(dict)
            i = i + 1
            time.sleep(2)
    except KeyboardInterrupt:
        print "Subprocess put_data_proc (pid=%s) was interruptted. " % pid

def put_data_proc_1(queue):

    pid = os.getpid()
    i = 0 
    dict = {'id':1}
    try:
        while True:
            dict['a'] = i
            dict['b'] = i
            dict['c'] = i
            print "Current value is: ", dict
            queue.put(dict)
            i = i + 1
            time.sleep(4)
    except KeyboardInterrupt:
        print "Subprocess put_data_proc (pid=%s) was interruptted. " % pid


def get_data_proc(queue):
  
    pid = os.getpid()
    try:
        while True:
            output = queue.get()
            print "Output is ", output
    except KeyboardInterrupt:
        print "Subprocess get_data_proc (pid=%s) was interruptted. " % pid

def main_proc():

    pid = os.getpid()
    # initialize manager
    mgr = SyncManager()
    mgr.start(mgr_init)
    
    try:
        # Create share object between processes
        shared_queue = mgr.Queue()

        # Create subprocesses
        put_proc = Process(target=put_data_proc, args=(shared_queue,))
        put_proc_1 = Process(target=put_data_proc_1, args=(shared_queue,))
        get_proc = Process(target=get_data_proc, args=(shared_queue,))

        # Start the processes
        put_proc.start()
        put_proc_1.start()
        get_proc.start()

        # Join the processes until they finished
        put_proc.join()
        put_proc_1.join()
        get_proc.join()

    except KeyboardInterrupt:
        print "Main process (pid=%s) was interruptted" % pid
    finally:
        mgr.shutdown()


if __name__ == '__main__':

    main_proc()
