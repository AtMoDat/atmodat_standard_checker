import numpy as np

def check_global_attr_type(ds, attr, attr_type, status):
    """
    Checks globals attribute values in a NetCDF Dataset and returns integer regarding
    whether the `attr` matches `attr_type`.

    Note: Problems may occur with numpy types (int32, int 64, ...)

    :param ds: netCDF4 Dataset object
    :param attr: global attribute name [string]
    :param attr_type: a numpy type [string]
    :param status: status (mandatory or sth. else) [string]
    :return: Integer (0: not found; 1: found (incorrect type); 2: found and correct type.
    """
    if status == "mandatory" and not attr in ds.ncattrs():
        return 0

    global_attr = getattr(ds, attr)

    if np.dtype(type(global_attr)) != np.dtype(attr_type):
        return 1

    return 2


def check_global_attr_ISO8601(ds, attr):
    """
    Checks globals attribute values in a NetCDF Dataset and returns integer regarding
    whether the `attr` matches ISO8601 format.

    :param ds: netCDF4 Dataset object
    :param attr: global attribute name [string]
    :return: Integer (0: incorrect format; 1: correct format).
    """
    global_attr = getattr(ds, attr)

    if np.dtype(type(global_attr)) != np.dtype(attr_type):
        return 1

    return 2
