"""
PyUnit TestCase for TemplateProcessor.

$Id: testTemplateProcessor.py 3193 2010-11-10 14:22:01Z duan $
"""

__version__= "$Revision: 3193 $"[11:-2]


import unittest
import sets

# more imports
import template.TemplateException as TemplateException
import template.TemplateProcessor as TemplateProcessor

import template.Template as Template

# test fixture

class testTemplateProcessor(unittest.TestCase):

    def setUp(self):
        self.__testee = TemplateProcessor.TemplateProcessor()

    def tearDown(self):
        self.__testee = None

    def test_set(self):
        """
        test set
        """
        proc = TemplateProcessor.TemplateProcessor()    
        self.assertRaises(TemplateException.TemplateException,
                            proc.set, 'a', 1)
                                                   
    def test_setdict(self):
        """
        test setdict
        """
        proc = TemplateProcessor.TemplateProcessor()    
        self.assertRaises(TemplateException.TemplateException,
                            proc.setdict, {'a':1,'b':2})
                            
    def test_reset(self):
        """
        test reset
        """
        proc = TemplateProcessor.TemplateProcessor()    
        self.assertRaises(TemplateException.TemplateException,
                            proc.reset, 1)

    def test_process(self):
        """
        test process
        """
        proc = TemplateProcessor.TemplateProcessor()    
        self.assertRaises(TemplateException.TemplateException,
                            proc.process, Template.Template, 1)

    def test_instance_boundary(self):
        """
        Make sure the test covers every method in a TemplateProcessor instance.
        """
        proc = TemplateProcessor.TemplateProcessor()
        tested = sets.Set(['__module__', '__doc__', '__init__', 'set', 
                           'setdict', 'reset', 'process', ])

        all_dir = tested | sets.Set(dir(proc))

        self.assertEquals(all_dir, sets.Set(dir(self.__testee)))

    def test_class_boundary(self):
        """
        Make sure the test covers every method in a TemplateProcessor class.
        """
        base_set = sets.Set()
        for base in TemplateProcessor.TemplateProcessor.__bases__:
            base_set |= sets.Set(dir(base))

        tested = sets.Set(['__module__', '__doc__', '__init__', 'set', 
                           'setdict', 'reset', 'process', ])

        all_dir = tested | base_set

        self.assertEquals(all_dir, sets.Set(dir(TemplateProcessor.TemplateProcessor)))

