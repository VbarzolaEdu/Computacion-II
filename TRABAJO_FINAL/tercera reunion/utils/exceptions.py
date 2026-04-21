"""
Excepciones personalizadas del proyecto.
"""


class AppError(Exception):
    """Excepción base del proyecto"""
    pass


class ValidationError(AppError):
    """Error de validación de datos"""
    pass


class DatabaseError(AppError):
    """Error en operaciones de BD"""
    pass


class WorkerError(AppError):
    """Error en ejecución de worker"""
    pass


class TimeoutError(AppError):
    """Timeout en operación"""
    pass
