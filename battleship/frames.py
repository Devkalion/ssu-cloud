import tkinter


class Root(tkinter.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        icon = tkinter.PhotoImage(height=16, width=16)
        icon.blank()
        self.iconphoto(True, icon)
        self.title('')
        self.resizable(height=False, width=False)


class PlaceField(tkinter.Frame):
    pass


class BattleField(tkinter.Frame):
    pass
