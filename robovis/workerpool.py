from multiprocessing.pool import Pool
from multiprocessing.queues import SimpleQueue
from multiprocessing.pool import worker
import os
from queue import PriorityQueue

class JobRef(object):
    def __init__(self, func, args, ref=None, priority=1):
        self.func = func
        self.args = args
        self.ref = ref
        self.priority= priority
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

    def registerJob(self, func, args, ref=None, priority=1):
        job = JobRef(func, args, ref, priority)
        # Replace duplicate-source unstarted jobs
        if ref is not None:
            self.jobs = [j for j in self.jobs if j.ref != ref or j.started()]
        self.jobs.append(job)
        if self.in_pipe < self.pipe_target:
            job.jobStarted(self.pool.apply_async(func, args))
            self.in_pipe += 1
        return job

    def poll(self):
        done = []
        sorted_jobs = sorted(self.jobs, key=lambda j: j.priority)
        for job in sorted_jobs:
            if job.started():
                # Check if it's finished
                if job.ready():
                    self.jobs.remove(job)
                    self.in_pipe -= 1
            else:
                if self.in_pipe < self.pipe_target:
                    job.jobStarted(self.pool.apply_async(job.func, job.args))
                    self.in_pipe += 1

    def terminate(self):
        self.pool.terminate()
