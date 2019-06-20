"""
Utility functionality to test pipelines.
"""
import json


class TestRecord(object):
    """
    Dummy `Record` class.

    Encapsulates data fields for all pipeline.
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
        # TODO make this class pipeline-specific (pipeline type dependent)
        #  since some pipelines  do not use json data
        #  e.g. discussion pipeline
        self.log_message = json.dumps({"event": json.dumps({"commentable_id": "test_commentable_id",
                                                            "id": "test_id",
                                                            "thread_type": "test_thread_type",
                                                            "category_id": "test_category_id"}),
                                      "context": {"user_id": user_id,
                                                  "course_id": course_id}})
        self.message_type = event_type

    def log_message(self):
        return self.log_message
