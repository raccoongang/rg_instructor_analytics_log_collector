"""
Project constants.
"""


class Events(object):
    """
    Edx events enum.
    """

    USER_ENROLLED = 'edx.course.enrollment.activated'
    USER_UNENROLLED = 'edx.course.enrollment.deactivated'
    # This event type coincides with this line is not completely, only partially.
    ADMIN_ENROLL_UNENROLL = '/admin/student/courseenrollment/'

    ENROLLMENT_EVENTS = [
        USER_ENROLLED,
        USER_UNENROLLED,
        ADMIN_ENROLL_UNENROLL
    ]
