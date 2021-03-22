"""
Please excuse the function's complexity, I may reduce it later or you can.
Note: 'logger.error' can be replaced with 'print'
"""


def tryExceptDecorator(errorMsg=None, returnValue=None, stackTrace: bool = False, checkIfDebug: bool = False):
    """
    try catches decorated function, both sync and async funtions
    :param errorMsg: error msg to be displayed if exception raised
    :param returnValue: value to be returned if exceptin raised
    :param stackTrace: if stackTrace is true, appends traceback in passesd function's
        global variable named 'stackTrace' if it exists
    :param checkIfDebug: run this function only when not debugging (DEBUG=False in settings)
    """

    def intermediate(func):
        def wrapper(*args, **kwargs):
            if checkIfDebug and settings.DEBUG:
                # not handling when debug = True
                return func(*args, **kwargs)

            if not asyncio.iscoroutinefunction(func):
                try:
                    return func(*args, **kwargs)
                except Exception as ex:
                    if errorMsg:
                        logger.error(errorMsg)
                    if stackTrace and "stackTrace" in func.__globals__:
                        func.__globals__["stackTrace"].append(traceback.format_exc())
                    logger.error(traceback.print_exc())
                    try:
                        args, kwargs = checkJsonSerializibilityForArgsKwargs(args, kwargs)
                        logger.error("For " + json.dumps({"args": args, "kwargs": kwargs}))
                    except (TypeError, OverflowError):
                        pass
                    logger.error("Error %s", str(ex))
                    return returnValue
            else:

                async def temp(argz, kwargz):
                    try:
                        return await func(*args, **kwargs)
                    except Exception as ex:
                        if errorMsg:
                            logger.error(errorMsg)
                        if stackTrace and "stackTrace" in func.__globals__:
                            func.__globals__["stackTrace"].append(traceback.format_exc())
                        logger.error(traceback.print_exc())
                        try:
                            # remove args of type class i.e. self, funn()
                            argz, kwargz = checkJsonSerializibilityForArgsKwargs(argz, kwargz)
                            logger.error("For " + json.dumps({"args": argz, "kwargs": kwargz}))
                        except (TypeError, OverflowError):
                            pass
                        logger.error("Error %s", str(ex))
                        return returnValue

                return temp(args, kwargs)

        return wrapper

    return intermediate


def checkJsonSerializibility(x):
    try:
        json.dumps(x)
        return True
    except Exception:
        return False


def checkJsonSerializibilityForArgsKwargs(args, kwargs):
    args = tuple(filter(checkJsonSerializibility, args))
    kwargs = {k: v for k, v in kwargs.items() if checkJsonSerializibility(v)}
    return args, kwargs


