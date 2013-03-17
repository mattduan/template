"""
PyUnit TestCase for TMPLTemplateManager.

$Id: testTMPLTemplateManager.py 3193 2010-11-10 14:22:01Z duan $
"""

__version__= "$Revision: 3193 $"[11:-2]

import unittest
import sets
import sys
import os
import cPickle
# more imports
import template.TemplateException as TemplateException
import template.TMPLTemplateManager as TMPLTemplateManager
import template.TemplateManager as TemplateManager
import template.TMPLTemplate as TMPLTemplate

# test fixture

def rm_f(top):
    for root, dirs, files in os.walk(top, topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))
    os.rmdir(top)

def create_file(filename, content, always=0):
    if not os.access(filename, os.F_OK) or always:
        f = open(filename, 'w')
        f.write(content)
        f.close()

INCLUDE_DIR = "."
class testTMPLTemplateCompiler(unittest.TestCase):

    def setUp(self):
        self.__testee = TMPLTemplateManager.TMPLTemplateCompiler()
        self.__path = sys.modules[self.__module__].__path__
        
        # create a tmp dir
        os.mkdir(os.path.join(self.__path, "tmpCpl"))
        
        self.__tmpl_filename = os.path.join(self.__path, 'tmpCpl/test.tmpl')       
        create_file(self.__tmpl_filename, "Test 1")
        self.__tmpl_filename2 = os.path.join(self.__path, 'tmpCpl/test2.tmpl') 
        create_file(self.__tmpl_filename2, "Test 2")

    def tearDown(self):
        self.__testee = None
	  # remove tmp dir
        rm_f(os.path.join(self.__path, "tmpCpl"))

    def test___init__(self):
	"""
        Test constructor
	"""
        self.assertEquals(self.__testee._include, 1)
        self.assertEquals(self.__testee._max_include, 5)
        self.assertEquals(self.__testee._comments, 1)
        self.assertEquals(self.__testee._gettext, 0)
        self.assertEquals(self.__testee._include_files, [])
        self.assertEquals(self.__testee._include_level, 0) 

    def test_compile(self):
	"""
        Test compile
	"""
        template = self.__testee.compile(self.__tmpl_filename)
        self.assertEquals(self.__testee._include_path, \
                          os.path.join(os.path.dirname(self.__tmpl_filename),INCLUDE_DIR ))
        self.assertEquals(template._version, TMPLTemplate.__version__)
        self.assertEquals(template._tokens, ['Test 1'])
        self.assertEquals(template._compile_params, (self.__testee._include,                  self.__testee._max_include, self.__testee._comments, self.__testee._gettext))
        self.assertEquals(template._mtime, os.path.getmtime(self.__tmpl_filename))  

        self.assertEquals(template._file, self.__tmpl_filename)
        self.assertEquals(template._content, None)
        self.assertEquals(template._include_mtimes, {})

    def test_gettext_tokens(self):
        """
        Test find_param
	"""     
        tokens = []
        self.__testee.gettext_tokens(tokens,'string')
        self.assertEquals(tokens, ['string'])
        self.__testee.gettext_tokens(tokens,'string\\\\string')
        self.assertEquals(tokens, ['string','string\\string'])
        tokens = []
        self.__testee.gettext_tokens(tokens,'string\\string')
        self.assertEquals(tokens, ['string\\string'])
        tokens = []
        self.__testee.gettext_tokens(tokens,'string\\[string')
        self.assertEquals(tokens, ['string[string'])
        tokens = []
        self.__testee.gettext_tokens(tokens,'string\\]string')
        self.assertEquals(tokens, ['string]string'])
        tokens = []
        self.__testee.gettext_tokens(tokens,'string[[sth]]string')
        self.assertEquals(tokens,['string', '<TMPL_GETTEXT', 'sth', None, None, 'string'])


    def test_find_param(self):
	"""
        Test find_param
	"""
        self.assertEquals(self.__testee.find_param('NO',['name1=val1','name2=val2']), None)
        self.assertEquals(self.__testee.find_param('name2',['name1=val1','name2=val2']), 'val2')
        self.assertEquals(self.__testee.find_param('name1',['name1="val1"','name2=val2']), 'val1')
        self.assertRaises(TemplateException.TemplateException,\
                          self.__testee.find_param,'name',['='])

    def test_find_name(self):
        """
        Test find_name
	"""
        self.assertEquals(self.__testee.find_name(['NAME=val','name2=val2']), 'val')
        self.assertEquals(self.__testee.find_name(['NAME','name2=val2']), 'NAME')

    def test_read(self):
	"""
        Test read
	"""
        self.assertEquals(self.__testee.read(self.__tmpl_filename), "Test 1")
        self.assertRaises(TemplateException.TemplateException, self.__testee.read,'/home/file.txt')

    def test_add_gettext_token(self):
	"""
        Test add_gettext_token
	"""
        tokens=[]
        self.__testee.add_gettext_token(tokens,'test')
        self.assertEquals(tokens, ["<TMPL_GETTEXT", "test", None, None])

    def test_parse(self):
        self.assertEquals(self.__testee.parse('template_data### comment'), ['template_data'])
        

    def test_strip_brackets(self):
	"""
        Test strip_brackets
	"""
        self.assertEquals(self.__testee.strip_brackets("<!-- TMPL_somefool"), "TMPL_some")
        self.assertEquals(self.__testee.strip_brackets("<!-- /TMPL_somefool"), "/TMPL_some")
        self.assertEquals(self.__testee.strip_brackets("<somefool"), "somefoo")
    

    def test_remove_comments(self):
        """
        Test remove_comments
	"""
        self.assertEquals(self.__testee.remove_comments('begin### something'),"begin")
       
       
    
    def test_include_templates(self):
        """
        Test include_templates
	"""
        self.assertRaises(TemplateException.TemplateException, self.__testee.include_templates, ["<TMPL_INCLUDE",""])
        self.__testee.compile(self.__tmpl_filename)
        self.__testee.compile(self.__tmpl_filename2)
        tokens = ["<TMPL_INCLUDE", "test.tmpl", "", "", "<TMPL_INCLUDE","test2.tmpl"]
        self.__testee.include_templates(tokens)
        self.assertEquals(tokens, ["Test 1", "Test 2"])
        self.assertEquals(self.__testee._include_files, [os.path.join(self.__testee._include_path, "test.tmpl"),os.path.join(self.__testee._include_path, "test2.tmpl")])

    def test_tokenize(self):
        """
        Test tokenize
	"""
        self.assertEquals(self.__testee.tokenize("<TMPL_ NAME=val ESCAPE=escape GLOBAL=global#"),\
['<TMPL_', 'val', 'escape', 'global'])
        self.assertEquals(self.__testee.tokenize\
("<!-- /TMPL_ NAME=val ESCAPE=escape GLOBAL=global####"), ['</TMPL_', 'val', 'escape', 'global'])
        self.assertEquals(self.__testee.tokenize("NAME=val ESCAPE=escape GLOBAL=global"),\
["NAME=val ESCAPE=escape GLOBAL=global"])
        
        testee = TMPLTemplateManager.TMPLTemplateCompiler(1,5,1,1)
        self.assertEquals(testee.tokenize("s\\\\s"), ['s\\s'])
       
    def test_compile_string(self):
	"""
        Test compile_string
	"""
        template = self.__testee.compile_string("Compile_string### comments")
        self.assertEquals(template._version, TMPLTemplate.__version__)
        self.assertEquals(template._tokens, ['Compile_string'])
        self.assertEquals(template._compile_params, (self.__testee._include,                  self.__testee._max_include, self.__testee._comments, self.__testee._gettext))
        self.assertEquals(template._mtime, None)  
        self.assertEquals(template._file , None)
        self.assertEquals(template._content, "Compile_string### comments")
        self.assertEquals(template._include_mtimes, {})

    def test_find_directive(self):
	"""
        Test find directive
	"""
        self.assertEquals(self.__testee.find_directive(["TMPL_SOME"]), "<TMPL_SOME")
      
    def test_instance_boundary(self):
	"""
        Make sure the test cover every method in a TMPLTemplateManager instance
	"""
        mg = TMPLTemplateManager.TMPLTemplateCompiler()

        tested = sets.Set(['compile', '__module__', 'gettext_tokens', 'find_param', 
                           'read', 'add_gettext_token', '__doc__', 'parse', 
                           'strip_brackets', 'remove_comments', 'find_name', 'include_templates', 
                           'tokenize', 'compile_string', 'find_directive', '__init__', ])

        all_dir = tested | sets.Set(dir(mg))

        self.assertEquals(all_dir, sets.Set(dir(self.__testee)))

    def test_class_boundary(self):
	"""
        Make sure the test cover every method in a TMPLTemplateManager class
	"""
        base_set = sets.Set()
        for base in TMPLTemplateManager.TMPLTemplateCompiler.__bases__:
            base_set |= sets.Set(dir(base))

        tested = sets.Set(['compile', '__module__', 'gettext_tokens', 'find_param', 
                           'read', 'add_gettext_token', '__doc__', 'parse', 
                           'strip_brackets', 'remove_comments', 'find_name', 'include_templates', 
                           'tokenize', 'compile_string', 'find_directive', '__init__', ])

        all_dir = tested | base_set

        self.assertEquals(all_dir, sets.Set(dir(TMPLTemplateManager.TMPLTemplateCompiler)))

