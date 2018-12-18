NOTIFY_HASH = {}

def register_notify(name, handler):
    NOTIFY_HASH[name] = handler

def dispatch_notify(name, **kwargs):
    if name in NOTIFY_HASH:
        try:
            func = NOTIFY_HASH[name]
            func(**kwargs)
        except Exception as e:
            # tmp handle
            print("dispatch_notify err: {name}, {e}".format(name=name, e=e.message))
