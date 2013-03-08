import logging
class NoParsingFilter(logging.Filter):
    def filter(self, record):
        try:
            success = not record.getMessage().index('requests.packages.urllib3') > -1
        except:
            success = False
        return not success

