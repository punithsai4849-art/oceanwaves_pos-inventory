import logging

security_log = logging.getLogger('security')

def log_event(request, event_type, detail='', level='INFO'):
    ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', 'Unknown IP'))
    
    # Check if request has a user and if it's authenticated
    if hasattr(request, 'user') and request.user.is_authenticated:
        user_display = request.user.username
    else:
        user_display = 'Anonymous'

    msg = f"[{event_type}] user={user_display} ip={ip} detail={detail}"
    
    log_func = getattr(security_log, level.lower(), security_log.info)
    log_func(msg)
