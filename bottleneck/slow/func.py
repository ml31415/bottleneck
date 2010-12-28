
import numpy as np

__all__ = ['median', 'nanmedian', 'nanmean', 'nanvar', 'nanstd', 'nanmin',
           'nanmax', 'nanargmin', 'nanargmax']

def median(arr, axis=None):
    "Slow median function used for unaccelerated ndim/dtype combinations."
    arr = np.asarray(arr)
    y = np.median(arr, axis=axis)
    if y.dtype != arr.dtype:
        if issubclass(arr.dtype.type, np.inexact):
            y = y.astype(arr.dtype)
    return y

def nanmedian(arr, axis=None):
    "Slow nanmedian function used for unaccelerated ndim/dtype combinations."
    arr = np.asarray(arr)
    y = scipy_nanmedian(arr, axis=axis)
    if not hasattr(y, "dtype"):
        if issubclass(arr.dtype.type, np.inexact):
            y = arr.dtype.type(y)
        else:
            y = np.float64(y)
    if y.dtype != arr.dtype:
        if issubclass(arr.dtype.type, np.inexact):
            y = y.astype(arr.dtype)
    if (y.size == 1) and (y.ndim == 0):
        y = y[()]
    return y

def nanmean(arr, axis=None):
    "Slow nanmean function used for unaccelerated ndim/dtype combinations."
    arr = np.asarray(arr)
    y = scipy_nanmean(arr, axis=axis)
    if y.dtype != arr.dtype:
        if issubclass(arr.dtype.type, np.inexact):
            y = y.astype(arr.dtype)
    return y

def nanvar(arr, axis=None, ddof=0):
    "Slow nanvar function used for unaccelerated ndim/dtype combinations."
    arr = np.asarray(arr)
    y = nanstd(arr, axis=axis, ddof=ddof)
    return y * y

def nanstd(arr, axis=None, ddof=0):
    "Slow nanstd function used for unaccelerated ndim/dtype combinations."
    arr = np.asarray(arr)
    if ddof == 0:
        bias = True
    elif ddof == 1:
        bias = False
    else:
        raise ValueError("With NaNs ddof must be 0 or 1.")
    if axis != None:
        # Older versions of scipy can't handle negative axis?
        if axis < 0:
            axis += arr.ndim
        if (axis < 0) or (axis >= arr.ndim):
            raise ValueError, "axis(=%d) out of bounds" % axis
    else:
        # Older versions of scipy choke on axis=None
        arr = arr.ravel()
        axis = 0
    y = scipy_nanstd(arr, axis=axis, bias=bias)
    if y.dtype != arr.dtype:
        if issubclass(arr.dtype.type, np.inexact):
            y = y.astype(arr.dtype)
    return y

def nanmin(arr, axis=None):
    "Slow nanmin function used for unaccelerated ndim/dtype combinations."
    return np.nanmin(arr, axis=axis)

def nanmax(arr, axis=None):
    "Slow nanmax function used for unaccelerated ndim/dtype combinations."
    return np.nanmax(arr, axis=axis)

def nanargmin(arr, axis=None):
    "Slow nanargmin function used for unaccelerated ndim/dtype combinations."
    return np.nanargmin(arr, axis=axis)

def nanargmax(arr, axis=None):
    "Slow nanargmax function used for unaccelerated ndim/dtype combinations."
    return np.nanargmax(arr, axis=axis)

# ---------------------------------------------------------------------------
#
# SciPy
#
# Local copy of scipy.stats functions to avoid (by popular demand) a SciPy
# dependency. The SciPy license is included in the Bottleneck license file,
# which is distributed with Bottleneck.
#
# Code taken from scipy trunk on Dec 16, 2010.
# nanmedian take from scipy trunk on Dec 17, 2010.

def scipy_nanmean(x, axis=0):
    """
    Compute the mean over the given axis ignoring nans.

    Parameters
    ----------
    x : ndarray
        Input array.
    axis : int, optional
        Axis along which the mean is computed. Default is 0, i.e. the
        first axis.

    Returns
    -------
    m : float
        The mean of `x`, ignoring nans.

    See Also
    --------
    nanstd, nanmedian

    Examples
    --------
    >>> from scipy import stats
    >>> a = np.linspace(0, 4, 3)
    >>> a
    array([ 0.,  2.,  4.])
    >>> a[-1] = np.nan
    >>> stats.nanmean(a)
    1.0

    """
    x, axis = _chk_asarray(x,axis)
    x = x.copy()
    Norig = x.shape[axis]
    factor = 1.0-np.sum(np.isnan(x),axis)*1.0/Norig

    x[np.isnan(x)] = 0
    return np.mean(x,axis)/factor

