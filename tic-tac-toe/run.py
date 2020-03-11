import random
import tkinter

EMPTY = 0
COMP = -1
USER = 1


class Field(tkinter.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.winner = None
        self.flags = None
        self.buttons = None
        self.clear()

    def clear(self):
        self.winner = None
        self.flags = [EMPTY for _ in range(9)]
        self.buttons = [
            tkinter.Button(self, text='', command=self.turn(i))
            for i in range(9)
        ]
        for i, btn in enumerate(self.buttons):
            btn.grid(row=int(i / 3) + 1, column=i % 3)

    def get_empty(self, indexes):
        for i in indexes:
            if self.flags[i] == EMPTY:
                return i

    def find_closest(self, user):
        for i in range(3):
            if sum(self.flags[i * 3: i * 3 + 3]) == 2 * user:
                return self.get_empty(range(i * 3, i * 3 + 3))

            if sum(self.flags[i::3]) == 2 * user:
                return self.get_empty(range(i, len(self.flags), 3))

        if sum(self.flags[::4]) == 2 * user:
            return self.get_empty(range(0, len(self.flags), 3))

        if sum(self.flags[2:7:2]) == 2 * user:
            return self.get_empty(range(2, 7, 2))

    def ai_turn(self):
        win_id = self.find_closest(COMP)
        if win_id:
            return win_id
        block_id = self.find_closest(USER)
        if block_id:
            return block_id

        random_ids = [i for i, x in enumerate(self.flags) if x == EMPTY]
        random.shuffle(random_ids)
        return random_ids[0]

    def make_turn(self, cell, player):
        self.buttons[cell]['text'] = 'X' if player == USER else 'O'
        self.flags[cell] = player
        self.winner = self.get_winner()

    def turn(self, user_cell):
        def f():
            if self.winner is not None or self.flags[user_cell] != EMPTY:
                return
            self.make_turn(user_cell, USER)
            if self.winner is not None:
                self.end_game()
                return

            comp_cell = self.ai_turn()
            self.make_turn(comp_cell, COMP)

            if self.winner is not None:
                self.end_game()
                return

        return f

    def end_game(self):
        if self.winner == USER:
            winner_text = 'You are win'
        elif self.winner == COMP:
            winner_text = 'You are lose'
        else:
            winner_text = 'You are draw'
        lbl = tkinter.Label(self, text=winner_text)
        lbl.grid(row=0, column=0, columnspan=3)
        # self.quit()
        print(self.winner)

    def get_winner(self):
        sums = [
            *(sum(self.flags[i * 3: i * 3 + 3]) for i in range(3)),
            *(sum(self.flags[i::3]) for i in range(3)),
            sum(self.flags[::4]),
            sum(self.flags[2:7:2])
        ]

        filtered_sums = [
            USER if s == USER * 3 else COMP
            for s in sums
            if s / 3 in (USER, COMP)
        ]

        if filtered_sums:
            return filtered_sums[0]

        if all(map(lambda x: x != EMPTY, self.flags)):
            return EMPTY


def configure(frame):
    icon = tkinter.PhotoImage(height=16, width=16)
    icon.blank()
    frame.iconphoto(True, icon)
    frame.title('')
    frame.resizable(height=False, width=False)


if __name__ == '__main__':
    root = tkinter.Tk()
    configure(root)
    Field(root).pack()
    root.mainloop()
