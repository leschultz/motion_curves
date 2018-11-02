def error(x, period):
    n = len(x)
    mean = sum(x)/n
    minus = n-1

    # Compute the covariance between blocks
    valcov = 0.0
    for i in range(0, n):
        for j in range(0, n):
            val = 0.0
            for k in range(0, n):
                val += (x[i]-mean)*(x[j]-mean)
            val /= minus

            valcov += val

    valcov /= n

    # Compute variance of each block
    valvar = 0.0
    for i in range(0, n):
        val = 0.0
        for j in range(0, n):
            val += x[j]**2.0

        val /= n
        val -= mean**2.0

        valvar += val

    valvar /= n

    variance = valvar+valcov
    error = variance**0.5

    return error
