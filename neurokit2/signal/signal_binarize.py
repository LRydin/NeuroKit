# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import sklearn.mixture





def signal_binarize(signal, method="threshold", threshold="auto"):
    """Binarize a continuous signal.

    Convert a continuous signal into zeros and ones depending on a given threshold.

    Parameters
    ----------
    signal : list, array or Series
        The signal channel in the form of a vector of values.
    threshold : float
        The threshold value by which to select the events. If "auto", takes the value between the max and the min.

    Returns
    -------
    list
        A list or array depending on the type passed.

    Examples
    --------
    >>> import numpy as np
    >>> import pandas as pd
    >>> import neurokit2 as nk
    >>>
    >>> signal = np.cos(np.linspace(start=0, stop=20, num=1000))
    >>> binary = nk.signal_binarize(signal)
    >>> pd.DataFrame({"Raw": signal, "Binary": binary}).plot()
    """

    # Return appropriate type
    if isinstance(signal, list):
        binary = _signal_binarize(np.array(signal), method=method, threshold=threshold)
        signal = list(binary)
    elif isinstance(signal, pd.Series):
        binary = _signal_binarize(signal.values, method=method, threshold=threshold)
        signal[:] = binary
    else:
        signal = _signal_binarize(signal, method=method, threshold=threshold)

    return signal



def _signal_binarize(signal, method="threshold", threshold="auto"):
    method = method.lower()  # remove capitalised letters
    if method == "threshold":
        binary = _signal_binarize_threshold(signal, threshold=threshold)
    elif method == "mixture":
        binary = _signal_binarize_mixture(signal, threshold=threshold)
    else:
        raise ValueError("NeuroKit error: signal_binarize(): 'method' should be "
                         "one of 'threshold' or 'mixture'.")
    return binary



# =============================================================================
# Methods
# =============================================================================

def _signal_binarize_threshold(signal, threshold="auto"):
    if threshold == "auto":
        threshold = np.mean([np.max(signal), np.min(signal)])

    binary = np.zeros(len(signal))
    binary[signal > threshold] = 1
    return binary



def _signal_binarize_mixture(signal, threshold="auto"):
    if threshold == "auto":
        threshold = 0.5

    # fit a Gaussian Mixture Model with two components
    clf = sklearn.mixture.GaussianMixture(n_components=2, random_state=333)
    clf = clf.fit(signal.reshape(-1, 1))

    # Get predicted probabilities
    probability = clf.predict_proba(signal.reshape(-1, 1))[:, np.argmax(clf.means_[:, 0])]

    binary = np.zeros(len(signal))
    binary[probability >= threshold] = 1
    return binary
