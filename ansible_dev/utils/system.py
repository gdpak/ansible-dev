import os
import stat

def is_executable(path):
    '''is the given path executable?

    Limitations:
    * Does not account for FSACLs.
    * Most times we really want to know "Can the current user execute this
      file"  This function does not tell us that, only if an execute bit is set.
    '''
    # These are all bitfields so first bitwise-or all the permissions we're
    # looking for, then bitwise-and with the file's mode to determine if any
    # execute bits are set.
    return ((stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH) & os.stat(path)[stat.ST_MODE])

def get_bin_path(arg, required=False, opt_dirs=None):
    '''
    find system executable in PATH.
    Optional arguments:
       - required:  if executable is not found and required is true it produces an Exception
       - opt_dirs:  optional list of directories to search in addition to PATH
    if found return full path; otherwise return None
    '''
    opt_dirs = [] if opt_dirs is None else opt_dirs

    sbin_paths = ['/sbin', '/usr/sbin', '/usr/local/sbin']
    paths = []
    for d in opt_dirs:
        if d is not None and os.path.exists(d):
            paths.append(d)
    paths += os.environ.get('PATH', '').split(os.pathsep)
    bin_path = None
    # mangle PATH to include /sbin dirs
    for p in sbin_paths:
        if p not in paths and os.path.exists(p):
            paths.append(p)
    for d in paths:
        if not d:
            continue
        path = os.path.join(d, arg)
        if os.path.exists(path) and not os.path.isdir(path) and is_executable(path):
            bin_path = path
            break
    if required and bin_path is None:
        raise ValueError('Failed to find required executable %s in paths: %s' % (arg, os.pathsep.join(paths)))

    return bin_path
