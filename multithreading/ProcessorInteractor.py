import queue
import traceback
from threading import Thread


# TODO rename + testing
# TODO check if everything works


class Job:
    def __init__(self, function, arguments=None, keywords=None, is_async=True, callback=None):
        if arguments is None:
            arguments = []
        if keywords is None:
            keywords = {}

        self.function = function
        self.arguments = arguments
        self.keywords = keywords
        self.is_async = is_async
        self.callback = callback
        self.result = queue.Queue()

    def __str__(self):
        variables = vars(self)
        variables['arguments'] = [str(entry) for entry in variables['arguments']]
        return str({key: str(value) for key, value in variables.items()})


class Processor:
    class __JobException(Exception):
        def __init__(self, message):
            super().__init__(message)

    class __CallbackException(Exception):
        def __init__(self, message):
            super().__init__(message)

    def __init__(self, num_workers=4, daemon=True):
        self.job_queue = queue.Queue()
        self.stop = False
        self.join = False
        self.workers = [Thread(target=self.__process_jobs_queue, args=[i],
                               name='Worker {}'.format(i), daemon=daemon) for i in range(num_workers)]

        for worker in self.workers:
            worker.start()

    def submit_job(self, job: Job):
        self.job_queue.put(job, block=True, timeout=None)

        if not job.is_async:
            success = job.result.get()
            result = job.result.get() if success else None
            return success, result

    def __process_jobs_queue(self, worker_id):
        while not self.stop or (self.join and self.job_queue.qsize() == 0):
            # print('worker {}: waiting for job '.format(worker_id))
            job = self.job_queue.get()
            print('worker {}: got a new job. Jobs left in queue: {} '.format(worker_id, self.job_queue.qsize()))

            try:
                result = job.function(*job.arguments, **job.keywords)
                job.result.put(True)
                job.result.put(result)

                self.call_callback(job, worker_id)
            except self.__CallbackException:
                pass
            except Exception as e:
                job.result.put(False)
                self.call_callback(job, worker_id)
                self.raise_job_exception_caused_by(job, e, worker_id)

            # print('worker {}: Job done'.format(worker_id))
            self.job_queue.task_done()

    def call_callback(self, job, worker_id):
        try:
            if job.callback is not None:
                job.callback(job)
        except Exception as e:
            self.raise_callback_exception_caused_by(job, e, worker_id)

    def raise_callback_exception_caused_by(self, job, cause, worker_id):
        try:
            raise self.__CallbackException(
                'Callback Exception in Worker {} for Job {}'.format(worker_id, str(job))) from cause
        except self.__CallbackException:
            traceback.print_exc()

    def raise_job_exception_caused_by(self, job, cause, worker_id):
        try:
            raise self.__JobException('Exception in Worker {} for job {}'.format(worker_id, str(job))) from cause
        except self.__JobException:
            traceback.print_exc()

    def stop(self, wait_for_workers=True):
        self.stop = True

        if not wait_for_workers:
            return

        for worker in self.workers:
            worker.join()

    def join(self):
        self.join = True

        for worker in self.workers:
            if worker.is_alive():
                worker.join()

        self.stop = True

    def wait_for_all_jobs(self):
        self.job_queue.join()

    def __del__(self):
        self.stop = True
