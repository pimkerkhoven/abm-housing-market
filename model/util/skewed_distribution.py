from scipy.stats import skewnorm


def skewed_distribution(mean, median, size=1, sigma=None):
    # Note: When sigma is None, sigma will always equal (mean - median) for now,
    #  so skew is always -3 or + 3
    if sigma is None:
        sigma = abs(0.15 * mean)  # math.sqrt((median - mean) ** 2)

    skew = 3
    if not sigma == 0:
        skew = 3 * (mean - median) / sigma

    r = skewnorm.rvs(skew, loc=mean, size=size, scale=sigma)
    if size == 1:
        return r[0]

    return r
