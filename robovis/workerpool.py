from multiprocessing.pool import Pool
from multiprocessing.queues import SimpleQueue
from multiprocessing.pool import worker
import os
from queue import PriorityQueue

class JobRef(object):
    def __init__(self, func, args, ref=None):
        self.func = func
        self.args = args
        self.ref = ref
        self._res = None
        self._started = False

    def jobStarted(self, res):
        self._res = res
        self._started = True

    def ready(self):
        if self._res == None:
            return False
        else:
            return self._res.ready()

    def started(self):
        return self._started

    def get(self):
        if self._res == None:
            raise Exception('Not ready')
        else:
            return self._res.get()

class RVWorkerPool(object):
    def __init__(self, processes=None):
        self.pool = Pool(processes)
        self.pipe_target = os.cpu_count()
        self.in_pipe = 0
        self.jobs = []

    def registerJob(self, func, args):
        job = JobRef(func, args)
        self.jobs.append(job)
        if self.in_pipe < self.pipe_target:
            job.jobStarted(self.pool.apply_async(func, args))
            self.in_pipe += 1
        return job

    def poll(self):
        done = []
        for job in self.jobs:
            if job.started():
                # Check if it's finished
                if job.ready():
                    done.append(job)
                    self.in_pipe -= 1
            else:
                if self.in_pipe < self.pipe_target:
                    job.jobStarted(self.pool.apply_async(job.func, job.args))
                    self.in_pipe += 1
        for job in done:
            self.jobs.remove(job)

    def terminate(self):
        self.pool.terminate()