class testTMPLTemplateManager(unittest.TestCase):

    def setUp(self):
        self.__path = sys.modules[self.__module__].__path__
        
        # create a tmp dir
        os.mkdir(os.path.join(self.__path, "tmp"))
        
        self.__tmpl_filename1 = os.path.join(self.__path, 'tmp/test1.tmpl')
        self.__tmpl_filename2 = os.path.join(self.__path, 'tmp/test2.tmpl')
        self.__tmpl_filename3 = os.path.join(self.__path, 'tmp/test3.tmpl')
        
        create_file(self.__tmpl_filename1, "Test 1")
        create_file(self.__tmpl_filename2, "Test 2")
        create_file(self.__tmpl_filename3, "Test 3")
        
        self.ttm_no_cache = TMPLTemplateManager.TMPLTemplateManager(cache=0, precompile=1)
        self.ttm_cache_1  = TMPLTemplateManager.TMPLTemplateManager(cache=1, precompile=1)
        self.ttm_cache_2  = TMPLTemplateManager.TMPLTemplateManager(cache=2, precompile=1)

        self.__test_content = "The test content."

       

    def tearDown(self):
        self.ttm_no_cache = None
        self.ttm_cache_1  = None
        self.ttm_cache_2  = None

        # remove tmp dir
        rm_f(os.path.join(self.__path, "tmp"))

    def test_init(self):
	"""
        Test Constructor
	"""
        self.assertRaises(TemplateException.TemplateException, TMPLTemplateManager.TMPLTemplateManager, -1 , 1)
        self.assertEquals(self.ttm_cache_1._cache, 1)	  
        self.assertEquals(self.ttm_cache_1._precompile, 1)
        self.assertEquals(self.ttm_cache_1._templates, {})
        self.assertEquals(self.ttm_cache_1._ref_counts, {})
        self.assertEquals(self.ttm_cache_1._include, 1)
        self.assertEquals(self.ttm_cache_1._max_include, 5)
        self.assertEquals(self.ttm_cache_1._comments, 1)
        self.assertEquals(self.ttm_cache_1._gettext, 0)        

    def testinit(self):
	"""
        Test init
	"""
        self.ttm_cache_1.init(include=1, max_include=5, comments=1, gettext=0)
        self.assertEquals(self.ttm_cache_1._include, 1)
        self.assertEquals(self.ttm_cache_1._max_include, 5)
        self.assertEquals(self.ttm_cache_1._comments, 1)
        self.assertEquals(self.ttm_cache_1._gettext, 0)
        self.assertEquals(self.ttm_cache_1.debug("TMPLTemplate Manager INIT DONE"),"TMPLTemplate Manager INIT DONE")

    def testPrepare(self):
        """ prepare(file, content)
            file, content:
            1. return compiled if no cache
            2. return cached if cache
          """
        prepare1 = self.ttm_no_cache.prepare(self.__tmpl_filename1)
        prepare1 = self.ttm_no_cache.prepare(self.__tmpl_filename1)
        prepare1 = self.ttm_no_cache.prepare(self.__tmpl_filename1)
        prepare2 = self.ttm_no_cache.prepare(self.__tmpl_filename2)
        prepare3 = self.ttm_no_cache.prepare(self.__tmpl_filename3)
        
        self.assert_(prepare1.file() == self.__tmpl_filename1)
        self.assert_(prepare2.file() == self.__tmpl_filename2)
        self.assert_(prepare3.file() == self.__tmpl_filename3)

        prepare4 = self.ttm_cache_1.prepare(self.__tmpl_filename1)
        prepare4 = self.ttm_cache_1.prepare(self.__tmpl_filename1)
        prepare4 = self.ttm_cache_1.prepare(self.__tmpl_filename1)
        prepare5 = self.ttm_cache_1.prepare(self.__tmpl_filename2)
        prepare6 = self.ttm_cache_1.prepare(self.__tmpl_filename3)

        self.assert_(prepare4.file() == self.__tmpl_filename1)
        self.assert_(prepare5.file() == self.__tmpl_filename2)
        self.assert_(prepare6.file() == self.__tmpl_filename3)

        prepare7 = self.ttm_cache_2.prepare(self.__tmpl_filename1)
        prepare8 = self.ttm_cache_2.prepare(self.__tmpl_filename2)
        prepare8 = self.ttm_cache_2.prepare(self.__tmpl_filename2)
        prepare8 = self.ttm_cache_2.prepare(self.__tmpl_filename2)
        prepare9 = self.ttm_cache_2.prepare(self.__tmpl_filename3)
        prepare9 = self.ttm_cache_2.prepare(self.__tmpl_filename3)
        prepare9 = self.ttm_cache_2.prepare(self.__tmpl_filename3)

        self.assert_(prepare7.file() == self.__tmpl_filename1)
        self.assert_(prepare8.file() == self.__tmpl_filename2)
        self.assert_(prepare9.file() == self.__tmpl_filename3)

        prepare10 = self.ttm_no_cache.prepare(None, self.__test_content)
        prepare10 = self.ttm_no_cache.prepare(None, self.__test_content)
        prepare10 = self.ttm_no_cache.prepare(None, self.__test_content)
        prepare10 = self.ttm_no_cache.prepare(None, self.__test_content)
        prepare11 = self.ttm_cache_1.prepare(None, self.__test_content)
        prepare12 = self.ttm_cache_2.prepare(None, self.__test_content)
        self.assert_(prepare10.file() is None)
        self.assert_(prepare10.content() == self.__test_content)
        self.assert_(prepare11.file() is None)
        self.assert_(prepare11.content() == self.__test_content)
        self.assert_(prepare12.file() is None)
        self.assert_(prepare12.content() == self.__test_content)

    def testCompiled(self):
	"""
        Test Compiled
	"""
        compiled1 = self.ttm_no_cache.compiled(self.__tmpl_filename1)
        compiled2 = self.ttm_no_cache.compiled(self.__tmpl_filename2)
        compiled3 = self.ttm_no_cache.compiled(self.__tmpl_filename3)
        
        compiled1 = self.ttm_no_cache.compiled(self.__tmpl_filename1)
        compiled1 = self.ttm_no_cache.compiled(self.__tmpl_filename1)
        
        self.assert_(compiled1.file() == self.__tmpl_filename1)
        self.assert_(compiled2.file() == self.__tmpl_filename2)
        self.assert_(compiled3.file() == self.__tmpl_filename3)

        compiled4 = self.ttm_cache_1.compiled(self.__tmpl_filename1)
        compiled5 = self.ttm_cache_1.compiled(self.__tmpl_filename2)
        compiled6 = self.ttm_cache_1.compiled(self.__tmpl_filename3)
        compiled4 = self.ttm_cache_1.compiled(self.__tmpl_filename1)
        compiled4 = self.ttm_cache_1.compiled(self.__tmpl_filename1)

        self.assert_(compiled4.file() == self.__tmpl_filename1)
        self.assert_(compiled5.file() == self.__tmpl_filename2)
        self.assert_(compiled6.file() == self.__tmpl_filename3)

        compiled7 = self.ttm_cache_2.compiled(self.__tmpl_filename1)
        compiled8 = self.ttm_cache_2.compiled(self.__tmpl_filename2)
        compiled9 = self.ttm_cache_2.compiled(self.__tmpl_filename3)
        compiled8 = self.ttm_cache_2.compiled(self.__tmpl_filename2)
        compiled9 = self.ttm_cache_2.compiled(self.__tmpl_filename3)

        self.assert_(compiled7.file() == self.__tmpl_filename1)
        self.assert_(compiled8.file() == self.__tmpl_filename2)
        self.assert_(compiled9.file() == self.__tmpl_filename3)

        compiled10 = self.ttm_no_cache.compiled(None, self.__test_content)
        compiled10 = self.ttm_no_cache.compiled(None, self.__test_content)
        compiled10 = self.ttm_no_cache.compiled(None, self.__test_content)
        compiled11 = self.ttm_cache_1.compiled(None, self.__test_content)
        compiled12 = self.ttm_cache_2.compiled(None, self.__test_content)
        self.assert_(compiled10.file() is None)
        self.assert_(compiled10.content() == self.__test_content)
        self.assert_(compiled11.file() is None)
        self.assert_(compiled11.content() == self.__test_content)
        self.assert_(compiled12.file() is None)
        self.assert_(compiled12.content() == self.__test_content)

    
    def testUpdate(self):
	"""
        Test Update
	"""
        compiled1 = self.ttm_no_cache.compiled(self.__tmpl_filename1)
        compiled2 = self.ttm_no_cache.compiled(self.__tmpl_filename2)
        compiled3 = self.ttm_no_cache.compiled(self.__tmpl_filename3)
        
        compiled4 = self.ttm_cache_1.compiled(self.__tmpl_filename1)
        compiled5 = self.ttm_cache_1.compiled(self.__tmpl_filename2)
        compiled6 = self.ttm_cache_1.compiled(self.__tmpl_filename3)

        compiled7 = self.ttm_cache_2.compiled(self.__tmpl_filename1)
        compiled8 = self.ttm_cache_2.compiled(self.__tmpl_filename2)
        compiled9 = self.ttm_cache_2.compiled(self.__tmpl_filename3)

        compiled10 = self.ttm_no_cache.compiled(None, self.__test_content)
        compiled11 = self.ttm_cache_1.compiled(None, self.__test_content)
        compiled12 = self.ttm_cache_2.compiled(None, self.__test_content)

        update1 = self.ttm_no_cache.update(compiled1)
        update2 = self.ttm_no_cache.update(compiled2)
        update3 = self.ttm_no_cache.update(compiled3)

        self.assert_(update1.file() == self.__tmpl_filename1)
        self.assert_(update2.file() == self.__tmpl_filename2)
        self.assert_(update3.file() == self.__tmpl_filename3)

        update4 = self.ttm_cache_1.update(compiled4)
        update5 = self.ttm_cache_1.update(compiled5)
        update6 = self.ttm_cache_1.update(compiled6)

        self.assert_(update4.file() == self.__tmpl_filename1)
        self.assert_(update5.file() == self.__tmpl_filename2)
        self.assert_(update6.file() == self.__tmpl_filename3)

        update7 = self.ttm_cache_2.update(compiled7)
        update8 = self.ttm_cache_2.update(compiled8)
        update9 = self.ttm_cache_2.update(compiled9)

        self.assert_(update7.file() == self.__tmpl_filename1)
        self.assert_(update8.file() == self.__tmpl_filename2)
        self.assert_(update9.file() == self.__tmpl_filename3)

        update10 = self.ttm_no_cache.update(compiled10)
        update11 = self.ttm_cache_1.update(compiled11)
        update12 = self.ttm_cache_2.update(compiled12)

        self.assert_(update10.file() is None)
        self.assert_(update10.content() == self.__test_content)
        self.assert_(update11.file() is None)
        self.assert_(update11.content() == self.__test_content)
        self.assert_(update12.file() is None)
        self.assert_(update12.content() == self.__test_content)

    def test_lock_file(self):
	"""
        Test lock_file
	"""
        file = open(self.__tmpl_filename1,'w')
        self.assertRaises(TemplateException.TemplateException,\
                          self.ttm_cache_1.lock_file, file, 4)
        file.close()
       

    def testCompile(self):
        """
        Test Compile
	"""
        tmpl = self.ttm_no_cache.compile(self.__tmpl_filename1)
        self.assert_(tmpl.file() == self.__tmpl_filename1)
        self.assert_(tmpl.tokens() == ['Test 1'])
        self.assert_(tmpl.content() == None)


  
    def test_compile_string(self):
	"""
        Test compile_strint
	"""
        tmpl = self.ttm_no_cache.compile_string("context### coments")
        self.assert_(tmpl.file() is None)
        self.assert_(tmpl.content() == "context### coments")
      
    def test_is_precompiled(self):
	"""
        Test is_precompiled
	"""
        self.assertEquals(self.ttm_no_cache.is_precompiled(self.__tmpl_filename1), 0) 
        self.ttm_no_cache.compiled(self.__tmpl_filename1)
        self.assertEquals(self.ttm_no_cache.is_precompiled(self.__tmpl_filename1), 1)   

    def test_load_precompiled(self):
	"""
        Test load_precompiled
	"""
        self.assertRaises(TemplateException.TemplateException,\
                 self.ttm_no_cache.load_precompiled, self.__tmpl_filename1)
        self.ttm_no_cache.compiled(self.__tmpl_filename1)

        template = self.ttm_no_cache.load_precompiled(self.__tmpl_filename1)
        self.assertEquals(template.file(), self.__tmpl_filename1)
   

    def test_save_precompiled(self):
	"""
        Test load_precompiled
	"""
        tmpl = TMPLTemplate.TMPLTemplate(self.__tmpl_filename1)
        #tmpl = self.ttm_cache_1.prepare(self.__tmpl_filename1)
        #print tmpl.file()
        
        self.assertRaises(TemplateException.TemplateException, \
                        self.ttm_no_cache.load_precompiled, self.__tmpl_filename1)
        self.ttm_no_cache.save_precompiled(tmpl)
        tmpl = self.ttm_no_cache.load_precompiled(self.__tmpl_filename1)
        self.assertEquals(tmpl.file(), self.__tmpl_filename1)

    def test_instance_boundary(self):
        templatemanager = TMPLTemplateManager.TMPLTemplateManager()

        tested = sets.Set(['init', 'compile', 'compiled', 'setlogger', 
                           'lock_file', 'compile_string', 'is_precompiled', 'load_precompiled', 
                           'save_precompiled', ])

        all_dir = tested | sets.Set(dir(templatemanager))

        self.assertEquals(all_dir, sets.Set(dir(self.ttm_no_cache)))

    def test_class_boundary(self):
        base_set = sets.Set()
        for base in TMPLTemplateManager.TMPLTemplateManager.__bases__:
            base_set |= sets.Set(dir(base))

        tested = sets.Set(['init', 'compile', 'compiled', 'setlogger', 
                           'lock_file', 'compile_string', 'is_precompiled', 'load_precompiled', 
                           'save_precompiled', ])

        all_dir = tested | base_set

        self.assertEquals(all_dir, sets.Set(dir(TMPLTemplateManager.TMPLTemplateManager)))

