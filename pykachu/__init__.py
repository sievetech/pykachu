# -*- coding: utf-8 -*-
from datetime import datetime
import redis
import time
import os


REDIS_HOST = os.environ.get("PYKACHU_REDIS_SERVER", "127.0.0.1")
REDIS_PORT = os.environ.get("PYKACHU_REDIS_PORT", 6379)
REDIS_DB = os.environ.get("PYKACHU_REDIS_DB", 0)


class JobState:
    WAITING = 'Waiting'
    RUNNING = 'Running'
    STOP = 'Stoped'
    ERROR = 'Error'
    FINISH = 'Finish'


class JobServer(object):
    def __init__(self, prefix="pykachu"):
        self.prefix = prefix + '_'
        if not hasattr(JobServer, 'pool'):
            JobServer.create_pool()
        self.connection = redis.Redis(connection_pool=JobServer.pool)
        self.expiration_after_complete = 60 * 60  # 1h

    @staticmethod
    def create_pool():
        JobServer.pool = redis.ConnectionPool(host=REDIS_HOST,
                               port=int(REDIS_PORT), db=int(REDIS_DB))

    def publish_job(self, job, job_dict):
        """
        :type job: Job
        :type job_dict: dict
        """
        self.connection.hmset(self.get_job_id(job), job_dict)

    def another_step_job(self, job, steps_second=0, data=None):
        """
        :type job: Job
        :type data: object
        """
        with self.connection.pipeline() as pipeline:
            if data:
                pipeline.hset(self.get_job_id(job), 'last_item', unicode(data))
            if job.status != "Running":
                job.status = "Running"
                pipeline.hset(self.get_job_id(job), 'state', job.status)

            pipeline.hset(self.get_job_id(job), 'steps_second', steps_second)
            pipeline.hincrby(self.get_job_id(job), 'steps')
            pipeline.execute()

    def error_job(self, job, data=None, error=None):
        """
        :type job: Job
        :param error: str
        """
        with self.connection.pipeline() as pipeline:

            if error:
                pipeline.hset(self.get_job_id(job), 'data', error)

            if data:
                pipeline.hset(self.get_job_id(job), 'last_item', unicode(data))

            pipeline.hset(self.get_job_id(job), 'state', JobState.ERROR)
            pipeline.expire(self.get_job_id(job), job.expiration or self.expiration_after_complete)
            pipeline.execute()

    def finish_job(self, job):
        """
        :type job: Job
        """
        with self.connection.pipeline() as pipeline:

            pipeline.hset(self.get_job_id(job), 'steps', job.total)
            pipeline.hset(self.get_job_id(job), 'state', JobState.FINISH)
            pipeline.expire(self.get_job_id(job), job.expiration or self.expiration_after_complete)
            pipeline.execute()

    def situation_job(self, job):
        return self.connection.hgetall(self.get_job_id(job))

    def get_job_id(self, job):
        """
        :type job: Job
        :return: str
        """
        return self.prefix + str(job.id)


class Job(object):
    def __init__(self, *args, **kwargs):
        self.id = kwargs.get('id')
        self.total = kwargs.get('total', 0)
        self.status = kwargs.get('status', JobState.WAITING)
        self.name = kwargs.get('name', 'Sem Nome')
        self.last_update = time.time()
        self.connection = None
        self.expiration = kwargs.get('expiration', 0)
        self.last_step = -1

    def publish(self, connection=None, **kwargs):
        """
        :type connection: JobServer
        """
        if not self.connection:
            self.connection = connection or JobServer()
        self.connection.publish_job(self, self.to_dict(kwargs))

    def to_dict(self, extra):
        return dict(
            id=self.id,
            state=JobState.WAITING,
            total=self.total,
            steps=0,
            name=self.name,
            start_at=datetime.now().strftime('%X %x'), **extra)

    def another_step(self, data=None):
        steps_second = 1 / (time.time() - self.last_update)
        self.last_update = time.time()
        if self.last_step < self.total:
            self.last_step += 1
            self.connection.another_step_job(self, steps_second, data)

    def finish(self):
        self.connection.finish_job(self)

    def error(self, error):
        self.connection.error_job(self, error)

    def situation(self):
        return self.connection.situation_job(self)


class JobDummy(Job):
    """
    Ideal para MOCK
    """
    def publish(self, connection=None, **kwargs):
        pass

    def another_step(self, data=None):
        pass

    def finish(self):
        pass

    def error(self, error):
        pass

    def situation(self):
        pass
