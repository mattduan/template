"""
All template exception classes.
"""

__version__='$Revision: 53 $'[11:-2]
__author__ = "Duan Guoqiang (mattgduan@gmail.com)"



##############################################
#                EXCEPTIONS
##############################################   
class TemplateException(Exception):
    """ Fatal exception. Raised on runtime or template syntax errors.
    """

    def __init__(self, error):
        """ Constructor.
            @hidden
        """
        Exception.__init__(self, "%s" % error)


class PrecompiledError(Exception):
    """ This exception is _PRIVATE_ and non fatal.
        @hidden
    """

    def __init__(self, template):
        """ Constructor.
            @hidden
        """
        Exception.__init__(self, template)
        
class NotImplementedException(Exception):
    """ Fatal exception. Raised on runtime or template syntax errors.
    """

    def __init__(self, error):
        """ Constructor.
            @hidden
        """
        Exception.__init__(self, "%s" % error)
