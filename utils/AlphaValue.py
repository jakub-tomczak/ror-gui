from tkinter import DoubleVar, StringVar
import ror.alpha as ror_alpha


class AlphaValue:
    def __init__(self) -> None:
        self.name: StringVar = StringVar('')
        self.value: DoubleVar = DoubleVar(0.0)


    def to_ror_alpha_value(self) -> ror_alpha.AlphaValue:
        return ror_alpha.AlphaValue(self.value.get(), self.name.get())

    def __eq__(self, o: object) -> bool:
        return type(o) is AlphaValue and o.value == self.value and o.name == self.name

    def __hash__(self) -> int:
        return 19*hash(self.value) + 13*hash(self.name)

    def __repr__(self) -> str:
        return f'<GUIAlphaValue [name: {self.name.get()}, value: {self.value.get()}]>'