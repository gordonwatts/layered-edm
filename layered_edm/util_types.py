from dataclasses import dataclass
import uuid
from typing import Any, Callable, Dict, List, Optional, Type, TypeVar, Union, get_args

import awkward as ak

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


def _get_behavior_name(b_name: Union[str, type]):
    if isinstance(b_name, str):
        return b_name
    return b_name.__name__


def _get_behavior_object(b_name: Union[str, type]):
    if isinstance(b_name, str):
        return ak.behavior["*", b_name]
    else:
        return b_name


@dataclass
class AkBehaviorInfo:
    "Awkward behavior registration info"

    # The name or type of the behavior
    name: Union[str, type]

    # Callback to register the behavior if need be.
    register_callback: Optional[Callable[[], None]]


def append_awk_behavior_to_class(
    class_to_wrap: type,
    behavior_name: Union[str, type],
    reg_function: Optional[Callable[[], None]],
):
    "Add a behavior info to a class"
    if not hasattr(class_to_wrap, "_awk_behaviors"):
        setattr(class_to_wrap, "_awk_behaviors", [])
    getattr(class_to_wrap, "_awk_behaviors").append(AkBehaviorInfo(behavior_name, reg_function))


def class_behavior(class_to_wrap: Callable) -> Optional[str]:
    """Scan a given class for any defined behaviors.

    Args:
        class_to_wrap (type): Class to scan

    Returns:
        type: The behavior type, or None if no behaviors are found.
    """
    behavior_list: Optional[List[AkBehaviorInfo]] = getattr(class_to_wrap, "_awk_behaviors", None)
    if behavior_list is None:
        return None

    # Call all the callback functions
    for cb in behavior_list:
        if cb.register_callback is not None:
            cb.register_callback()

    behavior_name: Optional[str] = None
    behavior_object = None
    if len(behavior_list) == 1:
        behavior_name = _get_behavior_name(behavior_list[0].name)
        behavior_object = None if isinstance(behavior_list[0].name, str) else behavior_list[0].name
    else:
        # Multiple behaviors are done by multiple inheritance.
        class all_behaviors(*(_get_behavior_object(c.name) for c in behavior_list)):  # type: ignore
            pass

        behavior_name = str(uuid.uuid4())
        behavior_object = all_behaviors

    # Make sure the behavior is registered
    if ("*", behavior_name) not in ak.behavior:
        if behavior_object is not None:
            ak.behavior["*", behavior_name] = behavior_object
            ak.behavior[behavior_name] = behavior_object
        else:
            raise ValueError(f'Awkward behavior "{behavior_name}" is not declared to awkward')

    return behavior_name
