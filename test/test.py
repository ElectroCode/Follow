def test():
    """test routine"""
    import sys

    files = [ (path, Follow(path)) for path in sys.argv[1:] ]

    if not files:
        print "Usage: follow.py files ...."
        sys.exit(1)

    inisleep = 0.25
    sleep = inisleep
    while True:
        lines = False
        for fname, filep in files:
            line = filep.readline()
            if line:
                lines = True
                sys.stdout.write("%s: %s" % (fname, line))
                sleep = inisleep
        if not lines:
            time.sleep(sleep)
            sleep *= 2
            if sleep > 10:
                sleep = inisleep

if __name__ == "__main__":
    test()
