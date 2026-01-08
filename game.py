import tkinter as tk
import random
from PIL import Image, ImageTk
import os
import winsound

snakes = {
    16: 6, 47: 26, 49: 11, 56: 32, 62: 19, 64: 60,
    87: 24, 93: 73, 95: 75, 98: 78
}

ladders = {
    4: 14, 9: 31, 21: 42, 28: 84,
    36: 44, 51: 67, 71: 91, 80: 96
}

CELL_SIZE = 60
BOARD_SIZE = 10
ANIMATION_SPEED = 50

class SnakesAndLadders:
    def __init__(self, root):
        self.root = root
        self.root.title("Snakes and Ladders 🐍🎲")
        self.root.config(bg="#E8F6F3")

        self.players = []
        self.positions = []
        self.tokens = []
        self.turn = 0
        self.total_players = 2
        self.score_history = []

        self.board_image = None
        self.load_board_image()

        self.canvas = tk.Canvas(root, width=CELL_SIZE * BOARD_SIZE, height=CELL_SIZE * BOARD_SIZE, bg="#DFF6F0", highlightthickness=0)
        self.canvas.grid(row=0, column=0, columnspan=6)
        self.draw_board()

        self.player_entries = []
        for i in range(4):
            entry = tk.Entry(root, font=("Helvetica", 12))
            entry.grid(row=1, column=i, padx=5, pady=5)
            self.player_entries.append(entry)

        self.num_players_var = tk.IntVar(value=2)
        self.num_players_menu = tk.OptionMenu(root, self.num_players_var, *[1, 2, 3, 4], command=self.update_entries_visibility)
        self.num_players_menu.grid(row=1, column=4, padx=5)

        self.start_btn = tk.Button(root, text="Start Game", font=("Helvetica", 12, "bold"), bg="#5CAB7D", fg="white", command=self.start_game)
        self.start_btn.grid(row=1, column=5, padx=5, pady=5)

        self.roll_btn = tk.Button(root, text="Roll Dice 🎲", font=("Helvetica", 12, "bold"), bg="#496D89", fg="white", state="disabled", command=self.start_dice_animation)
        self.roll_btn.grid(row=2, column=0, columnspan=6, pady=10)

        self.dice_label = tk.Label(root, text="🎲 Roll: 0", font=("Helvetica", 20, "bold"), bg="#E8F6F3", fg="#496D89")
        self.dice_label.grid(row=2, column=6, padx=10)

        self.status = tk.Label(root, text="Enter player names and click Start Game", bg="#E8F6F3", fg="darkgreen", font=("Helvetica", 14, "italic"))
        self.status.grid(row=3, column=0, columnspan=6, pady=10)

        self.reset_btn = tk.Button(root, text="Reset Game", font=("Helvetica", 10), bg="#FF6B6B", fg="white", command=self.reset_game)
        self.reset_btn.grid(row=4, column=0, columnspan=6, pady=5)

        self.history_frame = tk.Frame(root, bg="#E8F6F3", bd=2, relief="groove")
        self.history_frame.grid(row=0, column=6, rowspan=5, padx=10, sticky="n")

        tk.Label(self.history_frame, text="📜 History", bg="#E8F6F3", font=("Helvetica", 12, "bold")).pack(pady=(5, 0))
        self.history_box = tk.Listbox(self.history_frame, height=25, width=30, font=("Courier", 10))
        self.history_box.pack(pady=5, padx=5)


        self.update_entries_visibility(self.num_players_var.get())

        self.animating = False
        self.token_animating = False

    def load_board_image(self):
        try:
            image_files = ['board.png', 'board.jpg', 'snakes_ladders.png', 'snakes_ladders.jpg']
            for img_file in image_files:
                if os.path.exists(img_file):
                    img = Image.open(img_file)
                    img = img.resize((CELL_SIZE * BOARD_SIZE, CELL_SIZE * BOARD_SIZE), Image.Resampling.LANCZOS)
                    self.board_image = ImageTk.PhotoImage(img)
                    break
        except Exception as e:
            print(f"Could not load board image: {e}")
            self.board_image = None

    def draw_board(self):
        if self.board_image:
            self.canvas.create_image(0, 0, anchor="nw", image=self.board_image)
        else:
            colors = ["#C4E1C1", "#A3D2CA"]
            for row in range(BOARD_SIZE):
                for col in range(BOARD_SIZE):
                    actual_row = BOARD_SIZE - 1 - row
                    if actual_row % 2 == 0:
                        cell_num = actual_row * BOARD_SIZE + col + 1
                    else:
                        cell_num = actual_row * BOARD_SIZE + (BOARD_SIZE - col)
                    x1 = col * CELL_SIZE
                    y1 = row * CELL_SIZE
                    x2 = x1 + CELL_SIZE
                    y2 = y1 + CELL_SIZE
                    if cell_num in snakes:
                        fill_color = "#FFB3B3"
                    elif cell_num in ladders:
                        fill_color = "#B3FFB3"
                    else:
                        fill_color = colors[(row + col) % 2]
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill=fill_color, outline="#557A95", width=1)
                    self.canvas.create_text(x1 + 30, y1 + 15, text=str(cell_num), font=("Arial", 10, "bold"), fill="#2E4F4F")
                    if cell_num in snakes:
                        self.canvas.create_text(x1 + CELL_SIZE//2, y1 + CELL_SIZE//2 + 5, text="🐍", font=("Arial", 16))
                    elif cell_num in ladders:
                        self.canvas.create_text(x1 + CELL_SIZE//2, y1 + CELL_SIZE//2 + 5, text="🪜", font=("Arial", 16))

    def get_coords(self, pos):
        row = (pos - 1) // BOARD_SIZE
        col = (pos - 1) % BOARD_SIZE
        if row % 2 == 1:
            col = BOARD_SIZE - 1 - col
        x = col * CELL_SIZE + CELL_SIZE // 2
        y = (BOARD_SIZE - 1 - row) * CELL_SIZE + CELL_SIZE // 2
        return x, y

    def get_token_coords(self, pos, player):
        x, y = self.get_coords(pos)
        offset = (player - 2) * 12
        return (x - 8, y + offset - 8, x + 8, y + offset + 8)

    def update_entries_visibility(self, num_players):
        for i, entry in enumerate(self.player_entries):
            if i < num_players:
                entry.grid()
            else:
                entry.grid_remove()

    def start_game(self):
        self.players = []
        self.positions = []
        self.tokens = []
        self.turn = 0
        self.total_players = self.num_players_var.get()

        for token in self.tokens:
            self.canvas.delete(token)
        self.tokens.clear()

        for i in range(self.total_players):
            name = self.player_entries[i].get().strip()
            if self.total_players == 1 and i == 1:
                name = "Computer"
            if not name:
                name = f"Player {i + 1}"
            self.players.append(name)
            self.positions.append(1)
            token = self.canvas.create_oval(*self.get_token_coords(1, i + 1), fill=self.get_color(i), outline="black", width=2)
            self.tokens.append(token)

        if self.total_players == 1:
            self.players.append("Computer")
            self.positions.append(1)
            token = self.canvas.create_oval(*self.get_token_coords(1, 2), fill=self.get_color(1), outline="black", width=2)
            self.tokens.append(token)
            self.total_players = 2

        self.status.config(text=f"{self.players[0]}'s turn ⏳")
        self.roll_btn.config(state="normal")
        self.start_btn.config(state="disabled")
        for entry in self.player_entries:
            entry.config(state="disabled")

        self.dice_label.config(text="🎲 Roll: 0")

        if self.players[0] == "Computer":
            self.roll_btn.config(state="disabled")
            self.root.after(1500, self.start_dice_animation)

    def get_color(self, idx):
        colors = ["#D72631", "#1B98E0", "#F4A261", "#8E44AD"]
        return colors[idx % len(colors)]

    def start_dice_animation(self):
        if not self.animating and not self.token_animating:
            self.animating = True
            self.roll_btn.config(state="disabled")
            self.dice_roll_result = random.randint(1, 6)
            winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS)
            self.status.config(text=f"{self.players[self.turn]} rolled 🎲 {self.dice_roll_result}")
            self.dice_label.config(text=f"🎲 Roll: {self.dice_roll_result}")
            self.animating = False
            self.animate_token_move(self.dice_roll_result)

    def animate_token_move(self, roll):
        self.token_animating = True
        current_pos = self.positions[self.turn]
        intermediate_pos = current_pos + roll

        if intermediate_pos > 100:
            self.token_animating = False
            self.finish_turn(current_pos, current_pos, roll)
            return

        path = list(range(current_pos + 1, intermediate_pos + 1))

        def after_main_move():
            final_pos = self.update_position(intermediate_pos, 0)
            if final_pos != intermediate_pos:
                if final_pos > intermediate_pos:
                    slide_path = list(range(intermediate_pos + 1, final_pos + 1))
                else:
                    slide_path = list(range(intermediate_pos - 1, final_pos - 1, -1))
                self.move_along_path(slide_path, 0, intermediate_pos, roll, after_second_move)
            else:
                self.token_animating = False
                self.finish_turn(current_pos, intermediate_pos, roll)

        def after_second_move():
            self.token_animating = False
            self.finish_turn(current_pos, self.positions[self.turn], roll)

        self.move_along_path(path, 0, current_pos, roll, after_main_move)

    def move_along_path(self, path, index, start_pos, roll, callback=None):
        if index >= len(path):
            if callback:
                callback()
            return
        pos = path[index]
        self.positions[self.turn] = pos
        self.canvas.coords(self.tokens[self.turn], *self.get_token_coords(pos, self.turn + 1))
        self.root.after(ANIMATION_SPEED, self.move_along_path, path, index + 1, start_pos, roll, callback)

    def update_position(self, pos, roll):
        new_pos = pos + roll
        if new_pos > 100:
            return pos
        if new_pos in snakes:
            return snakes[new_pos]
        elif new_pos in ladders:
            return ladders[new_pos]
        return new_pos

    def finish_turn(self, old_pos, new_pos, roll):
        msg = ""
        if new_pos < old_pos + roll:
            msg = f"{self.players[self.turn]} got bitten by a 🐍 and slid down to {new_pos}!"
        elif new_pos > old_pos + roll:
            msg = f"{self.players[self.turn]} climbed a 🪜 to {new_pos}!"
        else:
            msg = f"{self.players[self.turn]} moved to {new_pos}."

        self.positions[self.turn] = new_pos  
        self.status.config(text=msg)
        self.score_history.append(f"{self.players[self.turn]} rolled {roll} and moved from {old_pos} to {new_pos}")
        self.update_history_box()


        if new_pos == 100:
            self.show_winner_popup(self.players[self.turn])
            self.roll_btn.config(state="disabled")
            return

        self.turn = (self.turn + 1) % self.total_players
        self.root.after(1500, self.next_turn)

    def next_turn(self):
        next_player = self.players[self.turn]
        self.status.config(text=f"{next_player}'s turn ⏳")
        self.roll_btn.config(state="normal")

        if next_player == "Computer":
            self.roll_btn.config(state="disabled")
            self.root.after(1500, self.start_dice_animation)

    def update_history_box(self):
        self.history_box.delete(0, tk.END)
        for entry in self.score_history[-10:]:
            self.history_box.insert(tk.END, entry)

    def reset_game(self):
        self.players.clear()
        self.positions.clear()
        for token in self.tokens:
            self.canvas.delete(token)
        self.tokens.clear()
        self.turn = 0
        self.score_history.clear()
        self.history_box.delete(0, tk.END)

        self.roll_btn.config(state="disabled")
        self.start_btn.config(state="normal")
        for entry in self.player_entries:
            entry.config(state="normal")
            entry.delete(0, tk.END)

        self.status.config(text="Enter player names and click Start Game")
        self.dice_label.config(text="🎲 Roll: 0")

    def show_winner_popup(self, winner):
        popup = tk.Toplevel(self.root)
        popup.title("🎉 We have a Winner! 🎉")
        popup.geometry("300x150")
        popup.config(bg="#FFFAF0")

        label = tk.Label(popup, text=f"🏆 Congratulations, {winner}! 🏆", font=("Helvetica", 14, "bold"), bg="#FFFAF0", fg="#2E8B57")
        label.pack(pady=20)

        btn = tk.Button(popup, text="Close", command=popup.destroy, bg="#5CAB7D", fg="white", font=("Helvetica", 12, "bold"))
        btn.pack(pady=10)

        colors = ["#FFDDC1", "#FFABAB", "#FFC3A0", "#FF677D", "#D4A5A5"]
        def animate_bg(i=0):
            if i < 15:
                popup.config(bg=colors[i % len(colors)])
                label.config(bg=colors[i % len(colors)])
                btn.config(bg=colors[(i+2) % len(colors)])
                popup.after(300, animate_bg, i+1)
            else:
                popup.config(bg="#FFFAF0")
                label.config(bg="#FFFAF0")
                btn.config(bg="#5CAB7D")

        animate_bg()

if __name__ == "__main__":
    root = tk.Tk()
    game = SnakesAndLadders(root)
    root.mainloop()

