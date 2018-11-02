"""
Project constants.
"""


class Events(object):
    """
    Edx events enum.
    """

    USER_ENROLLED = 'edx.course.enrollment.activated'
    USER_UNENROLLED = 'edx.course.enrollment.deactivated'

    FORUM_COMMENT_CREATED = 'edx.forum.comment.created'
    FORUM_RESPONSE_CREATED = 'edx.forum.response.created'
    FORUM_RESPONSE_VOTED = 'edx.forum.response.voted'
    FORUM_SEARCHED = 'edx.forum.searched'
    FORUM_THREAD_CREATED = 'edx.forum.thread.created'
    FORUM_THREAD_VOTED = 'edx.forum.thread.voted'

    USER_STARTED_VIEW_VIDEO = 'play_video'
    USER_PAUSED_VIEW_VIDEO = 'pause_video'
    USER_FINISHED_WATCH_VIDEO = 'stop_video'

    ENROLLMENT_EVENTS = [USER_ENROLLED,
                         USER_UNENROLLED]

    DISCUSSION_EVENTS = [FORUM_THREAD_CREATED,
                         FORUM_COMMENT_CREATED,
                         FORUM_RESPONSE_CREATED,
                         FORUM_THREAD_VOTED,
                         FORUM_RESPONSE_VOTED]

    VIDEO_VIEW_EVENTS = [USER_STARTED_VIEW_VIDEO,
                         USER_PAUSED_VIEW_VIDEO,
                         USER_FINISHED_WATCH_VIDEO]
