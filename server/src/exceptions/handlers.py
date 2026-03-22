from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class NotFoundError(Exception):
    def __init__(self, detail: str):
        self.detail = detail


class ConflictError(Exception):
    def __init__(self, detail: str):
        self.detail = detail


class BusinessLogicError(Exception):
    def __init__(self, detail: str):
        self.detail = detail


class UnauthorizedError(Exception):
    def __init__(self, detail: str):
        self.detail = detail


class ForbiddenError(Exception):
    def __init__(self, detail: str):
        self.detail = detail

class TokenExpiredError(UnauthorizedError):
    pass


class TokenInvalidError(UnauthorizedError):
    pass



def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(NotFoundError)
    async def not_found_handler(request: Request, exc: NotFoundError):
        return JSONResponse(status_code=404, content={"detail": exc.detail})

    @app.exception_handler(ConflictError)
    async def conflict_handler(request: Request, exc: ConflictError):
        return JSONResponse(status_code=409, content={"detail": exc.detail})

    @app.exception_handler(BusinessLogicError)
    async def business_logic_handler(request: Request, exc: BusinessLogicError):
        return JSONResponse(status_code=422, content={"detail": exc.detail})

    @app.exception_handler(UnauthorizedError)
    async def unauthorized_handler(request: Request, exc: UnauthorizedError):
        return JSONResponse(status_code=401, content={"detail": exc.detail})

    @app.exception_handler(ForbiddenError)
    async def forbidden_handler(request: Request, exc: ForbiddenError):
        return JSONResponse(status_code=403, content={"detail": exc.detail})
