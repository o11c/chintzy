import chintzy

for lang in chintzy.languages:
    exec('''
def {lang}_std_modules():
    for s in chintzy.{lang}_standards:
        yield getattr(__import__('chintzy.std', fromlist=[s]), s)
'''.format(lang=lang))
del lang

def all_std_modules():
    for lang in chintzy.languages:
        for m in globals()[lang + '_std_modules']():
            yield m

def named_std_module(s):
    assert s.isalnum()
    return getattr(__import__('chintzy.std', fromlist=[s]), s)
