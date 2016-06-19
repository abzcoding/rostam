from datetime import datetime


class TimeEntry(object):
    def __init__(self, container_id, timestamp=None, build_output=None, build_result="succeed"):
        self.container_id = int(container_id)
        if timestamp is None:
            self.timestamp = datetime.now()
        else:
            self.timestamp = timestamp
        if build_output is None:
            build_output = ""
        self.build_output = build_output
        self.build_result = build_result
