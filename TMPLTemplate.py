"""
This template engine (tmpl) is based on Tomas Styblo's htmltmpl version
1.22 (http://htmltmpl.sourceforge.net/). The templating language was
borrowed from Perl package HTML::Template. The language detail can be
found at http://sam.tregar.com/html_template.html.
"""

__version__='$Revision: 3193 $'[11:-2]

# imported modules of the standard Python library.
import os
import os.path
import copy
import logging

# template imports
from Template import Template
from TemplateException import TemplateException


##############################################
#              CLASS: Template               #
##############################################

class TMPLTemplate( Template ):
    """ This class represents a compiled template.

        This class provides storage and methods for the compiled template
        and associated metadata. It's serialized by pickle if we need to
        save the compiled template to disk in a precompiled form.

        You should never instantiate this class directly. Always use the
        <em>TemplateManager</em> or <em>TemplateCompiler</em> classes to
        create the instances of this class.

        The only method which you can directly use is the <em>is_uptodate</em>
        method.
    """

    def __init__(self, file, content=None, logger=None):
        self._file = file
        self._content = content
        self._mtime = None

        self._version = __version__
        self._tokens = None
        self._compile_params = None
        self._include_mtimes = {}
        self._logger = logger

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
        
    def init(self, version, include_files, tokens, compile_params,
             logger=None):
        """ Initialization.
            @hidden
        """
        self._version = version
        self._tokens = tokens
        self._compile_params = compile_params
        self._logger = logger
        self._include_mtimes = {}

        # Save modificaton times of all included template files.
        for inc_file in include_files:
            if os.path.isfile(inc_file):
                self._include_mtimes[inc_file] = os.path.getmtime(inc_file)
            else:
                raise TemplateException, "Template: file does not exist: '%s'"\
                                         % inc_file
            
        self.debug("NEW TEMPLATE CREATED")

    def is_uptodate(self, compile_params=None):
        """ Check whether the compiled template is uptodate.

            Return true if this compiled template is uptodate.
            Return false, if the template source file was changed on the
            disk since it was compiled.
            Works by comparison of modification times.
            Also takes modification times of all included templates
            into account.

            @header is_uptodate(compile_params=None)
            @return True if the template is uptodate, false otherwise.

            @param compile_params Only for internal use.
            Do not use this optional parameter. It's intended only for
            internal use by the <em>TemplateManager</em>.
        """
        if not self._file:
            self.debug("TEMPLATE COMPILED FROM A STRING")
            return 1
        
        if self._version != __version__:
            self.debug("TEMPLATE: VERSION NOT UPTODATE")
            return 0

        if compile_params != None and compile_params != self._compile_params:
            self.debug("TEMPLATE: DIFFERENT COMPILATION PARAMS")
            return 0
    
        # Check modification times of the main template and all included
        # templates. If the included template no longer exists, then
        # the problem will be resolved when the template is recompiled.

        # Main template file.
        if not (os.path.isfile(self._file) and \
                self._mtime == os.path.getmtime(self._file)):
            self.debug("TEMPLATE: NOT UPTODATE: " + self._file)
            return 0        

        # Included templates.
        for inc_file in self._include_mtimes.keys():
            if not (os.path.isfile(inc_file) and \
                    self._include_mtimes[inc_file] == \
                    os.path.getmtime(inc_file)):
                self.debug("TEMPLATE: NOT UPTODATE: " + inc_file)
                return 0
        else:
            self.debug("TEMPLATE: UPTODATE")
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

    def tokens(self):
        """ Get tokens of this template.
            @hidden
        """
        return self._tokens

    def file(self):
        """ Get filename of the main file of this template.
            @hidden
        """
        return self._file

    def content(self):
        """ Get content string of this template.
            @hidden
        """
        return self._content
        
    def setlogger(self, logger):
        """ Get debugging state.
            @hidden
        """
        self._logger = logger
    
    def debug(self, msg, level=logging.DEBUG):
        if self._logger:
            self._logger.write(msg, level=level)

    ##############################################
    #              PRIVATE METHODS               #
    ##############################################

    def __getstate__(self):
        """ Used by pickle when the class is serialized.
            Remove the 'debug' attribute before serialization.
            @hidden
        """
        dict = copy.copy(self.__dict__)
        del dict["_logger"]
        return dict

    def __setstate__(self, dict):
        """ Used by pickle when the class is unserialized.
            Add the 'debug' attribute.
            @hidden
        """
        self.__dict__ = dict



