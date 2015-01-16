name = __name__.split('.')[-2]
name_title = name.title()
name_snake = name + '_'

def init_me():
    modname = 'chintzy._std.%s' % name
    mod = __import__(modname, fromlist=['bogus'])
    for k, v in mod.__dict__.items():
        if k.startswith('_'):
            continue
        globals()[k] = v
init_me()
del init_me
