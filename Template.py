"""
The template class. It converts a template file into an object and
compile it if necessary. The unique filename is the class identity.
The modified-time of it can keep the template up-to-date. The
template can just be a string, in this case, the MD5 of the string
is used to identify the template. It will never need to update.
"""

__version__='$Revision: 11 $'[11:-2]
__author__ = "Duan Guoqiang (mattgduan@gmail.com)"

# standard Python imports.
import os
import os.path


# template imports
from TemplateException import TemplateException


##############################################
#              CLASS: Template
##############################################

class Template:
    """ This class represents a compiled template.

        This class is the abstract class for all templates.
    """
    
    def __init__(self, file, content=None ):
        """ Constructor.
            @hidden
        """
        self._file = file
        self._content = content
        self._mtime = None

        if not file:
            if not content:
                raise TemplateException, "Template: file or content must be specified"
            # template compiled from a string
            return

        # Save modifitcation time of the main template file.        
        if os.path.isfile(file):
            self._mtime = os.path.getmtime(file)
        else:
            raise TemplateException, "Template: file does not exist: '%s'" % file


    def is_uptodate(self, compile_params=None):
        """ Check whether the compiled template is uptodate.
        """
        if not self._file:
            # TEMPLATE COMPILED FROM A STRING
            return 1
        
        if not (os.path.isfile(self._file) and \
                self._mtime == os.path.getmtime(self._file)):
            # TEMPLATE: NOT UPTODATE
            return 0
        
        return 1

    def getid(self):
        """ Return the identification of this template, either
        filename or md5 of content.
        """
        if self._file:
            return self._file
        else:
            import md5
            return md5.new(self._content).hexdigest()

