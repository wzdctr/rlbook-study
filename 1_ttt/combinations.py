import numpy as np
import itertools


def is_win(state, symbols=(1, 2)):
    if (state == 0).all():
        return False

    for s in symbols:
        sym_state = state == s
        if (
            3 in np.sum(sym_state, axis=0)
            or 3 in np.sum(sym_state, axis=1)
            or np.trace(sym_state) == 3
            or np.trace(np.rot90(sym_state)) == 3
        ):
            return True
    return False


def check_duplicate(state):
    rotational_transforms = [
        lambda x: x,
        lambda x: np.rot90(x, 1),
        lambda x: np.rot90(x, 2),
        lambda x: np.rot90(x, 3),
    ]

    reflection_transforms = [
        lambda x: x,
        lambda x: np.fliplr(x),
        lambda x: np.flipud(x),
    ]

    transforms = list(itertools.product(rotational_transforms, reflection_transforms))

    for rotate, reflect in transforms:
        transformed_state = rotate(reflect(state))
        transformed_state_str = "".join(
            transformed_state.astype(int).astype(str).flatten()
        )
        if transformed_state_str in all_states:
            return True
    return False


def generate_boards(state, all_states, step=0):
    if step == 9 or is_win(state):
        return  # go to backtrack

    move = step % 2 + 1

    unplayed = np.argwhere(state == 0)
    for cell in unplayed:
        state[cell[0], cell[1]] = move
        if not check_duplicate(state):
            state_str = "".join(state.astype(int).astype(str).flatten())
            print(f"unique state found: {state_str}")
            all_states.add(state_str)
        generate_boards(state, all_states, step + 1)
        # if above function returned, proceed to backtrack
        state[cell[0], cell[1]] = 0


initial_state = np.zeros((3, 3), dtype=int)
all_states = set()

generate_boards(initial_state, all_states)
print(f"total unique states: {len(all_states)}")
