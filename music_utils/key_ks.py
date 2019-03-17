# taken from https://gist.github.com/bmcfee/1f66825cef2eb34c839b42dddbad49fd

import numpy as np
import scipy.linalg
import scipy.stats


def ks_key(X):
    """
    Estimate the key from a pitch class distribution

    Parameters
    ----------
    X : np.ndarray, shape=(12,)
        Pitch-class energy distribution.  Need not be normalized

    Returns
    -------
    major : np.ndarray, shape=(12,)
    minor : np.ndarray, shape=(12,)

        For each key (C:maj, ..., B:maj) and (C:min, ..., B:min),
        the correlation score for `X` against that key.
    """
    X = scipy.stats.zscore(X)

    # Coefficients from Krumhansl and Schmuckler
    # as reported here: http://rnhart.net/articles/key-finding/
    major = np.asarray([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
    major = scipy.stats.zscore(major)

    minor = np.asarray([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])
    minor = scipy.stats.zscore(minor)

    # Generate all rotations of major
    major = scipy.linalg.circulant(major)
    minor = scipy.linalg.circulant(minor)

    return major.T.dot(X), minor.T.dot(X)


if __name__ == "__main__":

    random_note_data = [432, 231, 0, 405, 12, 316, 4, 126, 612, 0, 191, 1]
    major, minor = ks_key(random_note_data)
    max_minor = np.argmax(minor)
    max_major = np.argmax(major)

    if minor[max_minor] > major[max_major]:
        max_key = max_minor
        mode = "minor"
    else:
        max_key = max_major
        mode = "major"

    print(major, "\n\n", minor, "\n")
    test = np.asarray([1, 3, 5])
    test2 = np.asarray([2, 3, 5])

    test_mean = [x - np.mean(test) for x in test]
    test2_mean = [x - np.mean(test2) for x in test2]

    nominator = np.dot(test_mean, test2_mean)
    denominator = np.sqrt(np.dot([x ** 2 for x in test_mean], [x ** 2 for x in test2_mean]))

    print(np.dot(test, test2))
