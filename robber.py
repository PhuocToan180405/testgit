def rob(nums):
    n = len(nums)
    if n == 0:
        return 0
    if n == 1:
        return nums[0]

    memo = {}

    def dfs(i):
        if i in memo:           # nếu đã tính thì trả về
            return memo[i]
        if i == 0:
            memo[i] = nums[0]
        elif i == 1:
            memo[i] = max(nums[0], nums[1])
        else:
            memo[i] = max(dfs(i-1), dfs(i-2) + nums[i])
        return memo[i]

    return dfs(n-1)


# Ví dụ test
houses = [2, 7, 9, 3, 1]
print("Số tiền tối đa có thể trộm:", rob(houses))  # Kết quả: 12
