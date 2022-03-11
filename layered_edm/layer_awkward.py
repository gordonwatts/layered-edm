# from typing import Callable
# import awkward as ak
# from .base_layer import BaseEDMLayer


# class LEDMAwkward(BaseEDMLayer):
#     def __init__(self, awk_array: ak.Array):
#         super().__init__(awk_array, "awk")


# def edm_awk(class_to_wrap: Callable) -> Callable:
#     "Creates a class edm based on an awkward array"

#     def make_it(arr: ak.Array):
#         return LEDMAwkward(arr)

#     return make_it
