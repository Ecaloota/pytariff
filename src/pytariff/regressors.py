from typing import Literal

import numpy as np
from numpy.typing import ArrayLike
from scipy.interpolate import interp1d
from sklearn.base import BaseEstimator, RegressorMixin


class MovingAverageRegressor(BaseEstimator, RegressorMixin):
    def __init__(
        self, window_size: int = 5, mode: Literal["full", "same", "valid"] = "same"
    ) -> None:
        self.window_size = window_size
        self.mode = mode
        super().__init__()

    def fit(self, X: ArrayLike, y: ArrayLike) -> "MovingAverageRegressor":
        """Fit the provided data in preparation for MovingAverage regression. X is expected to
        be a sorted array, but this is not enforced. X and y must have the same dimensionality."""

        self.fitted_ = True
        self.index_ = np.asarray(X)
        self.vals_ = np.asarray(y)

        if not self.index_.shape[0] == self.vals_.shape[0]:
            raise ValueError("X and y must have the same shape")

        return self

    def predict(self, X: ArrayLike, y: ArrayLike | None = None) -> ArrayLike:
        """Performs convolution over fitted data using a MovingAverage kernel, then evaluates
        a piecewise linear interpolation over the convolution at each point x in X.

        Points in X outside the range defined by self.index_ are filled by the following rules:
        1. x < self.index_[0] => x = self.index_[0]
        2. x > self.index_[-1] => x = self.index_[-1]

        Returns an 1D array with dimension equal to the dimension of X.
        """

        if not hasattr(self, "fitted_"):
            raise AttributeError(
                "Regressor must be trained before prediction can be performed"
            )

        if np.any(self.index_ == np.nan):
            raise ValueError(
                "Fit data cannot contain NaN values for MovingAverage regression"
            )

        # the alternative would be to zip the index_ and vals_, then sort and unzip
        # but I think it's better to be explicit about the requirement here
        if not np.all(np.diff(self.index_.ravel() > 0)):
            raise ValueError("Fit data must be sorted for MovingAverage regression")

        kernel = np.ones(self.window_size) / self.window_size
        values = np.convolve(self.vals_, kernel, mode=self.mode)
        new_values = np.interp(np.asarray(X).ravel(), self.index_.ravel(), values)

        return new_values


class PiecewiseConstantRegressor(BaseEstimator, RegressorMixin):
    def fit(self, X: ArrayLike, y: ArrayLike) -> "PiecewiseConstantRegressor":
        """Fit the provided data in preparation for PiecewiseConstant regression. X is expected to
        be a sorted array, but this is not enforced. X and y must have the same dimensionality."""

        self.fitted_ = True
        self.index_ = np.asarray(X)
        self.vals_ = np.asarray(y)

        if not self.index_.shape[0] == self.vals_.shape[0]:
            raise ValueError("X and y must have the same shape")

        return self

    def predict(self, X: ArrayLike, y: ArrayLike | None = None) -> ArrayLike:
        """Evaluates a piecewise linear interpolation at each point x in X.

        Points in X outside the range defined by self.index_ are filled by the following rules:
        1. x < self.index_[0] => x = self.index_[0]
        2. x > self.index_[-1] => x = self.index_[-1]

        Returns an 1D array with dimension equal to the dimension of X.
        """

        if not hasattr(self, "fitted_"):
            raise AttributeError(
                "Regressor must be trained before prediction can be performed"
            )

        if np.any(self.index_ == np.nan):
            raise ValueError(
                "Fit data cannot contain NaN values for PiecewiseConstant regression"
            )

        # the alternative would be to zip the index_ and vals_, then sort and unzip
        # but I think it's better to be explicit about the requirement here
        if not np.all(np.diff(self.index_.ravel()) > 0):
            raise ValueError("Fit data must be sorted for PiecewiseConstant regression")

        # NOTE interp1d is considered legacy, but is much more intuitive than its recommended
        # replacement `make_inter_spline` when we have specific requirements for the boundary
        # conditions that aren't clearly defined by the nature of their derivatives.
        # `previous` means we perform piecewise extrapolation using the last known value
        #  `fill_value` determines how we extrapolate outside the bounds of self.index_
        interp = interp1d(
            self.index_.ravel(),
            self.vals_,
            kind="previous",
            fill_value=(self.vals_[0], self.vals_[-1]),
            bounds_error=False,
        )
        values = interp(np.asarray(X).ravel())

        return values
