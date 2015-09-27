import re

UID = 1
RID = 2
TRAINID = 3

pattern_rid = re.compile("^[0-9]+$")
pattern_trainid = re.compile("^[0-9][A-Za-z][0-9][0-9]$")

DEFAULT_GRANULARITY="day"

def validate_tiploc(code):
    return code

def api_bool(value):
    if value in ('y', 't', 'true', 'True', 'yes', '1'):
        return True
    else:
        return False

def validate_service(service):
    return service

def service_type(s):
    """Returns whether a service is a UID, a RID or a trainId"""
    s = s.strip()
    if pattern_rid.match(s):
        return RID
    if pattern_trainid.match(s):
        return TRAINID
    return UID

def validated_granularity(value):
    GRANUlARITIES = [
        "day",
        "week",
        "month"
    ]
    
    value = value.toLower()
    if not value in GRANUlARITIES:
        raise Exception("Granularity is not valid. Given: " + str(value))

    return value
