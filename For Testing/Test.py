def fact(n):
    if n <= 1:
        return 1
    else:
        print(n - 1, n)
        return fact(n - 1) * n


print(fact(5))
print(fact(10))
