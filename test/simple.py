def print_Fibonacci(N):
    """生成斐波那契数列的前 N 个数字，并输出"""
    if N <= 0:
        print("请输入正整数")
        return
    
    fib = [0, 1]
    for i in range(2, N):
        fib.append(fib[i-1] + fib[i-2])
    
    print(f"斐波那契数列前 {N} 个数字:")
    for i, num in enumerate(fib[:N]):
        print(f"{i+1}: {num}")
