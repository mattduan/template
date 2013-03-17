"""
The template manager class. Its purpose is to organize all templates used
in a website. It responds to initialize, cache/save and update templates.
All templates should be got only from this class.
"""

__version__='$Revision: 52 $'[11:-2]
__author__ = "Duan Guoqiang (mattgduan@gmail.com)"



# template imports
from TemplateException import NotImplementedException


##############################################
#          CLASS: TemplateManager
##############################################

class TemplateManager:
    """  Class that manages compilation and precompilation of templates.
         With mod_python, it will keep one instance in Apache name space
         to keep template caches in memory.

         This class is the abstract class of all template manager classes.
    """

    def __init__(self, cache=10, precompile=1):
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
        self._cache = cache
        self._precompile = precompile
        self._templates = {}

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
        raise NotImplementedException, "TemplateManager.prepare() method must be " + \
                                       "overwrited by subclass for model specific" + \
                                       "template object!"
        
    
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
        raise NotImplementedException, "TemplateManager.update() method must be " + \
                                       "overwrited by subclass for model specific" + \
                                       "template object!"
