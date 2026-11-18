from django.shortcuts import render


def _render_error(request, code, title, message, symbol, *, template="errors/error.html"):
    return render(
        request,
        template,
        {
            "code": code,
            "title": title,
            "message": message,
            "symbol": symbol,
        },
        status=code,
    )


def bad_request(request, exception=None):
    return _render_error(
        request, 400, "Bad request",
        "The request could not be understood. Please check it and try again.",
        "⚠",
    )


def permission_denied(request, exception=None):
    return _render_error(
        request, 403, "Access denied",
        "You do not have permission to view this page or perform this action.",
        "🔒",
    )


def page_not_found(request, exception=None):
    return _render_error(
        request, 404, "Page not found",
        "The page may have moved, been removed, or the address may be incorrect.",
        "⌕",
    )


def server_error(request):
    return _render_error(
        request, 500, "Something went wrong",
        "An unexpected error occurred on our server. Please try again later.",
        "⚙",
    )


def method_not_allowed(request, message=None):
    """Use from a view when a request uses an unsupported HTTP method."""
    return _render_error(
        request, 405, "Method not allowed",
        message or "This action does not support the HTTP method used.",
        "⚠",
    )


def service_unavailable(request, message=None):
    """Use from a view or maintenance middleware when the service is unavailable."""
    return _render_error(
        request, 503, "Temporarily unavailable",
        message or "The service is temporarily unavailable. Please try again shortly.",
        "⏳",
    )
