import asyncio
import inspect
from typing import Any, Callable, Coroutine, Dict, cast

import panel as pn

from imednet import ImednetSDK
from imednet.endpoints.base import BaseEndpoint
from imednet.utils import configure_json_logging


def _collect_functions(sdk: ImednetSDK) -> Dict[str, Callable[..., Any]]:
    """Return a mapping of callable names to bound methods."""
    funcs: Dict[str, Callable[..., Any]] = {}
    for name in dir(sdk):
        if name.startswith("_"):
            continue
        member = getattr(sdk, name)
        if isinstance(member, BaseEndpoint):
            for func_name in dir(member):
                if func_name.startswith("_"):
                    continue
                func = getattr(member, func_name)
                if callable(func):
                    funcs[f"{name}.{func_name}"] = func
        elif callable(member):
            funcs[name] = member
    return funcs


def _widgets_for_function(func: Callable[..., Any]) -> list[pn.widgets.Widget]:
    """Create widgets based on a function signature."""
    widgets: list[pn.widgets.Widget] = []
    sig = inspect.signature(func)
    for param in sig.parameters.values():
        if param.name == "self":
            continue
        default = None if param.default is inspect._empty else param.default
        ann = param.annotation
        if ann is int:
            widget = pn.widgets.IntInput(name=param.name, value=default or 0)
        elif ann is float:
            widget = pn.widgets.FloatInput(name=param.name, value=default or 0.0)
        elif ann is bool:
            widget = pn.widgets.Checkbox(name=param.name, value=bool(default))
        else:
            widget = pn.widgets.TextInput(name=param.name, value=str(default or ""))
        widgets.append(widget)
    return widgets


def create_app() -> pn.Column | pn.pane.Markdown:
    """Return a Panel app for interacting with SDK functions."""
    print("Initializing ImednetSDK...")
    configure_json_logging()
    sdk = ImednetSDK()
    print("Collecting functions...")
    functions = _collect_functions(sdk)
    print(f"Collected {len(functions)} functions")
    if not functions:
        return pn.pane.Markdown("**No functions found in ImednetSDK.**")

    loading = pn.indicators.LoadingSpinner(value=True)
    layout = pn.Column(loading)

    select = pn.widgets.Select(name="Function", options=sorted(functions))
    params = pn.Column()
    result = pn.pane.JSON(width=800)

    def update_params(event: Any | None = None) -> None:
        params.clear()
        name = select.value if event is None else event.new
        func = functions[name]
        params.extend(_widgets_for_function(func))

    select.param.watch(update_params, "value")
    update_params()

    run = pn.widgets.Button(name="Run", button_type="primary")

    def execute(_: Any) -> None:
        func = functions[select.value]
        sig = inspect.signature(func)
        kwargs = {}
        for widget in params:
            param = sig.parameters[widget.name]
            val = widget.value
            if param.annotation is int:
                val = int(val)
            elif param.annotation is float:
                val = float(val)
            elif param.annotation is bool:
                val = bool(val)
            kwargs[widget.name] = val
        outcome = func(**kwargs)
        if inspect.isawaitable(outcome):
            outcome = asyncio.run(cast(Coroutine[Any, Any, Any], outcome))
        result.object = outcome

    run.on_click(execute)

    layout[:] = [select, params, run, result]
    loading.value = False
    print("UI ready")
    return layout


if __name__ == "__main__":
    pn.extension()
    create_app().servable()
