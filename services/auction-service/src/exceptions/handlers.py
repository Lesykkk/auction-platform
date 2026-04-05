from datetime import datetime, timezone
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError, ResponseValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException


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


class ServiceUnavailableError(Exception):
    def __init__(self, detail: str):
        self.detail = detail


class TokenExpiredError(UnauthorizedError):
    pass


class TokenInvalidError(UnauthorizedError):
    pass


def create_error_response(request: Request, status_code: int, message: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": status_code,
            "message": message,
            "path": request.url.path,
        },
    )


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(NotFoundError)
    async def not_found_handler(request: Request, exc: NotFoundError):
        return create_error_response(request, 404, exc.detail)

    @app.exception_handler(ConflictError)
    async def conflict_handler(request: Request, exc: ConflictError):
        return create_error_response(request, 409, exc.detail)

    @app.exception_handler(BusinessLogicError)
    async def business_logic_handler(request: Request, exc: BusinessLogicError):
        return create_error_response(request, 400, exc.detail)

    @app.exception_handler(UnauthorizedError)
    async def unauthorized_handler(request: Request, exc: UnauthorizedError):
        return create_error_response(request, 401, exc.detail)

    @app.exception_handler(ForbiddenError)
    async def forbidden_handler(request: Request, exc: ForbiddenError):
        return create_error_response(request, 403, exc.detail)

    @app.exception_handler(ServiceUnavailableError)
    async def service_unavailable_handler(request: Request, exc: ServiceUnavailableError):
        return create_error_response(request, 503, exc.detail)

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        errors = [
            {
                "field": ".".join(str(loc) for loc in err["loc"]),
                "message": err["msg"],
            }
            for err in exc.errors()
        ]
        return JSONResponse(
            status_code=422,
            content={
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "status": 422,
                "message": "Validation error",
                "errors": errors,
                "path": request.url.path,
            },
        )

    @app.exception_handler(ResponseValidationError)
    async def response_validation_handler(request: Request, exc: ResponseValidationError):
        return create_error_response(request, 500, "Internal server error")

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        return create_error_response(request, exc.status_code, exc.detail)

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        return create_error_response(request, 500, "Internal server error")
