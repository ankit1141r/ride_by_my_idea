# Ride-Hailing Platform Application Package

# Compatibility shim: pkg_resources was removed in Python 3.14
# razorpay and other legacy packages still depend on it
import sys
try:
    import pkg_resources  # noqa: F401
except ModuleNotFoundError:
    import types

    class _DistributionNotFound(Exception):
        pass

    class _VersionConflict(Exception):
        pass

    _pkg = types.ModuleType("pkg_resources")
    _pkg.get_distribution = lambda name: types.SimpleNamespace(version="0.0.0")
    _pkg.require = lambda *a, **kw: None
    _pkg.DistributionNotFound = _DistributionNotFound
    _pkg.VersionConflict = _VersionConflict
    _pkg.working_set = []
    sys.modules["pkg_resources"] = _pkg
