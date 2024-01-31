# credit to dave

"""
constrains: 
1. int value in arr is between 1 and 9, and max arr length is 9
2. int values in the array are unique with no duplicate
3. checking if any triplet in arr sum to 15

logic:
1. sort the array
2. create a dict of remainder of 15 subtracted by each value in arr 
    -> let 3 values of combination be x, y, z 
    -> x + y + z = 15, y + z = 15 - x
    -> remainder would be 15 - x | y + z
3. create a dict of existence of each value in arr
4. iterate through arr, for each value i, subtract remainder[i] by other values in arr (arr[j]) -> new remainder (15 - x - y) (subtract previous remainder y + z | 15 - x by y check if z exist)
    -> check if new remainder is in the range of (1-9) 
    -> check if new remainder is not equal to i or j
    -> check if new remainder exist in arr
    -> if all true, return true
5. return false if no triplet sum to 15
"""


def check_if_any_array_triplet_sum_to_15(arr: list[int]) -> bool:
    # setup
    arr.sort()
    remainder = dict()
    exist = dict()

    # create exist dict
    for i in range(1, 10):
        exist[i] = False

    # create remainder dict 15 - x
    for i in arr:
        remainder[i] = 15 - i
        exist[i] = True

    # iterate through arr
    for i in arr:
        re_val = remainder[i]
        temp_arr = arr.copy()
        temp_arr.remove(i)
        for j in temp_arr:
            # 15 - x - y = z
            new_re_val = re_val - j

            # check if new_re_val is in range of (1-9)
            if new_re_val <= 0 or new_re_val >= 10:
                continue

            # check if new_re_val is not equal to i or j
            if new_re_val == j or new_re_val == i:
                continue

            # check if z exist
            if exist[new_re_val]:
                print(i, j, new_re_val)
                return True
    return False
