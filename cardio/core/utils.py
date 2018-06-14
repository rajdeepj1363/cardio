"""Miscellaneous ECG Batch utils."""

import functools

import pint
import numpy as np
from sklearn.preprocessing import LabelBinarizer as LB


UNIT_REGISTRY = pint.UnitRegistry()


def get_units_conversion_factor(old_units, new_units):
    """Return a multiplicative factor to convert a measured quantity from old
    to new units.

    Parameters
    ----------
    old_units : str
        Current units in SI format.
    new_units : str
        Target units in SI format.

    Returns
    -------
    factor : float
        A factor to convert quantities between units.
    """
    try:  # pint exceptions are wrapped with ValueError exceptions because they don't implement __repr__ method
        factor = UNIT_REGISTRY(old_units).to(new_units).magnitude
    except Exception as error:
        raise ValueError(error.__class__.__name__ + ": " + str(error))
    return factor


def partialmethod(func, *frozen_args, **frozen_kwargs):
    """Wrap a method with partial application of given positional and keyword
    arguments.

    Parameters
    ----------
    func : callable
        A method to wrap.
    frozen_args : misc
        Fixed positional arguments.
    frozen_kwargs : misc
        Fixed keyword arguments.

    Returns
    -------
    method : callable
        Wrapped method.
    """
    @functools.wraps(func)
    def method(self, *args, **kwargs):
        """Wrapped method."""
        return func(self, *frozen_args, *args, **frozen_kwargs, **kwargs)
    return method


class LabelBinarizer(LB):
    """Encode categorical features using a one-hot scheme.

    Unlike ``sklearn.preprocessing.LabelBinarizer``, each label will be
    encoded using ``n_classes`` numbers even for binary problems.
    """
    # pylint: disable=invalid-name

    def transform(self, y):
        """Transform ``y`` using one-hot encoding.

        Parameters
        ----------
        y : 1-D ndarray of shape ``[n_samples,]``
            Class labels.

        Returns
        -------
        Y : 2-D ndarray of shape ``[n_samples, n_classes]``
            One-hot encoded labels.
        """
        Y = super().transform(y)
        if len(self.classes_) == 1:
            Y = 1 - Y  # pylint: disable=redefined-variable-type
        if len(self.classes_) == 2:
            Y = np.hstack((1 - Y, Y))
        return Y

    def inverse_transform(self, Y, threshold=None):
        """Transform one-hot encoded labels back to class labels.

        Parameters
        ----------
        Y : 2-D ndarray of shape ``[n_samples, n_classes]``
            One-hot encoded labels.
        threshold : float, optional
            The threshold used in the binary and multi-label cases. If
            ``None``, it is assumed to be half way between ``neg_label`` and
            ``pos_label``.

        Returns
        -------
        y : 1-D ndarray of shape ``[n_samples,]``
            Class labels.
        """
        if len(self.classes_) == 1:
            y = super().inverse_transform(1 - Y, threshold)
        elif len(self.classes_) == 2:
            y = super().inverse_transform(Y[:, 1], threshold)
        else:
            y = super().inverse_transform(Y, threshold)
        return y
