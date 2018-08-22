import logging
import os
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import Session


class Runner(object):
    def __init__(self, connection_str, logger=None):
        self._connection_str = connection_str
        self._logger = logger or logging.getLogger(__name__)
        self.__jobs = []

    def engine(self, echo=False):
        """ Create a fresh new session... """
        return create_engine(self._connection_str, echo=echo)

    def connection(self, echo=False):
        return self.engine(echo=echo).connect()

    def _session(self, echo=False):
        return Session(bind=self.connection(echo=echo))

    @contextmanager
    def session(self, echo=False):
        """Provide a transactional scope around a series of operations."""
        try:
            s = self._session(echo=echo)
            yield s
            s.commit()
        except Exception as e:
            s.rollback()
            raise e
        finally:
            s.close()

    def _run_jobs(self):
        self._logger.debug("PID main {pid}".format(pid=os.getpid()))

        for job in self.jobs:
            # all jobs get the trigge
            self._logger.info("Job {j}".format(j=job.name))
            job.start()

        for job in self.jobs:
            self._logger.info("Wait for job {j}".format(j=job.name))
            job.join()
            self._logger.info("Job {j} done".format(j=job.name))

    @property
    def jobs(self):
        return self.__jobs



