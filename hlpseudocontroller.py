from collections import OrderedDict

import sardana
from sardana.pool.controller import PseudoMotorController, DefaultValue
from sardana.pool.controller import Type, Access, Description, DataAccess
from sardana.pool.controller import FGet, FSet


class pseudo_role:
    def __init__(self, axis, motors):
        self.axis = 1
        self.motors = motors

    def setter(self, func):
        self.calc_physical = func

    def __call__(self, func):
        if not hasattr(self, "calc_pseudo"):
            print("Set calc_pseudo", func)
            self.calc_pseudo = func
            return self
        else:
            return self.calc_pseudo


class SardanaAttribute:
    def __init__(self, **args):
        self.args = args
        self.name = ""
        self._get = None
        self._set = None

    def to_dict(self):
        dct = self.args.copy()
        dct[Type] = float
        dct[FGet] = self._get.func_name
        if self._set:
            dct[FSet] = self._set.func_name
        return dct

    def __call__(self, *args):
        if not self._get:
            func = args[0]
            self.name = func.func_name
            self._get = func
            return self
        else:
            print(args)
            self._get(*args)

    def setter(self, func):
        self._set = func


# axis_attribute = type("axis_attribute", (SardanaAttribute,), {})
# ctrl_attribute = type("axis_attribute", (SardanaAttribute,), {})
class axis_attribute(SardanaAttribute):
    pass


class ctrl_attribute(SardanaAttribute):
    pass


class MetaController(type):
    def __new__(cls, name, bases, dct):
        bases = bases + (PseudoMotorController,)
        # A small hack to get ordered set
        motor_roles = OrderedDict()
        pseudo_axis = []
        axis_attributes = {}
        ctrl_attributes = {}
        for k, attr in dct.items():
            if isinstance(attr, pseudo_role):
                attr.name = k
                pseudo_axis.append(attr)
                for m in attr.motors:
                    motor_roles[m] = None
            if isinstance(attr, axis_attribute):
                axis_attributes[attr.name] = attr.to_dict()
            if isinstance(attr, ctrl_attribute):
                ctrl_attributes[attr.name] = attr.to_dict()
        pseudo_axis = [a for a in sorted(pseudo_axis, key=lambda x: x.axis)]
        pseudo_motor_roles = [a.name for a in pseudo_axis]
        dct["_pseudo_axis"] = pseudo_axis
        dct["pseudo_motor_roles"] = pseudo_motor_roles
        # TODO: remove this hack
        dct["motor_roles"] = motor_roles.keys()
        dct["axis_attributes"] = axis_attributes
        dct["ctrl_attributes"] = ctrl_attributes
        return type.__new__(cls, name, bases, dct)


class HlPseudoController:
    __metaclass__ = MetaController

    def CalcPhysical(self, index, pseudo_pos, curr_physical_pos):
        print("CalcPhysical", index)
        return self._pseudo_axis[index - 1].calc_physical(self, *pseudo_pos)

    def CalcPseudo(self, index, physical_pos, curr_pseudo_pos):
        print("CalcPseudo", index)
        return self._pseudo_axis[index - 1].calc_pseudo(self, *physical_pos)

    def CalcAllPhysical(self, pseudo, curr):
        print("CalcAllPhysical")
        return [
            self.CalcPhysical(i, pseudo, curr)
            for i, _ in enumerate(self._pseudo_axis)
        ]

    def CalcAllPseudo(self, phy, curr):
        print("CalcAllPseudo")
        return [
            self.CalcPseudo(i, phy, curr)
            for i, _ in enumerate(self._pseudo_axis)
        ]
