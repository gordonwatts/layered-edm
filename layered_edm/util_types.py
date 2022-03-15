from typing import Any, Dict, Optional, Type, TypeVar
from typing import get_args


# TODO: This all comes from func_adl - should we keep it there
# since that needs to be part of this?


def is_iterable(t: Type) -> bool:
    "Is this type iterable?"
    while (t is not Any) and (not _is_iterable_direct(t)):
        t = get_inherited(t)

    return t is not Any


def _is_iterable_direct(t: Type) -> bool:
    "Is this type iterable?"
    if getattr(t, "_name", None) == "Iterable":
        return True
    return False


def get_inherited(t: Type) -> Type:
    """Returns the inherited type of `t`

    Notes:
    * This works for 3.7 forward (but not back!)

    Args:
        t (Type): The type (a class) that we should look at

    Returns:
        Type: The type for an inherited class, or `Any` if none can be found
    """
    if hasattr(t, "__orig_bases__"):
        base_classes = getattr(t, "__orig_bases__", None)
    elif hasattr(t, "__origin__") and hasattr(t.__origin__, "__orig_bases__"):
        base_classes = t.__origin__.__orig_bases__
    else:
        return Any

    r = base_classes[0]  # type: ignore

    g_args = get_args(t)
    if len(g_args) > 0:
        mapping = {a.__name__: v for a, v in zip(r.__parameters__, g_args)}
        r.__args__ = tuple(_resolve_type(t_arg, mapping) for t_arg in get_args(r))

    return r


def _resolve_type(t: Type, parameters: Dict[str, Type]) -> Optional[Type]:
    """Resolve any parameters in `t` with what we find in `parameters`

    int, {} => int
    ~T, {~T: int} => int
    ~K, {~T: int} => None

    Args:
        t (Type): The type to resolve
        parameters (Dict[str, Type]): The dict of types to resolve

    Returns:
        None if `t` is parameterized by unknown type var's
        The resolved type (a copy leaving `t` untouched) if TypeVar's are filled in
        The type if no substition is required.
    """
    if isinstance(t, TypeVar):
        if t.__name__ in parameters:
            return parameters[t.__name__]
        return None

    template_params = getattr(t, "__parameters__", None)
    if template_params is not None and (len(template_params) > 0):
        resolved_params = [_resolve_type(p, parameters) for p in template_params]
        if None in resolved_params:
            return None
        return t[tuple(resolved_params)]

    # Non-parameterized types are easy
    return t
