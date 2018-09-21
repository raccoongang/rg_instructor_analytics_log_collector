"""
Project constants.
"""


class Events(object):
    """
    Edx events enum.
    """

    USER_ENROLLED = 'edx.course.enrollment.activated'
    USER_UNENROLLED = 'edx.course.enrollment.deactivated'

    ENROLLMENT_EVENTS = [USER_ENROLLED, USER_UNENROLLED]
