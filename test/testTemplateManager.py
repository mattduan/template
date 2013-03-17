"""
PyUnit TestCase for TemplateManager.

$Id: testTemplateManager.py 3193 2010-11-10 14:22:01Z duan $
"""

__version__= "$Revision: 3193 $"[11:-2]

import unittest
import sets

# more imports
import template.TemplateException as TemplateException
import template.TemplateManager as TemplateManager
import template.Template as Template
#  test fixture



class testTemplateManager(unittest.TestCase):

    def setUp(self):
        self.__testee = TemplateManager.TemplateManager()

    def tearDown(self):
        self.__testee = None

    def test___init__(self):
        """
        test Constructor
        """
        mag = TemplateManager.TemplateManager()
        self.assertEquals(mag._cache, 10)
        self.assertEquals(mag._precompile, 1)
        self.assertEquals(mag._templates, {})

    def test_prepare(self):
        """
        test prepare
        """
        mag = TemplateManager.TemplateManager()
        self.assertRaises(TemplateException.NotImplementedException,
                            mag.prepare, None)
       
    def test_update(self):
        """
        test update
        """
        mag = TemplateManager.TemplateManager()
        self.assertRaises(TemplateException.NotImplementedException,
                           mag.update, Template.Template)
                           
    def test_instance_boundary(self):
        """
        Make sure the test covers every method in a TemplateManager instance.
        """
        mag = TemplateManager.TemplateManager()
        tested = sets.Set(['__module__', '__doc__', '__init__', 'prepare', 
                           'update', ])

        all_dir = tested | sets.Set(dir(mag))

        self.assertEquals(all_dir, sets.Set(dir(self.__testee)))

    def test_class_boundary(self):
        """
        Make sure the test covers every method in a TemplateManager class.
        """
        base_set = sets.Set()
        for base in TemplateManager.TemplateManager.__bases__:
            base_set |= sets.Set(dir(base))

        tested = sets.Set(['__module__', '__doc__', '__init__', 'prepare', 
                           'update', ])

        all_dir = tested | base_set

        self.assertEquals(all_dir, sets.Set(dir(TemplateManager.TemplateManager)))


