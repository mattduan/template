"""
This template engine (tmpl) is based on Tomas Styblo's htmltmpl version
1.22 (http://htmltmpl.sourceforge.net/). The templating language was
borrowed from Perl package HTML::Template. The language detail can be
found at http://sam.tregar.com/html_template.html.
"""

__version__='$Revision: 3193 $'[11:-2]


# All imported modules are part of the standard Python library.
import re
import os
import os.path
import logging
import cPickle      # for template compilation

# template imports
from TemplateManager import TemplateManager
from TemplateException import TemplateException
from TemplateException import PrecompiledError
import TMPLTemplate as TMPLTemplate


INCLUDE_DIR = "."

# Total number of possible parameters.
# Increment if adding a parameter to any statement.
PARAMS_NUMBER = 3

# Relative positions of parameters in TemplateCompiler.tokenize().
PARAM_NAME = 1
PARAM_ESCAPE = 2
PARAM_GLOBAL = 3
PARAM_GETTEXT_STRING = 1

# Find a way to lock files. Currently implemented only for UNIX and windows.
LOCKTYPE_FCNTL = 1
LOCKTYPE_MSVCRT = 2
LOCKTYPE = None
try:
    import fcntl
except:
    try:
        import msvcrt
    except:
        LOCKTYPE = None
    else:
        LOCKTYPE = LOCKTYPE_MSVCRT
else:
    LOCKTYPE = LOCKTYPE_FCNTL
LOCK_EX = 1
LOCK_SH = 2
LOCK_UN = 3


##############################################
#        CLASS: TMPLTemplateManager
##############################################

