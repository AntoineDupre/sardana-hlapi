from hlpseudocontroller import (
    HlPseudoController,
    pseudo_role,
    axis_attribute,
    ctrl_attribute,
)

class MyCtrl(HlPseudoController):
    _sign = 1

    # Roles
    ## Gap
    @pseudo_role(axis=1, motors=["slit2t", "slit2b"])
    def Gap(self, slit2t, slit2b):
        return self._sign * (slit2t + slit2t)

    @Gap.setter
    def calc_gap(self, gap, offset):
        return self._sign * (gap / 2.0 + offset)

    ## Offset
    @pseudo_role(axis=2, motors=["slit2t", "slit2b"])
    def Offset(self, slit2t, slit2b):
        return self._sign * (slit2t - (slit2t + slit2b) / 2.0)

    @Offset.setter
    def set_offset(self, gap, offset):  # Maybe bind with names ?
        return self._sign * (gap / 2.0 + offset)

    # Axis
    @axis_attribute(Type=float)
    def Grating(self, index):
        return self._grating

    @Grating.setter
    def set_grating(self, index, value):
        self._grating = value

    # Ctrl
    @ctrl_attribute(Type=float)
    def Sign(self, index, value):
        return self._sign

    @Sign.setter
    def set_sign(self, index, value):
        self._sign = 1
