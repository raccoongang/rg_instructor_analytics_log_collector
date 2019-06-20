"""
Utility functionality to test pipelines.
"""
import json


class TestRecord(object):
    """
    Dummy `Record` class.
    """
    LOG_TIME = 123
    USER_ID = 123
    EVENT_TYPE = "test_event_type"
    COURSE_ID = 456

    def __init__(self,
                 log_time=LOG_TIME,
                 user_id=USER_ID,
                 event_type=EVENT_TYPE,
                 course_id=COURSE_ID):
        self.log_time = log_time
        self.log_message = json.dumps({"event": json.dumps({"test_key": "test_value"}),
                                      "context": {"user_id": user_id,
                                                  "course_id": course_id}})
        self.message_type = event_type

    def log_message(self):
        return self.log_message
