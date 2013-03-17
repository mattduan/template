"""
PyUnit TestCase for TMPLTemplate.

$Id: testTMPLTemplate.py 3193 2010-11-10 14:22:01Z duan $
"""

__version__= "$Revision: 3193 $"[11:-2]


import os, os.path
import sys
import time
import md5
import unittest

import cPickle

import template.TMPLTemplate as TMPLTemplate
import template.TemplateException as TemplateException

def rm_f(top):
    for root, dirs, files in os.walk(top, topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))
    os.rmdir(top)


class testTMPLTemplate(unittest.TestCase):

    def setUp(self):
        self.__path = sys.modules[self.__module__].__path__
        
        # create a tmp dir
        os.mkdir(os.path.join(self.__path, "tmp"))
        
        self.__tmpl_filename = 'tmp/test.tmpl'
        self.__log_filename  = 'tmp/testTMPLTemplate.log'

        self.__test_filename = os.path.join(self.__path, self.__tmpl_filename)
        self.__test_logfile  = os.path.join(self.__path, self.__log_filename)

        if not os.access(self.__test_filename, os.F_OK):
            f = open(self.__test_filename, 'w')
            f.write("The test tmpl.")
            f.close()

        self.__test_content = "The test content."
        pass

    def tearDown(self):
        # remove tmp dir
        rm_f(os.path.join(self.__path, "tmp"))
        
    def test__init__(self):
	"""
        Test Constructor
        """
        f_tmpl = TMPLTemplate.TMPLTemplate(self.__test_filename)
        self.assertEquals(f_tmpl._file, self.__test_filename)
        self.assertEquals(f_tmpl._content, None)
        self.assertEquals(f_tmpl._mtime, os.path.getmtime(f_tmpl._file))    
        self.assertRaises(TemplateException.TemplateException, TMPLTemplate.TMPLTemplate, "file", None)
        self.assertEquals(f_tmpl._version, TMPLTemplate.__version__)
        self.assertEquals(f_tmpl._tokens, None)
        self.assertEquals(f_tmpl._compile_params, None)
        self.assertEquals(f_tmpl._include_mtimes, {})

    def testInit(self):
	"""
	  Test Init
	"""
        f_tmpl = TMPLTemplate.TMPLTemplate(self.__test_filename)
        f_tmpl.init(TMPLTemplate.__version__, [], [], {})
       
        self.assert_( f_tmpl.file() == self.__test_filename )
        self.assert_( f_tmpl.content() is None )
        self.assert_( f_tmpl._tokens == [] )
        self.assert_( f_tmpl._compile_params =={} )
        c_tmpl = TMPLTemplate.TMPLTemplate(self.__test_filename)
        self.assertRaises(TemplateException.TemplateException, c_tmpl.init, TMPLTemplate.__version__, "file", [], {})


    def testis_Uptodate(self):
	"""
        Test is_uptodate
	"""
        # file
        f_tmpl = TMPLTemplate.TMPLTemplate(self.__test_filename)
        f_tmpl.init(TMPLTemplate.__version__, [], [], {})

        # uptodate
        self.assert_( f_tmpl.is_uptodate() == 1 )

        # version change
        f_tmpl.init( "1.%s" % TMPLTemplate.__version__, [], [], {})
        self.assert_( f_tmpl.is_uptodate() == 0 )
        f_tmpl.init( TMPLTemplate.__version__, [], [], {} )

        # compile_params change
        self.assert_( f_tmpl.is_uptodate({1:1}) == 0 )

        # file mtime change
        time.sleep(1)
        f = open(self.__test_filename, 'w')
        f.write("The test tmpl.")
        f.close()
        self.assert_( f_tmpl.is_uptodate() == 0 )

        # content
        c_tmpl = TMPLTemplate.TMPLTemplate(None, content=self.__test_content)
        c_tmpl.init(TMPLTemplate.__version__, [], [], {})

        self.assert_( c_tmpl.is_uptodate() == 1 )
        

    def testGetId(self):
	"""
        Test GetId
	"""
        f_tmpl = TMPLTemplate.TMPLTemplate(self.__test_filename)

        self.assert_(f_tmpl.getid() == self.__test_filename)

        c_tmpl = TMPLTemplate.TMPLTemplate(None, content=self.__test_content)
        self.assert_(c_tmpl.getid() == md5.new(self.__test_content).hexdigest())


    def testPickle(self):
       
        # create tmp logger
        f_tmpl = TMPLTemplate.TMPLTemplate(self.__test_filename)
        f_tmpl.init(TMPLTemplate.__version__, [], [], {})

        f = None
        try:
            filename = self.__test_filename + 'c'
            f = open(filename, "wb")
            cPickle.dump(f_tmpl, f, 2)
        finally:
            if f:
                f.close()

        f = None
        try:
            filename = self.__test_filename + 'c'
            f = open(filename, "rb")
            f_tmpl2 = cPickle.load(f)
        finally:
            if f:
                f.close()

        self.assert_(f_tmpl2.file() == f_tmpl.file())


    def test_Tokens(self):
	"""
        Test Tokens
	"""
        f_tmpl = TMPLTemplate.TMPLTemplate(self.__test_filename)
        f_tmpl.init(TMPLTemplate.__version__, [], ['tokens'], {})       
        self.assertEquals(f_tmpl._tokens, ['tokens'])

    def test_file(self):
	"""
        Test file
	"""
        f_tmpl = TMPLTemplate.TMPLTemplate(self.__test_filename)
        self.assertEquals(f_tmpl.file(), self.__test_filename)

    def test_content(self):
	"""
        Test content
	"""
        f_tmpl = TMPLTemplate.TMPLTemplate(self.__test_filename, self.__test_content)
        self.assertEquals(f_tmpl.content(), self.__test_content)

      
    def test__getstate__(self):
	"""
        Test __getstate__
	"""
        f_tmpl = TMPLTemplate.TMPLTemplate(self.__test_filename,  self.__test_content)
        dict = f_tmpl.__getstate__()
        self.assertEquals(dict.keys(), ['_compile_params', '_mtime', '_content', '_file', '_version', '_include_mtimes', '_tokens'])

    def test__setstate__(self):
        """
        Test __setstate__
	"""
        f_tmpl = TMPLTemplate.TMPLTemplate(self.__test_filename)
        f_tmpl.init(TMPLTemplate.__version__, [], [], {})
        dict = f_tmpl.__getstate__()       
        f_tmpl.__setstate__(dict)
        self.assertEquals(f_tmpl.__dict__.keys(), ['_compile_params', '_mtime', '_content', '_logger', '_file', '_version', 'debug', '_include_mtimes', '_tokens'])
 
