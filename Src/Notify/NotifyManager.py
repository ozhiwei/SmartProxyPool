
NOTIFY_LIST = [
    "AFTER_SETTING_CHANGE"
]

NOTIFY_HANDLER = {}

NOTIFY_EVENT = {}
for name in NOTIFY_LIST:
    NOTIFY_EVENT[name] = name
    NOTIFY_HANDLER[name] = []

def register_event(name, handler):
    handler_list = NOTIFY_HANDLER[name]
    handler_list.append(handler)

def dispatch_event(name, **kwargs):
    if name in NOTIFY_HANDLER:
        try:
            handler_list = NOTIFY_HANDLER[name]
            for handler in handler_list:
                handler(**kwargs)
        except Exception as e:
            # tmp handle
            # print("dispatch_notify err: {name}, {e}".format(name=name, e=e))
            pass
