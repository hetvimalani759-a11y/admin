from django.shortcuts import redirect

def panel_required(panel):
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect("app:login")

            if request.session.get("panel") != panel:
                return redirect("app:login")

            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