def scipy_nanstd(x, axis=0, bias=False):
    """
    Compute the standard deviation over the given axis, ignoring nans.

    Parameters
    ----------
    x : array_like
        Input array.
    axis : int or None, optional
        Axis along which the standard deviation is computed. Default is 0.
        If None, compute over the whole array `x`.
    bias : bool, optional
        If True, the biased (normalized by N) definition is used. If False
        (default), the unbiased definition is used.

    Returns
    -------
    s : float
        The standard deviation.

    See Also
    --------
    nanmean, nanmedian

    Examples
    --------
    >>> from scipy import stats
    >>> a = np.arange(10, dtype=float)
    >>> a[1:3] = np.nan
    >>> np.std(a)
    nan
    >>> stats.nanstd(a)
    2.9154759474226504
    >>> stats.nanstd(a.reshape(2, 5), axis=1)
    array([ 2.0817,  1.5811])
    >>> stats.nanstd(a.reshape(2, 5), axis=None)
    2.9154759474226504

    """
    x, axis = _chk_asarray(x,axis)
    x = x.copy()
    Norig = x.shape[axis]

    Nnan = np.sum(np.isnan(x),axis)*1.0
    n = Norig - Nnan

    x[np.isnan(x)] = 0.
    m1 = np.sum(x,axis)/n

    if axis:
        d = (x - np.expand_dims(m1, axis))**2.0
    else:
        d = (x - m1)**2.0

    m2 = np.sum(d,axis)-(m1*m1)*Nnan
    if bias:
        m2c = m2 / n
    else:
        m2c = m2 / (n - 1.)
    return np.sqrt(m2c)

def _nanmedian(arr1d):  # This only works on 1d arrays
    """Private function for rank a arrays. Compute the median ignoring Nan.

    Parameters
    ----------
    arr1d : ndarray
        Input array, of rank 1.

    Results
    -------
    m : float
        The median.
    """
    cond = 1-np.isnan(arr1d)
    x = np.sort(np.compress(cond,arr1d,axis=-1))
    if x.size == 0:
        return np.nan
    return np.median(x)

def scipy_nanmedian(x, axis=0):
    """
    Compute the median along the given axis ignoring nan values.

    Parameters
    ----------
    x : array_like
        Input array.
    axis : int, optional
        Axis along which the median is computed. Default is 0, i.e. the
        first axis.

    Returns
    -------
    m : float
        The median of `x` along `axis`.

    See Also
    --------
    nanstd, nanmean

    Examples
    --------
    >>> from scipy import stats
    >>> a = np.array([0, 3, 1, 5, 5, np.nan])
    >>> stats.nanmedian(a)
    array(3.0)

    >>> b = np.array([0, 3, 1, 5, 5, np.nan, 5])
    >>> stats.nanmedian(b)
    array(4.0)

    Example with axis:

    >>> c = np.arange(30.).reshape(5,6)
    >>> idx = np.array([False, False, False, True, False] * 6).reshape(5,6)
    >>> c[idx] = np.nan
    >>> c
    array([[  0.,   1.,   2.,  nan,   4.,   5.],
           [  6.,   7.,  nan,   9.,  10.,  11.],
           [ 12.,  nan,  14.,  15.,  16.,  17.],
           [ nan,  19.,  20.,  21.,  22.,  nan],
           [ 24.,  25.,  26.,  27.,  nan,  29.]])
    >>> stats.nanmedian(c, axis=1)
    array([  2. ,   9. ,  15. ,  20.5,  26. ])

    """
    x, axis = _chk_asarray(x, axis)
    if x.ndim == 0:
        return float(x.item())
    x = x.copy()
    x = np.apply_along_axis(_nanmedian, axis, x)
    if x.ndim == 0:
        x = float(x.item())
    return x

def _chk_asarray(a, axis):
    if axis is None:
        a = np.ravel(a)
        outaxis = 0
    else:
        a = np.asarray(a)
        outaxis = axis
    return a, outaxis