class TMPLTemplateManager(TemplateManager):
    """  Class that manages compilation and precompilation of templates.
    
         You should use this class whenever you work with templates
         that are stored in a file. The class can create a compiled
         template and transparently manage its precompilation. It also
         keeps the precompiled templates up-to-date by modification times
         comparisons. 
    """

    def __init__(self, cache=10, precompile=1, logger=None):
        """ Constructor.
        
            @header
            __init__(cache=10, precompile=1)
            
            @param cache Enable or disable template cache or mixed cache with
            precompiled file cache.
            0 disable cache. 1 enable cache, that is, cache all templates in
            this class instance. #cache>1 enable mixed cache with only #cache
            templates in this class instance.
                        
            @param precompile Enable or disable precompilation of templates.
            This optional parameter can be used to enable or disable
            creation and usage of precompiled templates.
      
            A precompiled template is saved to the same directory in
            which the main template file is located. You need write
            permissions to that directory.

            Precompilation provides a significant performance boost because
            it's not necessary to parse the templates over and over again.
            The boost is especially noticeable when templates that include
            other templates are used.
            
            Comparison of modification times of the main template and all
            included templates is used to ensure that the precompiled
            templates are up-to-date. Templates are also recompiled if the
            htmltmpl module is updated.

            Precompilation is available only on UNIX and Windows platforms,
            because proper file locking which is necessary to ensure
            multitask safe behaviour is platform specific and is not
            implemented for other platforms. Attempts to enable precompilation
            on the other platforms result in raise of the
            <em>TemplateException</em> exception.
        """
        # Save the optional parameters.
        # These values are not modified by any method.

        # cache >= 0, integer
        try:
            self._cache = int(cache)
            if self._cache < 0:
                raise
        except:
            raise TemplateException, "Template cache must be an "\
                                     "non-negative integer."

        self._precompile = precompile
        # data structure used to cache templetes
        self._templates = {} # { 'file' : template, ... }
        self._ref_counts = {} # { 'file' : count, ... }

        self._include = 1
        self._max_include = 5
        self._comments = 1
        self._gettext = 0
        self._logger = logger

        # Find what module to use to lock files.
        # File locking is necessary for the 'precompile' feature to be
        # multitask/thread safe. Currently it works only on UNIX
        # and Windows. Anyone willing to implement it on Mac ?
        if precompile and not LOCKTYPE:
            raise TemplateException, "Template precompilation is not "\
                                     "available on this platform."

    def init(self, include=1, max_include=5, comments=1, gettext=0, logger=None):
        """ Initialization.
        
            @header
            init(include=1, max_include=5, comments=1, gettext=0, logger=None)
            
            @param include Enable or disable included templates.
            This optional parameter can be used to enable or disable
            <em>TMPL_INCLUDE</em> inclusion of templates. Disabling of
            inclusion can improve performance a bit. The inclusion is
            enabled by default.
      
            @param max_include Maximum depth of nested inclusions.
            This optional parameter can be used to specify maximum depth of
            nested <em>TMPL_INCLUDE</em> inclusions. It defaults to 5.
            This setting prevents infinite recursive inclusions.
            
            @param precompile Enable or disable precompilation of templates.
            This optional parameter can be used to enable or disable
            creation and usage of precompiled templates.
      
            A precompiled template is saved to the same directory in
            which the main template file is located. You need write
            permissions to that directory.

            Precompilation provides a significant performance boost because
            it's not necessary to parse the templates over and over again.
            The boost is especially noticeable when templates that include
            other templates are used.
            
            Comparison of modification times of the main template and all
            included templates is used to ensure that the precompiled
            templates are up-to-date. Templates are also recompiled if the
            htmltmpl module is updated.

            The <em>TemplateError</em>exception is raised when the precompiled
            template cannot be saved. Precompilation is enabled by default.

            Precompilation is available only on UNIX and Windows platforms,
            because proper file locking which is necessary to ensure
            multitask safe behaviour is platform specific and is not
            implemented for other platforms. Attempts to enable precompilation
            on the other platforms result in raise of the
            <em>TemplateError</em> exception.
            
            @param comments Enable or disable template comments.
            This optional parameter can be used to enable or disable
            template comments.
            Disabling of the comments can improve performance a bit.
            Comments are enabled by default.
            
            @param gettext Enable or disable gettext support.

            @param debug Enable or disable debugging messages.
            This optional parameter is a flag that can be used to enable
            or disable debugging messages which are printed to the standard
            error output. The debugging messages are disabled by default.
        """
        # Save the optional parameters.
        # These values are not modified by any method.
        self._include = include
        self._max_include = max_include
        self._comments = comments
        self._gettext = gettext
        self._logger = logger

        self.debug("TMPLTemplate Manager INIT DONE")

    def prepare(self, file, content=None):
        """ Preprocess, parse, tokenize and compile the template.
            
            If precompilation is enabled then this method tries to load
            a precompiled form of the template from the same directory
            in which the template source file is located. If it succeeds,
            then it compares modification times stored in the precompiled
            form to modification times of source files of the template,
            including source files of all templates included via the
            <em>TMPL_INCLUDE</em> statements. If any of the modification times
            differs, then the template is recompiled and the precompiled
            form updated.
            
            If precompilation is disabled, then this method parses and
            compiles the template.
            
            @header prepare(file)
            
            @return Compiled template.
            The methods returns an instance of the <em>Template</em> class
            which is a compiled form of the template. This instance can be
            used as input for the <em>TemplateProcessor</em>.
            
            @param file Path to the template file to prepare.
            The method looks for the template file in current directory
            if the parameter is a relative path. All included templates must
            be placed in subdirectory <strong>'inc'</strong> of the 
            directory in which the main template file is located.
        """
        template = None
        if self._cache == 0:
            # no cache
            self.debug("No cache! call compiled ...")
            return self.compiled(file, content)

        # considering cache
        self.debug("Cache = %s" % (self._cache))

        # create id
        tid = None
        if file:
            tid = file
        else:
            import md5
            tid = md5.new(content).hexdigest()

        self.debug( "Create Template ID: '%s'" % (tid) )

        # cache all templates
        if self._templates.has_key(tid):
            self.debug("%s PRECACHED" % (tid))
            cached_template = self._templates[tid]
            compile_params = (self._include, self._max_include,
                              self._comments, self._gettext)
            if cached_template.is_uptodate(compile_params):
                self.debug("PRECACHED: UPTODATE")
                template = cached_template
            else:
                self.debug("PRECACHED: NOT UPTODATE")
                template = self.update(cached_template)
                self._templates[tid] = template
            if self._cache > 1:
                if self._ref_counts.has_key(tid):
                    self._ref_counts[tid] += 1
                else:
                    self._ref_counts[tid] = 1
                self.debug("UPDATE REFER COUNTER %s" % (self._ref_counts[tid]))
        else:
            self.debug("%s IS NOT CACHED" % (tid))
            template = self.compiled(file, content)
            if self._cache == 1:
                self._templates[tid] = template
            else:
                # Mixed cache
                # Use reference counter as a measurement. The template with
                # higher counter is cached. Lower counted template will be
                # removed from cache.
                self.debug("DO MIXED CACHE")
                if self._ref_counts.has_key(tid):
                    self._ref_counts[tid] += 1
                else:
                    self._ref_counts[tid] = 1
                template_ref_count = self._ref_counts[tid]
                self.debug("UPDATE REFER COUNTER %s" % (template_ref_count))

                if len(self._templates) < self._cache:
                    self.debug("CACHE IS NOT FULL")
                    self._templates[tid] = template
                else:
                    self.debug("CACHE IS FULL")
                    old_tmpl = None
                    old_tid = None
                    old_rc = 0
                    for k in self._templates.keys():
                        cur_tmpl = self._templates[k]
                        cur_tid = cur_tmpl.getid()
                        cur_rc = self._ref_counts.get(cur_tid, 0)
                        if template_ref_count > cur_rc and \
                               ( cur_rc < old_rc or old_rc == 0 ):
                            old_tmpl = cur_tmpl
                            old_tid = cur_tid
                            old_rc = cur_rc
                    if old_tmpl:
                        self.debug("CACHE: REPLACE %s WITH %s" % (old_tid, tid))
                        del self._templates[old_tid]
                        self._templates[tid] = template
                
        return template
            

    def compiled(self, file, content=None):
        """ Preprocess, parse, tokenize and compile the template.
            
            If precompilation is enabled then this method tries to load
            a precompiled form of the template from the same directory
            in which the template source file is located. If it succeeds,
            then it compares modification times stored in the precompiled
            form to modification times of source files of the template,
            including source files of all templates included via the
            <em>TMPL_INCLUDE</em> statements. If any of the modification times
            differs, then the template is recompiled and the precompiled
            form updated.
            
            If precompilation is disabled, then this method parses and
            compiles the template.
            
            @header prepare(file)
            
            @return Compiled template.
            The methods returns an instance of the <em>Template</em> class
            which is a compiled form of the template. This instance can be
            used as input for the <em>TemplateProcessor</em>.
            
            @param file Path to the template file to prepare.
            The method looks for the template file in current directory
            if the parameter is a relative path. All included templates must
            be placed in subdirectory <strong>'inc'</strong> of the 
            directory in which the main template file is located.
        """
        compiled = None
        if file:
            if self._precompile:
                if self.is_precompiled(file):
                    try:
                        precompiled = self.load_precompiled(file)
                    except PrecompiledError, template:
                        self.debug( "Htmltmpl: bad precompiled "\
                                    "template '%s' removed" % template )
                        compiled = self.compile(file)
                        self.save_precompiled(compiled)
                    else:
                        precompiled.setlogger(self._logger)
                        compile_params = (self._include, self._max_include,
                                          self._comments, self._gettext)
                        if precompiled.is_uptodate(compile_params):
                            self.debug("PRECOMPILED: UPTODATE")
                            compiled = precompiled
                        else:
                            self.debug("PRECOMPILED: NOT UPTODATE")
                            compiled = self.update(precompiled)
                else:
                    self.debug("PRECOMPILED: NOT PRECOMPILED")
                    compiled = self.compile(file)
                    self.save_precompiled(compiled)
            else:
                self.debug("PRECOMPILATION DISABLED")
                compiled = self.compile(file)
        else:
            compiled = self.compile_string(content)
            
        return compiled
    
    def update(self, template):
        """ Update (recompile) a compiled template.
        
            This method recompiles a template compiled from a file.
            If precompilation is enabled then the precompiled form saved on
            disk is also updated.
            
            @header update(template)
            
            @return Recompiled template.
            It's ensured that the returned template is up-to-date.
            
            @param template A compiled template.
            This parameter should be an instance of the <em>Template</em>
            class, created either by the <em>TemplateManager</em> or by the
            <em>TemplateCompiler</em>. The instance must represent a template
            compiled from a file on disk.
        """
        self.debug("UPDATE")
        if template.file():
            updated = self.compile(template.file())
            if self._precompile:
                self.save_precompiled(updated)
        else:
            updated = self.compile_string(template.content())

        return updated

    def setlogger(self, logger):
        self._logger = logger

    ##############################################
    #              PRIVATE METHODS               #
    ##############################################    
    
    def lock_file(self, file, lock):
        """ Provide platform independent file locking.
            @hidden
        """
        fd = file.fileno()
        if LOCKTYPE == LOCKTYPE_FCNTL:
            if lock == LOCK_SH:
                fcntl.flock(fd, fcntl.LOCK_SH)
            elif lock == LOCK_EX:
                fcntl.flock(fd, fcntl.LOCK_EX)
            elif lock == LOCK_UN:
                fcntl.flock(fd, fcntl.LOCK_UN)
            else:
                raise TemplateException, "BUG: bad lock in lock_file"
        elif LOCKTYPE == LOCKTYPE_MSVCRT:
            if lock == LOCK_SH:
                # msvcrt does not support shared locks :-(
                msvcrt.locking(fd, msvcrt.LK_LOCK, 1)
            elif lock == LOCK_EX:
                msvcrt.locking(fd, msvcrt.LK_LOCK, 1)
            elif lock == LOCK_UN:
                msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)
            else:
                raise TemplateException, "BUG: bad lock in lock_file"
        else:
            raise TemplateException, "BUG: bad locktype in lock_file"

    def compile(self, file):
        """ Compile the template.
            @hidden
        """
        return TMPLTemplateCompiler(self._include, self._max_include,
                                    self._comments, self._gettext,
                                    self._logger).compile(file)
    
    def compile_string(self, data):
        """ Compile the template.
            @hidden
        """
        return TMPLTemplateCompiler(self._include, self._max_include,
                                    self._comments, self._gettext,
                                    self._logger).compile_string(data)
    
    def is_precompiled(self, file):
        """ Return true if the template is already precompiled on the disk.
            This method doesn't check whether the compiled template is
            uptodate.
            @hidden
        """
        filename = file + "c"   # "template.tmplc"
        if os.path.isfile(filename):
            return 1
        else:
            return 0
        
    def load_precompiled(self, file):
        """ Load precompiled template from disk.

            Remove the precompiled template file and recompile it
            if the file contains corrupted or unpicklable data.
            
            @hidden
        """
        filename = file + "c"   # "template.tmplc"
        self.debug("LOADING PRECOMPILED")
        try:
            remove_bad = 0
            file = None
            try:
                file = open(filename, "rb")
                self.lock_file(file, LOCK_SH)
                precompiled = cPickle.load(file)
            except IOError, (errno, errstr):
                raise TemplateException, "IO error in load precompiled "\
                                     "template '%s': (%d) %s"\
                                     % (filename, errno, errstr)
            except cPickle.UnpicklingError:
                remove_bad = 1
                raise PrecompiledError, filename
            except:
                remove_bad = 1
                raise
            else:
                return precompiled
        finally:
            if file:
                self.lock_file(file, LOCK_UN)
                file.close()
            if remove_bad and os.path.isfile(filename):
                # X: We may lose the original exception here, raising OSError.
                os.remove(filename)
                
    def save_precompiled(self, template):
        """ Save compiled template to disk in precompiled form.
            
            Associated metadata is also saved. It includes: filename of the
            main template file, modification time of the main template file,
            modification times of all included templates and version of the
            htmltmpl module which compiled the template.
            
            The method removes a file which is saved only partially because
            of some error.
            
            @hidden
        """
        filename = template.file() + "c"   # creates "template.tmplc"
        # Check if we have write permission to the template's directory.
        template_dir = os.path.dirname(os.path.abspath(filename))
        if not os.access(template_dir, os.W_OK):
            raise TemplateException, "Cannot save precompiled templates "\
                                 "to '%s': write permission denied."\
                                 % template_dir
        try:
            remove_bad = 0
            file = None
            try:
                file = open(filename, "wb")   # may truncate existing file
                self.lock_file(file, LOCK_EX)
                NEW_PROTO = 2  # new protocol introduced in version 2.3
                BINARY    = 1
                READABLE  = 0
                # compatibility for future versions
                HIGHEST_PROTO = NEW_PROTO
                cPickle.dump(template, file, HIGHEST_PROTO)
                #if self._logger:
                #    cPickle.dump(template, file, READABLE)
                #else:
                #    cPickle.dump(template, file, BINARY)
            except IOError, (errno, errstr):
                remove_bad = 1
                raise TemplateException, "IO error while saving precompiled "\
                                         "template '%s': (%d) %s"\
                                         % (filename, errno, errstr)
            except cPickle.PicklingError, error:
                remove_bad = 1
                raise TemplateException, "Pickling error while saving "\
                                         "precompiled template '%s': %s"\
                                         % (filename, error)
            except:
                remove_bad = 1
                raise
            else:
                self.debug("SAVING PRECOMPILED")
        finally:
            if file:
                self.lock_file(file, LOCK_UN)
                file.close()
            if remove_bad and os.path.isfile(filename):
                # X: We may lose the original exception here, raising OSError.
                os.remove(filename)

    def debug(self, msg, level=logging.DEBUG):
        if self._logger:
            self._logger.write(msg, level=level)

