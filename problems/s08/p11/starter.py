def sort_desc(nums):
    for i in range(0, len(nums) - 1, 1):
        pos = i
        for j in range(i + 1, len(nums), 1):
            if ____:
                pos = j
        nums[i], nums[pos] = ____
    return nums
