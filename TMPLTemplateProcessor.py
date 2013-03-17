"""
This template engine (tmpl) is based on Tomas Styblo's htmltmpl version
1.22 (http://htmltmpl.sourceforge.net/). The templating language was
borrowed from Perl package HTML::Template. The language detail can be
found at http://sam.tregar.com/html_template.html.
"""

__version__='$Revision: 3193 $'[11:-2]

# All imported modules are part of the standard Python library.

from types import *
import cgi          # for HTML escaping of variables
import urllib       # for URL escaping of variables
import gettext
import logging

# template imports
from TemplateProcessor import TemplateProcessor
from TemplateException import TemplateException

# Total number of possible parameters.
# Increment if adding a parameter to any statement.
PARAMS_NUMBER = 3

# Relative positions of parameters in TemplateCompiler.tokenize().
PARAM_NAME = 1
PARAM_ESCAPE = 2
PARAM_GLOBAL = 3
PARAM_GETTEXT_STRING = 1


##############################################
#          CLASS: TMPLTemplateProcessor
##############################################

class TMPLTemplateProcessor( TemplateProcessor ):
    """ Fill the template with data and process it.

        This class provides actual processing of a compiled template.
        Use it to set template variables and loops and then obtain
        result of the processing.
    """

    def __init__(self, logger=None):
        """ Constructor.
        """
        self._html_escape = 1
        self._magic_vars = 1
        self._global_vars = 0
        self._logger = logger

        # Data structure containing variables and loops set by the
        # application. Use debug=1, process some template and
        # then check stderr to see how the structure looks.
        # It's modified only by set() and reset() methods.
        self._vars = {}

        # Following variables are for multipart templates.
        self._current_part = 1
        self._current_pos = 0

    def init(self, html_escape=1, magic_vars=1, global_vars=0, keep_data=0, logger=None):
        """ Initialization.

            NOTE: html_escape should be parsed from html template TMPL_VAR as
            a flag value; magic_vars should always be 1; global_vars can also
            be a TMPL_VAR flag. FIXME!

            @header __init__(html_escape=1, magic_vars=1, global_vars=0,
                             debug=0)

            @param html_escape Enable or disable HTML escaping of variables.
            This optional parameter is a flag that can be used to enable or
            disable automatic HTML escaping of variables.
            All variables are by default automatically HTML escaped. 
            The escaping process substitutes HTML brackets, ampersands and
            double quotes with appropriate HTML entities.
            
            @param magic_vars Enable or disable loop magic variables.
            This parameter can be used to enable or disable
            "magic" context variables, that are automatically defined inside
            loops. Magic variables are enabled by default.

            Refer to the language specification for description of these
            magic variables.
      
            @param global_vars Globally activate global lookup of variables.
            This optional parameter is a flag that can be used to specify
            whether variables which cannot be found in the current scope
            should be automatically looked up in enclosing scopes.

            Automatic global lookup is disabled by default. Global lookup
            can be overriden on a per-variable basis by the
            <strong>GLOBAL</strong> parameter of a <strong>TMPL_VAR</strong>
            statement.

            @param logger A logger object for logging debugging messages.
        """
        self._html_escape  = html_escape
        self._magic_vars   = magic_vars
        self._global_vars  = global_vars
        self._logger       = logger

        # reset data
        self.reset(keep_data=keep_data)
        

    def set(self, var, value):
        """ Associate a value with top-level template variable or loop.

            A template identifier can represent either an ordinary variable
            (string) or a loop.

            To assign a value to a string identifier pass a scalar
            as the 'value' parameter. This scalar will be automatically
            converted to string.

            To assign a value to a loop identifier pass a list of mappings as
            the 'value' parameter. The engine iterates over this list and
            assigns values from the mappings to variables in a template loop
            block if a key in the mapping corresponds to a name of a variable
            in the loop block. The number of mappings contained in this list
            is equal to number of times the loop block is repeated in the
            output.
      
            @header set(var, value)
            @return No return value.

            @param var Name of template variable or loop.
            @param value The value to associate.
            
        """
        # The correctness of character case is verified only for top-level
        # variables.
        if self.is_ordinary_var(value):
            # template top-level ordinary variable
            if not var.islower():
                raise TemplateException, "Invalid variable name '%s'." % var
        elif type(value) in [ListType, TupleType] or \
             (hasattr(value, '__class__') and issubclass(value.__class__, list)):
            # template top-level loop
            if var != var.capitalize():
                raise TemplateException, "Invalid loop name '%s' (%s)." % (var, value)
        else:
            #raise TemplateException, "Value of toplevel variable '%s' must "\
            #                     "be either a scalar or a list." % var
            self.debug("Value of toplevel variable '%s' is not a "\
                       "scalar or a list. Assuming boolean ..." % var)
            value = value and True or False
            
        self._vars[var] = value
        self.debug("VALUE SET: " + str(var))

    def get(self, var, alt=None):
        """ Retreve a value with top-level template variable or loop.
        """
        return self._vars.get(var, alt)

    def __setitem__(self, var, value):
        """ [] = operator
        """
        self.set(var, value)

    def __getitem__( self, var ):
        """ [] operator
        """
        return self._vars[var]

    def __delitem__( self, var ):
        """ del [] operator
        """
        del self._vars[var]

    def has_key( self, var ):
        """ key lookup.
        """
        return self._vars.has_key( var )    
    
    def keys( self ):
        """ all of the keys
        """
        return self._vars.keys()

    def setdict(self, dict):
        if type(dict) != type({}):
            return

        for key in dict.keys():
            self.set(key, dict[key])
        
    def reset(self, keep_data=0):
        """ Reset the template data.

            This method resets the data contained in the template processor
            instance. The template processor instance can be used to process
            any number of templates, but this method must be called after
            a template is processed to reuse the instance,

            @header reset(keep_data=0)
            @return No return value.

            @param keep_data Do not reset the template data.
            Use this flag if you do not want the template data to be erased.
            This way you can reuse the data contained in the instance of
            the <em>TemplateProcessor</em>.
        """
        self._current_part = 1
        self._current_pos = 0
        if not keep_data:
            self._vars.clear()
        self.debug("RESET")

    def process(self, template, part=None):
        """ Process a compiled template. Return the result as string.

            This method actually processes a template and returns
            the result.

            @header process(template, part=None)
            @return Result of the processing as string.

            @param template A compiled template.
            Value of this parameter must be an instance of the
            <em>Template</em> class created either by the
            <em>TemplateManager</em> or by the <em>TemplateCompiler</em>.

            @param part The part of a multipart template to process.
            This parameter can be used only together with a multipart
            template. It specifies the number of the part to process.
            It must be greater than zero, because the parts are numbered
            from one.

            The parts must be processed in the right order. You
            cannot process a part which precedes an already processed part.

            If this parameter is not specified, then the whole template
            is processed, or all remaining parts are processed.
        """
        self.debug("APP INPUT:")
        self.debug( "%s" % (self._vars) )
        if part != None and (part == 0 or part < self._current_part):
            raise TemplateException, "process() - invalid part number"

        # This flag means "jump behind the end of current statement" or
        # "skip the parameters of current statement".
        # Even parameters that actually are not present in the template
        # do appear in the list of tokens as empty items !
        skip_params = 0 

        # Stack for enabling or disabling output in response to TMPL_IF,
        # TMPL_UNLESS, TMPL_ELSE and TMPL_LOOPs with no passes.
        output_control = []
        ENABLE_OUTPUT = 1
        DISABLE_OUTPUT = 0
        
        # Stacks for data related to loops.
        loop_name = []        # name of a loop
        loop_pass = []        # current pass of a loop (counted from zero)
        loop_start = []       # index of loop start in token list
        loop_total = []       # total number of passes in a loop
        
        tokens = template.tokens()
        len_tokens = len(tokens)
        out = ""              # buffer for processed output

        # Recover position at which we ended after processing of last part.
        i = self._current_pos
            
        # Process the list of tokens.
        while 1:
            if i == len_tokens: break            
            if skip_params:   
                # Skip the parameters following a statement.
                skip_params = 0
                i += PARAMS_NUMBER
                continue

            token = tokens[i]
            if token.startswith("<TMPL_") or \
               token.startswith("</TMPL_"):
                if token == "<TMPL_VAR":
                    # TMPL_VARs should be first. They are the most common.
                    var = tokens[i + PARAM_NAME]
                    if not var:
                        raise TemplateException, "No identifier in <TMPL_VAR>."
                    escape = tokens[i + PARAM_ESCAPE]
                    globalp = tokens[i + PARAM_GLOBAL]
                    skip_params = 1
                    
                    # If output of current block is not disabled then append
                    # the substitued and escaped variable to the output.
                    if DISABLE_OUTPUT not in output_control:
                        value = str(self.find_value(var, loop_name, loop_pass,
                                                    loop_total, globalp))
                        out += self.escape(value, escape)
                        self.debug("VAR: " + str(var))

                elif token == "<TMPL_LOOP":
                    var = tokens[i + PARAM_NAME]
                    if not var:
                        raise TemplateException, "No identifier in <TMPL_LOOP>."
                    skip_params = 1

                    # Find total number of passes in this loop.
                    passtotal = self.find_value(var, loop_name, loop_pass,
                                                loop_total)
                    if not passtotal: passtotal = 0
                    # Push data for this loop on the stack.
                    loop_total.append(passtotal)
                    loop_start.append(i)
                    loop_pass.append(0)
                    loop_name.append(var)

                    # Disable output of loop block if the number of passes
                    # in this loop is zero.
                    if passtotal == 0:
                        # This loop is empty.
                        output_control.append(DISABLE_OUTPUT)
                        self.debug("LOOP: DISABLE: " + str(var))
                    else:
                        output_control.append(ENABLE_OUTPUT)
                        self.debug("LOOP: FIRST PASS: %s TOTAL: %d"\
                                 % (var, passtotal))

                elif token == "<TMPL_IF":
                    var = tokens[i + PARAM_NAME]
                    if not var:
                        raise TemplateException, "No identifier in <TMPL_IF>."
                    globalp = tokens[i + PARAM_GLOBAL]
                    skip_params = 1
                    if self.find_value(var, loop_name, loop_pass,
                                       loop_total, globalp):
                        output_control.append(ENABLE_OUTPUT)
                        self.debug("IF: ENABLE: " + str(var))
                    else:
                        output_control.append(DISABLE_OUTPUT)
                        self.debug("IF: DISABLE: " + str(var))
     
                elif token == "<TMPL_UNLESS":
                    var = tokens[i + PARAM_NAME]
                    if not var:
                        raise TemplateException, "No identifier in <TMPL_UNLESS>."
                    globalp = tokens[i + PARAM_GLOBAL]
                    skip_params = 1
                    if self.find_value(var, loop_name, loop_pass,
                                      loop_total, globalp):
                        output_control.append(DISABLE_OUTPUT)
                        self.debug("UNLESS: DISABLE: " + str(var))
                    else:
                        output_control.append(ENABLE_OUTPUT)
                        self.debug("UNLESS: ENABLE: " + str(var))
     
                elif token == "</TMPL_LOOP":
                    skip_params = 1
                    if not loop_name:
                        raise TemplateException, "Unmatched </TMPL_LOOP>."
                    
                    # If this loop was not disabled, then record the pass.
                    if loop_total[-1] > 0: loop_pass[-1] += 1
                    
                    if loop_pass[-1] == loop_total[-1]:
                        # There are no more passes in this loop. Pop
                        # the loop from stack.
                        loop_pass.pop()
                        loop_name.pop()
                        loop_start.pop()
                        loop_total.pop()
                        output_control.pop()
                        self.debug("LOOP: END")
                    else:
                        # Jump to the beggining of this loop block 
                        # to process next pass of the loop.
                        i = loop_start[-1]
                        self.debug("LOOP: NEXT PASS")
     
                elif token == "</TMPL_IF":
                    skip_params = 1
                    if not output_control:
                        raise TemplateException, "Unmatched </TMPL_IF>."
                    output_control.pop()
                    self.debug("IF: END")
     
                elif token == "</TMPL_UNLESS":
                    skip_params = 1
                    if not output_control:
                        raise TemplateException, "Unmatched </TMPL_UNLESS>."
                    output_control.pop()
                    self.debug("UNLESS: END")
     
                elif token == "<TMPL_ELSE":
                    skip_params = 1
                    if not output_control:
                        raise TemplateException, "Unmatched <TMPL_ELSE>."
                    if output_control[-1] == DISABLE_OUTPUT:
                        # Condition was false, activate the ELSE block.
                        output_control[-1] = ENABLE_OUTPUT
                        self.debug("ELSE: ENABLE")
                    elif output_control[-1] == ENABLE_OUTPUT:
                        # Condition was true, deactivate the ELSE block.
                        output_control[-1] = DISABLE_OUTPUT
                        self.debug("ELSE: DISABLE")
                    else:
                        raise TemplateException, "BUG: ELSE: INVALID FLAG"

                elif token == "<TMPL_BOUNDARY":
                    if part and part == self._current_part:
                        self.debug("BOUNDARY ON")
                        self._current_part += 1
                        self._current_pos = i + 1 + PARAMS_NUMBER
                        break
                    else:
                        skip_params = 1
                        self.debug("BOUNDARY OFF")
                        self._current_part += 1

                elif token == "<TMPL_INCLUDE":
                    # TMPL_INCLUDE is left in the compiled template only
                    # when it was not replaced by the parser.
                    skip_params = 1
                    filename = tokens[i + PARAM_NAME]
                    out += """
                        <br />
                        <p>
                        <strong>HTMLTMPL WARNING:</strong><br />
                        Cannot include template: <strong>%s</strong>
                        </p>
                        <br />
                    """ % filename
                    self.debug("CANNOT INCLUDE WARNING")

                elif token == "<TMPL_GETTEXT":
                    skip_params = 1
                    if DISABLE_OUTPUT not in output_control:
                        text = tokens[i + PARAM_GETTEXT_STRING]
                        out += gettext.gettext(text)
                        self.debug("GETTEXT: " + text)
                    
                else:
                    # Unknown processing directive.
                    raise TemplateException, "Invalid statement %s>." % token
                     
            elif DISABLE_OUTPUT not in output_control:
                # Raw textual template data.
                # If output of current block is not disabled, then 
                # append template data to the output buffer.
                out += token
                
            i += 1
            # end of the big while loop
        
        # Check whether all opening statements were closed.
        
        if loop_name: raise TemplateException, "Missing </TMPL_LOOP>."
        if output_control: raise TemplateException, "Missing </TMPL_IF> or </TMPL_UNLESS>"
        return out

    def setlogger(self, logger):
        self._logger = logger

    def debug(self, msg, level=logging.DEBUG):
        if self._logger:
            self._logger.write(msg, level=level)
    
    ##############################################
    #              PRIVATE METHODS               #
    ##############################################
    
    def find_value(self, var, loop_name, loop_pass, loop_total,
                   global_override=None):
        """ Search the self._vars data structure to find variable var
            located in currently processed pass of a loop which
            is currently being processed. If the variable is an ordinary
            variable, then return it.
            
            If the variable is an identificator of a loop, then 
            return the total number of times this loop will
            be executed.
            
            Return an empty string, if the variable is not
            found at all.

            @hidden
        """
        # Search for the requested variable in magic vars if the name
        # of the variable starts with "__" and if we are inside a loop.
        if self._magic_vars and var.startswith("__") and loop_name:
            return self.magic_var(var, loop_pass[-1], loop_total[-1])
                    
        # Search for an ordinary variable or for a loop.
        # Recursively search in self._vars for the requested variable.
        scope = self._vars
        #self.debug("SCOPE: %s"%(scope))
        globals = []
        for i in range(len(loop_name)):            
            # If global lookup is on then push the value on the stack.
            if ((self._global_vars and global_override != "0") or \
                 global_override == "1") and scope.has_key(var) and \
                self.is_ordinary_var(scope[var]):
                globals.append(scope[var])
		   
            
            # Descent deeper into the hierarchy.
            if scope.has_key(loop_name[i]) and scope[loop_name[i]]:
                self.debug("LOOP_NAME: %s; LOOP_PASS: %s"%(loop_name[i],loop_pass[i]))
                scope = scope[loop_name[i]][loop_pass[i]] #####what is the meanning
            else:
                return ""
            
        if scope.has_key(var):
            # Value exists in current loop.
            if type(scope[var]) in [ListType, TupleType] or \
               (hasattr(scope[var], '__class__') and issubclass(scope[var].__class__, list)):
                # The requested value is a loop.
                # Return total number of its passes.
                return len(scope[var])
            else:
                return scope[var]
        elif globals and \
             ((self._global_vars and global_override != "0") or \
               global_override == "1"):
            # Return globally looked up value.
            return globals.pop()
        else:
            # No value found.
            if var[0].isupper():
                # This is a loop name.
                # Return zero, because the user wants to know number
                # of its passes.
                return 0
            else:
                return ""

    def magic_var(self, var, loop_pass, loop_total):
        """ Resolve and return value of a magic variable.
            Raise an exception if the magic variable is not recognized.

            @hidden
        """
        self.debug("MAGIC: '%s', PASS: %d, TOTAL: %d"\
                 % (var, loop_pass, loop_total))
        if var == "__FIRST__":
            if loop_pass == 0:
                return 1
            else:
                return 0
        elif var == "__LAST__":
            if loop_pass == loop_total - 1:
                return 1
            else:
                return 0
        elif var == "__INNER__":
            # If this is neither the first nor the last pass.
            if loop_pass != 0 and loop_pass != loop_total - 1:
                return 1
            else:
                return 0        
        elif var == "__PASS__":
            # Magic variable __PASS__ counts passes from one.
            return loop_pass + 1
        elif var == "__PASSTOTAL__":
            return loop_total
        elif var == "__ODD__":
            # Internally pass numbers stored in loop_pass are counted from
            # zero. But the template language presents them counted from one.
            # Therefore we must add one to the actual loop_pass value to get
            # the value we present to the user.
            if (loop_pass + 1) % 2 != 0:
                return 1
            else:
                return 0
        elif var.startswith("__EVERY__"):
            # Magic variable __EVERY__x is never true in first or last pass.
            if loop_pass != 0 and loop_pass != loop_total - 1:
                # Check if an integer follows the variable name.
                try:
                    every = int(var[9:])   # nine is length of "__EVERY__"
                except ValueError:
                    raise TemplateException, "Magic variable __EVERY__x: "\
                                         "Invalid pass number."
                else:
                    if not every:
                        raise TemplateException, "Magic variable __EVERY__x: "\
                                             "Pass number cannot be zero."
                    elif (loop_pass + 1) % every == 0:
                        self.debug("MAGIC: EVERY: " + str(every))
                        return 1
                    else:
                        return 0
            else:
                return 0
        else:
            raise TemplateException, "Invalid magic variable '%s'." % var

    def escape(self, str, override=""):
        """ Escape a string either by HTML escaping or by URL escaping.
            @hidden
        """
        ESCAPE_QUOTES = 1
        if (self._html_escape and override != "NONE" and override != "0" and \
            override != "URL") or override == "HTML" or override == "1":
            return cgi.escape(str, ESCAPE_QUOTES)
        elif override == "URL":
            return urllib.quote_plus(str)
        else:
            return str

    def is_ordinary_var(self, var):
        """ Return true if var is a scalar. (not a reference to loop)
            @hidden
        """
        if type(var) in [StringType, UnicodeType, IntType, LongType,
                         FloatType, BooleanType]:
            return 1
        else:
            return 0

    
