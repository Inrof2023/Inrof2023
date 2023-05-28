from typing import Any
class _const(object):
    class ConstError(TypeError):
        pass

    def __setattr__(self, name: str, value: Any) -> None:
        if name in self.__dict__:
            raise self.ConstError()
        self.__dict__[name] = value

import sys
sys.modules[__name__] = _const()

