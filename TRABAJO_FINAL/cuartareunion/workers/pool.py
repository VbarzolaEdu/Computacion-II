from concurrent.futures import ProcessPoolExecutor

from workers.tasks import _init_worker


class WorkerPool:
    """
    Envuelve el ProcessPoolExecutor y le pasa la ruta de la DB a cada worker.

    Cada proceso worker abre su propia conexión SQLite en _init_worker().
    SQLite maneja la concurrencia internamente — no se necesita Lock externo.
    """

    def __init__(self, num_workers: int, db_path: str):
        self.num_workers = num_workers
        self.db_path = db_path
        self.executor: ProcessPoolExecutor | None = None

    def create(self):
        print(f"[pool] Iniciando pool con {self.num_workers} workers")
        self.executor = ProcessPoolExecutor(
            max_workers=self.num_workers,
            initializer=_init_worker,
            initargs=(self.db_path,),
        )
        print("[pool] Pool listo")

    def shutdown(self):
        if self.executor:
            self.executor.shutdown(wait=True)
            print("[pool] Pool detenido")
