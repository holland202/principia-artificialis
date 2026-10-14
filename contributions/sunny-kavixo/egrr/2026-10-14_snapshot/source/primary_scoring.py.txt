"""Provisional EGRR primary ratio guard; NOT a frozen decision rule."""
import math

class PrimaryScoringError(ValueError):
    """Invalid numerical input to the primary comparison."""


def paired_relative_improvement(covariance_mse, magnitude_mse):
    """Return 1 - covariance_mse/magnitude_mse, or fail closed."""
    try:
        cov = float(covariance_mse)
        mag = float(magnitude_mse)
    except (TypeError, ValueError, OverflowError) as exc:
        raise PrimaryScoringError("invalid MSE input") from exc

    if not math.isfinite(cov) or not math.isfinite(mag):
        raise PrimaryScoringError("non-finite MSE")
    if cov < 0 or mag < 0:
        raise PrimaryScoringError("negative MSE")

    # PROVISIONAL: must be justified and approved before registration.
    if mag <= 1e-12:
        raise PrimaryScoringError("zero or near-zero magnitude MSE")

    ratio = cov / mag
    improvement = 1.0 - ratio
    if not math.isfinite(ratio) or not math.isfinite(improvement):
        raise PrimaryScoringError("non-finite improvement ratio")

    return improvement
