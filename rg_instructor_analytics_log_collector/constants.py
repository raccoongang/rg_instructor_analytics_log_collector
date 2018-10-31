"""
Project constants.
"""


class Events(object):
    """
    Edx events enum.
    """

    USER_ENROLLED = 'edx.course.enrollment.activated'
    USER_UNENROLLED = 'edx.course.enrollment.deactivated'
    USER_STARTED_VIEW_VIDEO = 'pause_video'
    USER_FINISHED_WATCH_VIDEO = 'stop_video'

    ENROLLMENT_EVENTS = [USER_ENROLLED, USER_UNENROLLED]
    VIDEO_VIEW_EVENTS = [USER_STARTED_VIEW_VIDEO, USER_FINISHED_WATCH_VIDEO]
