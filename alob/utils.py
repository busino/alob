'''
Alob Project
2016 -2018
Author(s): R.Walker

'''
import cmath
import psutil

def norm(c, v=1):
    '''
    Norm of complex number
    v: optional, can be used to set the absolute value of the new vector
    '''
    return c/abs(c)*v


def rot(c, angle):
    '''
    Rotation of complex number with the angle `angle` counter-clockwise
    '''
    return c*cmath.rect(1, angle)


def elapsed_human(seconds):
    '''Total elapsed time formatted into full time units,
    such as minutes, hours, days, and weeks. Merely
    for human-readable convenience.
    '''
    intervals = (
        ('weeks', 604800),
        ('days', 86400),
        ('hours', 3600),
        ('mins', 60),
    )
    result = []
    for name, count in intervals:
        value = int(seconds // count)
        if value:
            seconds -= value * count
            if value == 1:
                name = name.rstrip('s')
            result.append("{} {}".format(value, name))
    s = ', '.join(result)
    s += ' {:.2f} s'.format(seconds)
    return s

def process_exists(pid):
    '''
    Check if process with PID `pid` is running
    '''
    try:
        psutil.Process(pid)
    except psutil.NoSuchProcess:
        return False
    return True


def kill_process_tree(pid, including_parent=True):
    '''
    kill process with PID `pid` and all its subprocesses
    '''
    parent = psutil.Process(pid)
    children = parent.children(recursive=True)
    for child in children:
        child.kill()
    psutil.wait_procs(children, timeout=5)
    if including_parent:
        parent.kill()
        parent.wait(5)
