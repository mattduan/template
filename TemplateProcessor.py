"""
The template processor class interface.
"""

__version__='$Revision: 11 $'[11:-2]
__author__ = "Duan Guoqiang (mattgduan@gmail.com)"



# template imports
from TemplateException import TemplateException


##############################################
#          CLASS: TemplateProcessor
##############################################

class TemplateProcessor:
    """ Fill the template with data and process it.

        This class is the abstract class of all template processor classes.
    """

    def __init__(self):
        """ Constructor.
        """
        pass
    
    def set(self, var, value):
        """ Associate a value with top-level template variable or loop.
        """
        raise TemplateException, "TemplateProcessor.set() method must be " + \
                                 "overwrited by subclass for model specific" + \
                                 "data structures!"
        
    def setdict(self, dict):
        """ Associate dictionary values with top-level template variables.
        """
        raise TemplateException, "TemplateProcessor.setdict() method must be " + \
                                 "overwrited by subclass for model specific" + \
                                 "data structures!"

    def reset(self, keep_data=0):
        """ Reset the template data.
        """
        raise TemplateException, "TemplateProcessor.reset() method must be " + \
                                 "overwrited by subclass for model specific" + \
                                 "data structures!"

    def process(self, template, part=None):
        """ Process a compiled template. Return the result as string.
        """
        raise TemplateException, "TemplateProcessor.process() method must be " + \
                                 "overwrited by subclass for model specific" + \
                                 "template object!"

