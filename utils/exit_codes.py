from .structures import LookupDict

_codes = {

    # Informational.
    0: ('OK', ),
    1: ('abnormal termination',),
    2: ('major error',),
    62: ('illegal option',),
    127: ('command not found',),
    132: ('SIGILL',),
    133: ('SIGTRAP',),
    134: ('SIGABRT',),
    136: ('SIGFPE',),
    137: ('Out of memory',),
    138: ('SIGBUS',),
    139: ('Segmentation Fault',),
    158: ('SIGXCPUt',),
    152: ('SIGXCPUt',),
    153: ('SIGXFSZ',),
    159: ('SIGXFSZ',),
    999: ('Fuzzer Exception',),
}

codes = LookupDict(name='exit_codes')


def _init():
    for code, titles in _codes.items():
        for title in titles:
            setattr(codes, title, code)
            if not title.startswith(('\\', '/')):
                setattr(codes, title.upper(), code)

    def doc(code):
        names = ', '.join('``%s``' % n for n in _codes[code])
        return '* %d: %s' % (code, names)

    global __doc__
    __doc__ = (__doc__ + '\n' +
               '\n'.join(doc(code) for code in sorted(_codes))
               if __doc__ is not None else None)


_init()
