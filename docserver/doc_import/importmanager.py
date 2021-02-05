import concurrent.futures
import time
import queue
from enum import Enum, auto
from random import randint


from docserver.model.project import Project


class ImportStatus(Enum):
    NOT_IMPORTED = auto()
    IMPORTING = auto()
    IMPORTED = auto()


def process_project(name: str, import_queue: queue.Queue[Project]):
    while True:
        project = import_queue.get()
        sleep = randint(1, 10)
        print(f"{name} {project.name} Start {sleep}")
        time.sleep(sleep)
        print(f"{name} {project.name} Done {sleep}")


class ImportManager:

    def __init__(self):
        self.import_queue: queue.Queue[Project] = queue.Queue()
        executor = concurrent.futures.ThreadPoolExecutor(3)
        for i in range(3):
            task = executor.submit(process_project, f"Worker{i}", self.import_queue)
            task.add_done_callback()

    def queue_import(self, project: Project) -> None:
        self.import_queue.put(project)
