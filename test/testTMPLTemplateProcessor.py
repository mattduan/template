"""
PyUnit TestCase for TMPLTemplateProcessor.

$Id: testTMPLTemplateProcessor.py 3193 2010-11-10 14:22:01Z duan $
"""

__version__= "$Revision: 3193 $"[11:-2]

import unittest
import sets
import os
import sys

# more imports
import template.TMPLTemplateProcessor as TMPLTemplateProcessor
import template.TemplateProcessor as TemplateProcessor
import template.TMPLTemplate as TMPLTemplate
import template.TemplateException as TemplateException

# test fixture

def create_file(filename, content, always=0):
    if not os.access(filename, os.F_OK) or always:
        f = open(filename, 'w')
        f.write(content)
        f.close()

def rm_f(top):
    for root, dirs, files in os.walk(top, topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))
    os.rmdir(top)

class testTMPLTemplateProcessor(unittest.TestCase):

    def setUp(self):
        self.__testee = TMPLTemplateProcessor.TMPLTemplateProcessor()

        mo = sys.modules[self.__module__]
        self.__path = mo.__path__

        
    def tearDown(self):
        self.__testee = None

    def test__init__(self):
	"""
        Test Constructor
	"""
        self.assertEquals(self.__testee._html_escape, 1)
        self.assertEquals(self.__testee._magic_vars, 1)
        self.assertEquals(self.__testee._global_vars, 0)
        self.assertEquals(self.__testee._vars, {})
        self.assertEquals(self.__testee._current_part, 1)
        self.assertEquals(self.__testee._current_pos, 0)
   
    def test_init(self):
        """
        Test init
	"""
        tmpl = TMPLTemplateProcessor.TMPLTemplateProcessor()
        tmpl.init(html_escape=2, magic_vars=2, global_vars=1, keep_data=1, logger=None)
        self.assertEquals(tmpl._html_escape, 2)
        self.assertEquals(tmpl._magic_vars, 2)
        self.assertEquals(tmpl._global_vars, 1)
        self.assertEquals(tmpl._current_part, 1)
        self.assertEquals(tmpl._current_pos, 0)
    
    def test_reset(self):
	"""
        Test reset
	"""
        tmpl = TMPLTemplateProcessor.TMPLTemplateProcessor()
        tmpl.set('var',1)
        tmpl.reset(keep_data=0)
        self.assertEquals(tmpl._current_part, 1)
        self.assertEquals(tmpl._current_pos, 0)
        self.assertEquals(tmpl._vars.keys(), [])    

    def test_setdict(self):  
	"""
        Test setdict
	"""
        tmpl = TMPLTemplateProcessor.TMPLTemplateProcessor()
        tmpl.setdict({"var1":1, "var2":2})
        self.assertEquals(tmpl.keys(), ["var1","var2"])
        self.assertEquals(tmpl._vars["var1"], 1)
        self.assertEquals(tmpl._vars["var2"], 2)
        
    def test_escape(self):
	"""
        Test escape
	"""
        tmpl = TMPLTemplateProcessor.TMPLTemplateProcessor()
        self.assertEquals(tmpl.escape("A HREF = < & TMPLTemplateProcessor & >", override="HTML"),\
                         "A HREF = &lt; &amp; TMPLTemplateProcessor &amp; &gt;" )
        self.assertEquals(tmpl.escape("A HREF = < & TMPLTemplateProcessor & >", override="1"),\
                         "A HREF = &lt; &amp; TMPLTemplateProcessor &amp; &gt;" )
        self.assertEquals(tmpl.escape("A HREF = < & TMPLTemplateProcessor & >", override=None),\
                         "A HREF = &lt; &amp; TMPLTemplateProcessor &amp; &gt;" )

        self.assertEquals(tmpl.escape("A HREF = < & TMPLTemplateProcessor & >", override="URL"),\
                          "A+HREF+%3D+%3C+%26+TMPLTemplateProcessor+%26+%3E" )
        self.assertEquals(tmpl.escape("A HREF = < & TMPLTemplateProcessor & >", override="0"),\
                          "A HREF = < & TMPLTemplateProcessor & >")


    def test_magic_var(self):
	"""
        Test magic_var
	"""
        tmpl = TMPLTemplateProcessor.TMPLTemplateProcessor()
       
        self.assertEquals(tmpl.magic_var("__FIRST__", 0, 1), 1)
        self.assertEquals(tmpl.magic_var("__FIRST__", 1, 3), 0)

        self.assertEquals(tmpl.magic_var("__LAST__", 1, 2), 1)
        self.assertEquals(tmpl.magic_var("__LAST__", 1, 3), 0)
        
        self.assertEquals(tmpl.magic_var("__INNER__", 1, 3), 1)
        self.assertEquals(tmpl.magic_var("__INNER__", 2, 3), 0)

        self.assertEquals(tmpl.magic_var("__PASS__", 0, 3), 1)

        self.assertEquals(tmpl.magic_var("__PASSTOTAL__", 0, 3), 3)

        self.assertEquals(tmpl.magic_var("__ODD__", 0, 3), 1)
        self.assertEquals(tmpl.magic_var("__ODD__", 1, 3), 0)
 
        self.assertEquals(tmpl.magic_var("__EVERY__0", 0, 3), 0)
        self.assertEquals(tmpl.magic_var("__EVERY__0", 2, 3), 0)

        self.assertRaises(TemplateException.TemplateException, tmpl.magic_var, "InvalidString", 0, 0)       
        self.assertRaises(TemplateException.TemplateException, tmpl.magic_var, "__EVERY__NoInt", 1, 3)
        self.assertRaises(TemplateException.TemplateException, tmpl.magic_var, "__EVERY__0", 1, 3)
        self.assertEquals(tmpl.magic_var("__EVERY__2", 1, 3), 1)
        self.assertEquals(tmpl.magic_var("__EVERY__2", 2, 4), 0)
      
    def test_is_ordinary_var(self):
	"""
        Test is_ordinary_var
	"""
        tmpl = TMPLTemplateProcessor.TMPLTemplateProcessor()
        self.assertEquals(tmpl.is_ordinary_var(1), True)
        self.assertEquals(tmpl.is_ordinary_var(1.00), True)
        self.assertEquals(tmpl.is_ordinary_var(False), True)
        self.assertEquals(tmpl.is_ordinary_var("string"), True)
        self.assertEquals(tmpl.is_ordinary_var(10000000000), True)
        self.assertEquals(tmpl.is_ordinary_var([1,2,4]), False)

    def test_set(self):
	"""
        Test set
	"""
        tmpl = TMPLTemplateProcessor.TMPLTemplateProcessor()
        self.assertRaises(TemplateException.TemplateException, tmpl.set, 'Variables', 1)
        self.assertRaises(TemplateException.TemplateException, tmpl.set, 'class', [1,2])
        self.assertRaises(TemplateException.TemplateException, tmpl.set, 'class', (1,2))
        tmpl.set('var',{1:2,2:3})
        self.assertEquals(tmpl._vars['var'], True)
        tmpl.set('var', None)
        self.assertEquals(tmpl._vars['var'], False)
        tmpl.set('var', 'str')
        self.assertEquals(tmpl._vars['var'], 'str')
        tmpl.set('Var', [1,2,3])
        self.assertEquals(tmpl._vars['Var'], [1,2,3])


    def test_get(self):
	"""
        Test get
	"""
        tmpl = TMPLTemplateProcessor.TMPLTemplateProcessor()
        tmpl.set('var', 'str')
        self.assertEquals(tmpl.get('var'),'str')

    def test___setitem__(self):
	"""
        Test __setitem__
	"""
        tmpl = TMPLTemplateProcessor.TMPLTemplateProcessor()
        tmpl.__setitem__('var', 1)
        self.assertEquals(tmpl._vars['var'], 1)
  
    def test___getitem__(self):
	"""
        Test __getitem__
	"""
        tmpl = TMPLTemplateProcessor.TMPLTemplateProcessor()
        tmpl.__setitem__('var', 1)
        self.assertEquals(tmpl.__getitem__('var'), 1)
     

    def test___delitem__(self):
	"""
        Test __delitem__
	"""
        tmpl = TMPLTemplateProcessor.TMPLTemplateProcessor()
        tmpl.__setitem__('var', 1)
        self.assertEquals(tmpl.has_key('var'), True )
        tmpl.__delitem__('var')
        self.assertEquals(tmpl.has_key('var'), False )
    
    def test_has_key(self):
	"""
        Test has_key
	"""
        tmpl = TMPLTemplateProcessor.TMPLTemplateProcessor()
        tmpl.__setitem__('var', 1)
        self.assertEquals(tmpl.has_key('var'), True )

    def test_keys(self):
        tmpl = TMPLTemplateProcessor.TMPLTemplateProcessor()
        tmpl.__setitem__('var1', 1)
        tmpl.__setitem__('var2', 2)
        self.assertEquals(tmpl.keys(),['var1', 'var2'])

    def test_process(self):
	"""
        Test process
	"""
        path = sys.modules[self.__module__].__path__
        os.path.join(path, "tmp")
        filename = os.path.join(path, 'tmp/file.txt')
        os.mkdir(os.path.join(self.__path, "tmp"))

        fl = open(filename, 'w')

        f_tmpl = TMPLTemplate.TMPLTemplate(filename)
        tmplproc = TMPLTemplateProcessor.TMPLTemplateProcessor()
              
        self.assertRaises(TemplateException.TemplateException, tmplproc.process, f_tmpl, 0)
        tmplproc._current_part = 2 
        self.assertRaises(TemplateException.TemplateException, tmplproc.process, f_tmpl, 1)      
      
        f_tmpl.init(TMPLTemplate.__version__, [], ["<TMPL_INVALID"], {})
        self.assertRaises(TemplateException.TemplateException, tmplproc.process, f_tmpl)
        
        f_tmpl.init(TMPLTemplate.__version__, [], ["Raw ", "textual " ,"template ", "data"], {})
        self.assertEquals(tmplproc.process(f_tmpl), "Raw textual template data")
        
        f_tmpl.init(TMPLTemplate.__version__, [], ["<TMPL_GETTEXT", "a", "b", "c","d"], {})
        self.assertEquals(tmplproc.process(f_tmpl), "ad")
        
        f_tmpl.init(TMPLTemplate.__version__, [], ["<TMPL_INCLUDE", "filename","","",], {})
        self.assertEquals(tmplproc.process(f_tmpl), """
                        <br />
                        <p>
                        <strong>HTMLTMPL WARNING:</strong><br />
                        Cannot include template: <strong>filename</strong>
                        </p>
                        <br />
                    """ )
        f_tmpl.init(TMPLTemplate.__version__, [], ["<TMPL_BOUNDARY","a","b","c","d"], {})
        tmplproc.process(f_tmpl, 2)
        self.assertEquals(tmplproc._current_part, 3)
        self.assertEquals(tmplproc._current_pos, 4)
        self.assertEquals(tmplproc.process(f_tmpl, 4), 'd')

        f_tmpl.init(TMPLTemplate.__version__, [], ['a','b','c','d',"</TMPL_UNLESS"], {})
        self.assertRaises(TemplateException.TemplateException, tmplproc.process, f_tmpl)

        f_tmpl.init(TMPLTemplate.__version__, [], ['a','b','c','d',"</TMPL_IF"], {})
        self.assertRaises(TemplateException.TemplateException, tmplproc.process, f_tmpl)

        f_tmpl.init(TMPLTemplate.__version__, [], ['a','b','c','d',"</TMPL_LOOP"], {})
        self.assertRaises(TemplateException.TemplateException, tmplproc.process, f_tmpl)
        
        tmplproc.reset()
        tmplproc.set('var', 3)
        tmplproc.set('var1', 'HREF<')
        tmplproc.set('var2', 'HREF>')
        f_tmpl.init(TMPLTemplate.__version__, [], ["<TMPL_ELSE",'',None,None], {})
        self.assertRaises(TemplateException.TemplateException, tmplproc.process, f_tmpl)
        f_tmpl.init(TMPLTemplate.__version__, [], ["<TMPL_IF",'var',None,None,\
                                                   "<TMPL_ELSE","","","","TMPL_ELSE", "</TMPL_IF"], {})
        self.assertEquals(tmplproc.process(f_tmpl),'')
        f_tmpl.init(TMPLTemplate.__version__, [], ["<TMPL_IF",'NOVAR',None,None,\
                                                   "<TMPL_ELSE","","","","TMPL_ELSE","</TMPL_IF"], {})
        self.assertEquals(tmplproc.process(f_tmpl),'TMPL_ELSE')


        f_tmpl.init(TMPLTemplate.__version__, [], ["<TMPL_UNLESS",'',None,None], {})
        self.assertRaises(TemplateException.TemplateException, tmplproc.process, f_tmpl)
        f_tmpl.init(TMPLTemplate.__version__, [], ["<TMPL_UNLESS",'var',None,None,\
                                                     'TMPL_UNLESS'], {})
        self.assertRaises(TemplateException.TemplateException, tmplproc.process, f_tmpl)
        f_tmpl.init(TMPLTemplate.__version__, [], ["<TMPL_UNLESS",'var',None,None,\
                                                 'TMPL_UNLESS','</TMPL_UNLESS'], {})
        self.assertEquals(tmplproc.process(f_tmpl),'')                 
        f_tmpl.init(TMPLTemplate.__version__, [], ["<TMPL_UNLESS",'NOVAR',None,None,\
                                                 'TMPL_UNLESS',"</TMPL_UNLESS"], {})
        self.assertEquals(tmplproc.process(f_tmpl),'TMPL_UNLESS')


        f_tmpl.init(TMPLTemplate.__version__, [], ["<TMPL_IF",'',None,None], {})
        self.assertRaises(TemplateException.TemplateException, tmplproc.process, f_tmpl)
        f_tmpl.init(TMPLTemplate.__version__, [], ["<TMPL_IF",'var',None,None,\
                                                    '<TMPL_GETTEXT', 'TMPL_IF','',''], {})
        self.assertRaises(TemplateException.TemplateException, tmplproc.process, f_tmpl)
        f_tmpl.init(TMPLTemplate.__version__, [], ["<TMPL_IF",'var',None,None,\
                                                    '<TMPL_GETTEXT', 'TMPL_IF','','',"</TMPL_IF"], {})
        self.assertEquals(tmplproc.process(f_tmpl),'TMPL_IF')
        f_tmpl.init(TMPLTemplate.__version__, [], ["<TMPL_IF",'NOVAR',None,None,\
                                                    '<TMPL_GETTEXT', 'TMPL_IF','','',"</TMPL_IF"], {})
        self.assertEquals(tmplproc.process(f_tmpl),'')


        f_tmpl.init(TMPLTemplate.__version__, [], ["<TMPL_LOOP",'',None,None], {})
        self.assertRaises(TemplateException.TemplateException, tmplproc.process, f_tmpl)
        f_tmpl.init(TMPLTemplate.__version__, [], ["<TMPL_LOOP",'var',None,None,\
                                                   '<TMPL_GETTEXT', "Loop 3 times ","","","</TMPL_LOOP"], {})
        self.assertEquals(tmplproc.process(f_tmpl), "Loop 3 times Loop 3 times Loop 3 times ")
        f_tmpl.init(TMPLTemplate.__version__, [], ["<TMPL_LOOP",'NOVAR',None,None,\
                                                   '<TMPL_GETTEXT', "Loop 3 times ","","","</TMPL_LOOP"], {})
        self.assertEquals(tmplproc.process(f_tmpl), "")
        f_tmpl.init(TMPLTemplate.__version__, [], ["<TMPL_LOOP",'novar',None,None,\
                                                   '<TMPL_GETTEXT', "Loop 3 times ","",""],{})
        self.assertRaises(TemplateException.TemplateException, tmplproc.process, f_tmpl)


        f_tmpl.init(TMPLTemplate.__version__, [], ["<TMPL_VAR","",None,None], {})
        self.assertRaises(TemplateException.TemplateException, tmplproc.process, f_tmpl)        
        f_tmpl.init(TMPLTemplate.__version__, [], ["<TMPL_VAR","var1",None,None,\
                                                   "<TMPL_VAR","var2",None,None], {})
        self.assertEquals(tmplproc.process(f_tmpl), 'HREF&lt;HREF&gt;')
        
        # remove tmp dir
        rm_f(os.path.join(path, "tmp"))
        
    def test_find_value(self):
	"""
        Test find_value
	"""
        tmpl = TMPLTemplateProcessor.TMPLTemplateProcessor()
        tmpl.set('var1', 1)
        tmpl.set('var2', 2)
        self.assertEquals(tmpl.find_value('var1',[], 0, 0), 1)
        tmpl.set('List', [1,2,3])    
        self.assertEquals(tmpl.find_value('List',[], 0, 0), 3)
        self.assertEquals(tmpl.find_value('Nolist',[], 0, 0), 0)
        self.assertEquals(tmpl.find_value('var',[], 0, 0), '')

    def test_instance_boundary(self):
        templateprocessor = TMPLTemplateProcessor.TMPLTemplateProcessor()

        tested = sets.Set(['init', 'escape', 'magic_var', 'get', 
                           '__setitem__', '__getitem__', '__delitem__', 'has_key', 
                           'keys', 'setlogger', 'find_value', 'is_ordinary_var', ])

        all_dir = tested | sets.Set(dir(templateprocessor))

        self.assertEquals(all_dir, sets.Set(dir(self.__testee)))

    def test_class_boundary(self):

        base_set = sets.Set()
        for base in TMPLTemplateProcessor.TMPLTemplateProcessor.__bases__:
            base_set |= sets.Set(dir(base))

        tested = sets.Set(['init', 'escape', 'magic_var', 'get', 
                           '__setitem__', '__getitem__', '__delitem__', 'has_key', 
                           'keys', 'setlogger', 'find_value', 'is_ordinary_var', ])

        all_dir = tested | base_set

        self.assertEquals(all_dir, sets.Set(dir(TMPLTemplateProcessor.TMPLTemplateProcessor)))