##############################################
#        CLASS: TMPLTemplateCompiler
##############################################

class TMPLTemplateCompiler:
    """ Preprocess, parse, tokenize and compile the template.

        This class parses the template and produces a 'compiled' form
        of it. This compiled form is an instance of the <em>Template</em>
        class. The compiled form is used as input for the TemplateProcessor
        which uses it to actually process the template.

        This class should be used direcly only when you need to compile
        a template from a string. If your template is in a file, then you
        should use the <em>TemplateManager</em> class which provides
        a higher level interface to this class and also can save the
        compiled template to disk in a precompiled form.
    """

    def __init__(self, include=1, max_include=5, comments=1, gettext=0,
                 logger=None):
        """ Constructor.

        @header __init__(include=1, max_include=5, comments=1, gettext=0,
                         logger=None)

        @param include Enable or disable included templates.
        @param max_include Maximum depth of nested inclusions.
        @param comments Enable or disable template comments.
        @param gettext Enable or disable gettext support.
        @param logger Enable or disable debugging messages.
        """
        
        self._include = include
        self._max_include = max_include
        self._comments = comments
        self._gettext = gettext
        self._logger = logger
        
        # This is a list of filenames of all included templates.
        # It's modified by the include_templates() method.
        self._include_files = []

        # This is a counter of current inclusion depth. It's used to prevent
        # infinite recursive includes.
        self._include_level = 0
    
    def compile(self, file):
        """ Compile template from a file.

            @header compile(file)
            @return Compiled template.
            The return value is an instance of the <em>Template</em>
            class.

            @param file Filename of the template.
            See the <em>prepare()</em> method of the <em>TemplateManager</em>
            class for exaplanation of this parameter.
        """
        
        self.debug("COMPILING FROM FILE: %s" % ( file ))
        self._include_path = os.path.join(os.path.dirname(file), INCLUDE_DIR)
        tokens = self.parse(self.read(file))
        compile_params = (self._include, self._max_include, self._comments,
                          self._gettext)
        template = TMPLTemplate.TMPLTemplate(file)
        template.init(TMPLTemplate.__version__, self._include_files,
                      tokens, compile_params, self._logger)
        return template

    def compile_string(self, data):
        """ Compile template from a string.

            This method compiles a template from a string. The
            template cannot include any templates.
            <strong>TMPL_INCLUDE</strong> statements are turned into warnings.

            @header compile_string(data)
            @return Compiled template.
            The return value is an instance of the <em>Template</em>
            class.

            @param data String containing the template data.        
        """
        self.debug("COMPILING FROM STRING")
        self._include = 0
        tokens = self.parse(data)
        compile_params = (self._include, self._max_include, self._comments,
                          self._gettext)
        template = TMPLTemplate.TMPLTemplate(None, data)
        template.init(TMPLTemplate.__version__, [], tokens, compile_params, self._logger)
        return template

    ##############################################
    #              PRIVATE METHODS               #
    ##############################################
                
    def read(self, filename):
        """ Read content of file and return it. Raise an error if a problem
            occurs.
            @hidden
        """
        self.debug("READING: " + filename)
        try:
            f = None
            try:
                f = open(filename, "r")
                data = f.read()
            except IOError, (errno, errstr):
                raise TemplateException, "IO error while reading template '%s': "\
                                         "(%d) %s" % (filename, errno, errstr)
            else:
                return data
        finally:
            if f: f.close()
               
    def parse(self, template_data):
        """ Parse the template. This method is recursively called from
            within the include_templates() method.

            @return List of processing tokens.
            @hidden
        """
        if self._comments:
            self.debug("PREPROCESS: COMMENTS")
            template_data = self.remove_comments(template_data)
        tokens = self.tokenize(template_data)
        if self._include:
            self.debug("PREPROCESS: INCLUDES")
            self.include_templates(tokens)
        return tokens

    def remove_comments(self, template_data):
        """ Remove comments from the template data.
            @hidden
        """
        pattern = r"### .*"
        return re.sub(pattern, "", template_data)
    
    def include_templates(self, tokens):
        """ Process TMPL_INCLUDE statements. Use the include_level counter
            to prevent infinite recursion. Record paths to all included
            templates to self._include_files.
            @hidden
        """
        i = 0
        out = ""    # buffer for output
        skip_params = 0
        
        # Process the list of tokens.
        while 1:
            if i == len(tokens): break
            if skip_params:
                skip_params = 0
                i += PARAMS_NUMBER
                continue

            token = tokens[i]
            if token == "<TMPL_INCLUDE":
                filename = tokens[i + PARAM_NAME]
                if not filename:
                    raise TemplateException, "No filename in <TMPL_INCLUDE>."
                self._include_level += 1
                if self._include_level > self._max_include:
                    # Do not include the template.
                    # Protection against infinite recursive includes.
                    skip_params = 1
                    self.debug("INCLUDE: LIMIT REACHED: " + filename)
                else:
                    # Include the template.
                    skip_params = 0
                    include_file = os.path.join(self._include_path, filename)
                    self._include_files.append(include_file)
                    include_data = self.read(include_file)
                    include_tokens = self.parse(include_data)

                    # Append the tokens from the included template to actual
                    # position in the tokens list, replacing the TMPL_INCLUDE
                    # token and its parameters.
                    tokens[i:i+PARAMS_NUMBER+1] = include_tokens
                    i = i + len(include_tokens)
                    self.debug("INCLUDED: " + filename)
                    continue   # Do not increment 'i' below.
            i += 1
            # end of the main while loop

        if self._include_level > 0: self._include_level -= 1
        return out
    
    def tokenize(self, template_data):
        """ Split the template into tokens separated by template statements.
            The statements itself and associated parameters are also
            separately  included in the resulting list of tokens.
            Return list of the tokens.

            @hidden
        """
        self.debug("TOKENIZING TEMPLATE")
        # NOTE: The TWO double quotes in character class in the regexp below
        # are there only to prevent confusion of syntax highlighter in Emacs.
        pattern = r"""
            (?:^[ \t]+)?               # eat spaces, tabs (opt.)
            (<
             (?:!--[ ])?               # comment start + space (opt.)
             /?TMPL_[A-Z]+             # closing slash / (opt.) + statement
             [ a-zA-Z0-9""/.=:_\\-]*   # this spans also comments ending (--)
             >)
            [%s]?                      # eat trailing newline (opt.)
        """ % os.linesep
        rc = re.compile(pattern, re.VERBOSE | re.MULTILINE)
        split = rc.split(template_data)
        tokens = []
        for statement in split:
            if statement.startswith("<TMPL_") or \
               statement.startswith("</TMPL_") or \
               statement.startswith("<!-- TMPL_") or \
               statement.startswith("<!-- /TMPL_"):
                # Processing statement.
                statement = self.strip_brackets(statement)
                statement = statement.strip()
                params = re.split(r"\s+", statement)
                self.debug("PARAMS: %s"%(params))
                tokens.append(self.find_directive(params))
                tokens.append(self.find_name(params))
                tokens.append(self.find_param("ESCAPE", params))
                tokens.append(self.find_param("GLOBAL", params))
            else:
                # "Normal" template data.
                if self._gettext:
                    self.debug("PARSING GETTEXT STRINGS")
                    self.gettext_tokens(tokens, statement)
                else:
                    tokens.append(statement)
        return tokens
    
    def gettext_tokens(self, tokens, str):
        """ Find gettext strings and return appropriate array of
            processing tokens.
            @hidden
        """
        escaped = 0
        gt_mode = 0
        i = 0
        buf = ""
        while(1):
            if i == len(str): break
            if str[i] == "\\":
                escaped = 0
                if str[i+1] == "\\":
                    buf += "\\"
                    i += 2
                    continue
                elif str[i+1] == "[" or str[i+1] == "]":
                    escaped = 1
                else:
                    buf += "\\"
            elif str[i] == "[" and str[i+1] == "[":
                if gt_mode:
                    if escaped:
                        escaped = 0
                        buf += "["
                    else:
                        buf += "["
                else:
                    if escaped:
                        escaped = 0
                        buf += "["
                    else:
                        tokens.append(buf)
                        buf = ""
                        gt_mode = 1
                        i += 2
                        continue
            elif str[i] == "]" and str[i+1] == "]":
                if gt_mode:
                    if escaped:
                        escaped = 0
                        buf += "]"
                    else:
                        self.add_gettext_token(tokens, buf)
                        buf = ""
                        gt_mode = 0
                        i += 2
                        continue
                else:
                    if escaped:
                        escaped = 0
                        buf += "]"
                    else:
                        buf += "]"
            else:
                escaped = 0
                buf += str[i]
            i += 1
            # end of the loop
        
        if buf:
            tokens.append(buf)
                
    def add_gettext_token(self, tokens, str):
        """ Append a gettext token and gettext string to the tokens array.
            @hidden
        """
        self.debug("GETTEXT PARSER: TOKEN: " + str)
        tokens.append("<TMPL_GETTEXT")
        tokens.append(str)
        tokens.append(None)
        tokens.append(None)
    
    def strip_brackets(self, statement):
        """ Strip HTML brackets (with optional HTML comments) from the
            beggining and from the end of a statement.
            @hidden
        """
        statement = statement.strip()
        if statement.startswith("<!-- TMPL_") or \
           statement.startswith("<!-- /TMPL_"):
            return statement[5:-4]
        else:
            return statement[1:-1]

    def find_directive(self, params):
        """ Extract processing directive (TMPL_*) from a statement.
            @hidden
        """
        directive = params[0]
        del params[0]
        self.debug("TOKENIZER: DIRECTIVE: " + directive)
        return "<" + directive

    def find_name(self, params):
        """ Extract identifier from a statement. The identifier can be
            specified both implicitely or explicitely as a 'NAME' parameter.
            @hidden
        """
        if len(params) > 0 and '=' not in params[0]:
            # implicit identifier
            name = params[0]
            del params[0]
        else:
            # explicit identifier as a 'NAME' parameter
            name = self.find_param("NAME", params)
        self.debug("TOKENIZER: NAME: " + str(name))
        return name

    def find_param(self, param, params):
        """ Extract value of parameter from a statement.
            @hidden
        """
        for pair in params:
            name, value = pair.split("=")
            if not name or not value:
                raise TemplateException, "Syntax error in template."
            if name == param:
                if value[0] == '"':
                    # The value is in double quotes.
                    ret_value = value[1:-1]
                else:
                    # The value is without double quotes.
                    ret_value = value
                self.debug("TOKENIZER: PARAM: '%s' => '%s'" % (param, ret_value))
                return ret_value
        else:
            self.debug("TOKENIZER: PARAM: '%s' => NOT DEFINED" % param)
            return None
    
    def debug(self, msg, level=logging.DEBUG):
        if self._logger:
            self._logger.write(msg, level=level)


