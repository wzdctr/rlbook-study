# textbook implementation
import random
from itertools import combinations
from rich.console import Console

console = Console()

# FIXME: only a 73% winrate..?
# some of the earlier states are not getting updated

"""
states
"""

# the agent will play as "O", not "X"

# we visualize the TTT board as a 3x3 magic square,
# where all numbers are unique single-digit integers,
# and only vertical/horizontal/diagonals add to 15.
game_board = [2, 7, 6, 9, 5, 1, 4, 3, 8]

# the agent requires a means to select moves based on P(o_win)
# so we provide it a look-up table with all possible states of the game
# we simplify all possible states through binary encoding as 2^9
# this will make an array of 262,144 'None' which will be later populated.
# FIXME: this should be 2^9 * 2 ^9, but somehow state indexes exceed this value
value_table = [None] * ((2**10) * (2**9))

# the agent also needs to keep track of the game's state
# we define states as a tuple containing X and O's moves,
# and an index pointing to the corresponding P(o_win) of that state
initial_state = ([], [], 0)

# the moves are just the cell numbers of the magic square.
# e.g. x_moves = state[0] = [2, 7, 6]


# index is also calculated through binary encoding
def get_state_index(x_moves, o_moves):
    """
    receives moves made by both players,
    returns the corresponding index for looking up p(win) in value_table
    """
    x_sum = sum(2**i for i in x_moves)
    o_sum = sum(2**i for i in o_moves)
    index = x_sum + 512 * o_sum
    return index


"""
moves
"""


# we need a way to see what moves we can make
def get_unoccupied_cells(state):
    x_moves, o_moves = state[0], state[1]
    occupied_cells = x_moves + o_moves
    # recall that 3x3 magic square numbers are all single-digit
    unoccupied_cells = [i for i in range(1, 10) if i not in occupied_cells]
    return unoccupied_cells


# we need a way to play moves
def explore(state, player):
    # random move
    possible_moves = get_unoccupied_cells(state)
    return random.choice(possible_moves) if possible_moves else None


def exploit(state, player):
    # move with highest p(o_win)
    possible_moves = get_unoccupied_cells(state)
    if not possible_moves:
        return None

    # we start best_value at -1, bc 0 < value < 1
    best_value = -1
    best_move = None

    for move in possible_moves:
        # calculate the value of the next state
        # at the start, O doesn't play any moves, everything will be None
        new_state = get_next_state(state, player, move)
        move_value = value_table[new_state[2]]
        if move_value > best_value:
            best_value = move_value
            best_move = move

    return best_move


# we need a way to see if we won
def check_win(moves):
    # check if any 3 numbers of the magic square add to 15
    # this should only be 3-in-a-row's
    win = any(sum(combo) == 15 for combo in combinations(moves, 3))
    return win


# we need a way to move the game forward to the next state
def get_next_state(state, player, move):
    # create shallow copies so we don't fuck with the previous state
    x_moves, o_moves = state[0][:], state[1][:]

    if player == "X":
        x_moves.append(move)
    elif player == "O":
        o_moves.append(move)
    else:
        raise Exception(f"invalid player: {player}")

    new_state = (x_moves, o_moves, get_state_index(x_moves, o_moves))
    new_state_index = new_state[2]

    # now we update the value_table. first check if it's empty
    # this always should be none for the first game
    if value_table[new_state_index] is None:
        # if o wins, we set P(o_win) = 1
        if check_win(o_moves):
            value_table[new_state_index] = 1
        # if x wins, we set P(o_win) = 0
        elif check_win(x_moves):
            value_table[new_state_index] = 0
        # if it's a tie, we also set P(o_win) = 0
        elif len(x_moves) + len(o_moves) == 9:
            value_table[new_state_index] = 0
        # if we haven't seen this state before, P(o_win) is still None
        # so we set it as 50/50
        else:
            value_table[new_state_index] = 0.5

    return new_state


# this is the core temporal difference value function to update P(o_win)
# V(S_t) <-- V(S_t) + α[V(S_t+1) - V(S_t)]
def update_state_value(state, new_state, alpha):
    state_value = value_table[state[2]]
    next_state_value = value_table[new_state[2]]
    updated_value = state_value + (alpha * (next_state_value - state_value))
    # refer to figure 1.1; we 'back up' the value of the state after each greedy move
    value_table[state[2]] = updated_value


"""
game
"""

num_games = 100000

alpha = 0.5
# epsilon 0.1 v 0.01 - wr drops by 3%?
# and at epsilon 0.5, winrate becomes 50/50
# i guess not really a meaningful difference if
epsilon = 0.01

# counter for winrate
x_wins = 0
o_wins = 0

for i in range(1, num_games):
    # reset the state
    state = initial_state
    value_table[state[2]] = 0.5
    print(" ### NEW GAME ### ")

    while True:
        # X always picks a random move
        x_move = explore(state, "X")

        # no more moves left to play, exit the loop
        if not x_move:
            break

        state_after_x = get_next_state(state, "X", explore(state, "X"))
        print(f"   x move   P(o_win): {value_table[state_after_x[2]]:.6f}")

        # we check if the game is over after each turn.
        # recall that 0 < P(o_win) < 1, X win and O win respectively
        # so we just check for integers
        # this means i'm only updating the value table after terminal states..?
        if isinstance(value_table[state_after_x[2]], int):
            update_state_value(state, state_after_x, alpha)
            if value_table[state_after_x[2]] == 0:
                console.print("   X WIN", style="red")
                x_wins += 1
            break

        # decide whether O explores (1% chance as ε = 0.01)
        # is this a different method to e - 1 ??
        if random.random() < epsilon:
            o_move = explore(state_after_x, "O")
        else:
            # we only update the state value if greedy move was taken
            o_move = exploit(state_after_x, "O")
            update_state_value(state, state_after_x, alpha)

        # no more moves left to play, exit the loop
        if not o_move:
            break

        state_after_xo = get_next_state(state_after_x, "O", o_move)
        print(f"   o move   P(o_win): {value_table[state_after_xo[2]]:.6f}")

        # again, check if the game is over
        # the difference is updating state value after checking if
        # it's a terminal state or not
        if isinstance(value_table[state_after_xo[2]], int):
            update_state_value(state_after_x, state_after_xo, alpha)
            # additionally, check if O wins after their move
            if value_table[state_after_xo[2]] == 1:
                console.print("   O WINS", style="green")
                o_wins += 1
            break

        state = state_after_xo

# calculate the winrate
console.print(f"o winrate: {o_wins / (x_wins + o_wins)}", style="bold")
