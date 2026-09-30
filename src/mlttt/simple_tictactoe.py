from dataclasses import dataclass
from random import choice, random
import subprocess
#import ast
from time import sleep
from sklearn.ensemble import RandomForestClassifier
import joblib
import pickle
import os

DATA_PATH = "ttt_O_dataset.pkl"
if os.path.exists(DATA_PATH):
    with open(DATA_PATH, mode='rb') as f:
        dataset = pickle.load(f)
    print(f"loaded {len(dataset)} samples from {DATA_PATH}")
else:
    dataset = []

def train_model():
    global dataset
    dataset = [ (list(lst), n) for lst, n in { (tuple(lst), n) for lst, n in dataset } ]
    X = [state for state, _ in dataset]
    y = [label for _, label in dataset]
    clf = RandomForestClassifier(n_estimators=200, random_state=42)
    clf.fit(X, y)
    joblib.dump(clf, "ttt_O_bot.joblib")
    with open(DATA_PATH, mode='wb') as f:
        pickle.dump(dataset, f)
    print("model trained and saved as ttt_O_bot.joblib\ndataset saved as ttt_O_dataset.pkl")


board = [
    ["", "", ""],
    ["", "", ""],
    ["", "", ""]
]

game_dataset = []

def update_game_dset(o_move):
    global game_dataset
    status = ([-1 if board[row][col] == "X" else 1 if board[row][col] == "O" else 0 for row in range(3) for col in range(3) ], o_move)
    game_dataset.append(
        status
    )

bot = joblib.load("ttt_O_bot.joblib")
turn = "X"

def draw_table(g_count):
    subprocess.run("clear", shell=True)
    print(f"game number {g_count + 1}:")
    if any(row for row in board):
        print("*---*---*---*---*---*")
        print(f"\n({board[0][0]})\t({board[0][1]})\t({board[0][2]})")
        print(f"\n({board[1][0]})\t({board[1][1]})\t({board[1][2]})")
        print(f"\n({board[2][0]})\t({board[2][1]})\t({board[2][2]})")
        print("\n*---*---*---*---*---*")
    else:
        print("*---*---*---*---*---*")
        print("\n()\t()\t()")
        print("\n()\t()\t()")
        print("\n()\t()\t()")
        print("\n*---*---*---*---*---*")
    print(f"TURN: {turn}")

def check_state():
    @dataclass
    class SeqCounter:
        count_rx: int = 0
        count_ro: int = 0
        count_cx: int = 0
        count_co: int = 0
    counter = SeqCounter()
    for row in range(3):
        counter.count_rx = 0
        counter.count_ro = 0
        for col in range(3):
            if board[row][col] == "X":
                counter.count_rx += 1
                counter.count_ro = 0
            elif board[row][col]:
                counter.count_rx = 0
                counter.count_ro += 1
            else:
                break
            if counter.count_rx == 3:
                return 0
            elif counter.count_ro == 3:
                return 1
    for col in range(3):
        counter.count_cx = 0
        counter.count_co = 0
        for row in range(3):
            if board[row][col] == "X":
                counter.count_cx += 1
                counter.count_co = 0
            elif board[row][col]:
                counter.count_cx = 0
                counter.count_co += 1
            else:
                break
            if counter.count_cx == 3:
                return 0
            elif counter.count_co == 3:
                return 1
    if board[0][0] == board[1][1] == board[2][2] or board[0][2] == board[1][1] == board[2][0]:
        return 0 if board[1][1] == "X" else 1 if board[1][1] == "O" else None
    return None

def encoder(): # bot will be always Player O
    vector = []
    for row in range(3):
        for col in range(3):
            if board[row][col] == "X":
                vector.append(-1)
            elif board[row][col] == "O":
                vector.append(1)
            else:
                vector.append(0)
    return vector

def bot_move(ep=0.2):
    if random() < ep:
        legal = [(i, j) for i in range(3) for j in range(3) if board[i][j] == ""]
        r, c = choice(legal)
    else:
        predict = int(bot.predict([encoder()])[0])
        r, c = divmod(predict, 3)
        if board[r][c] != "":
            legal_moves = [(i, j) for i in range(3) for j in range(3) if board[i][j] == ""]
            r, c = choice(legal_moves)
    update_game_dset((r * 3) + c)
    return r + 1, c + 1

def random_x():
    legal_moves = [(i, j) for i in range(3) for j in range(3) if board[i][j] == ""]
    r, c = choice(legal_moves)
    return r + 1, c + 1

def game_handler(n_game = 100, retrain_every = 50):
    global dataset
    global board
    global bot
    global turn
    g_state = None
    n_draw = 0
    n_o = 0

    def loop(g_count):
        global board
        global turn
        nonlocal g_state

        while True:
            draw_table(g_count)
            try:
                choice = random_x() if turn == "X" else bot_move(0.0) # ast.literal_eval(input("Enter your choice (r=[1, 3], c=[1, 3]): "))
                if not board[int(choice[0] - 1)][int(choice[1] - 1)]:
                    board[int(choice[0] - 1)][int(choice[1] - 1)] = turn
                    turn = "X" if turn == "O" else "O"
                    g_state = check_state()
                    if g_state is not None:
                        g_state = True
                        draw_table(g_count)
                        return
                    elif all(all(col for col in row) for row in board):
                        g_state = False
                        draw_table(g_count)
                        return

                else:
                    raise Exception
            except Exception:
                print("invalid input. try again.")
                sleep(1.5)
    for g_count in range(n_game):
        loop(g_count)
        if g_state:
            winner = "X" if turn == "O" else "O"
            print(f"Player: {winner} won!")
            if winner == "O":
                dataset += game_dataset
                n_o += 1
        elif g_state is False:
            print("Draw!")
            n_draw += 1
        board = [["", "", ""], ["", "", ""], ["", "", ""]]
        turn = "X"
        game_dataset.clear()
        if (g_count + 1) % retrain_every == 0:
            train_model()
            bot = joblib.load("ttt_O_bot.joblib")
        #sleep(1.25)
    print(f"total games: {n_game}")
    print(f"O-won games: {n_o}")
    print(f"draw games: {n_draw}")
    print(f"X-won games: {n_game - (n_o + n_draw)}")
    print(f"accuracy: {n_o/n_game:2f}")

game_handler(5000, 1000)
train_model()
