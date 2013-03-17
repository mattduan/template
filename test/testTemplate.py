"""
PyUnit TestCase for Template.

$Id: testTemplate.py 3193 2010-11-10 14:22:01Z duan $
"""

__version__= "$Revision: 3193 $"[11:-2]

import unittest
import sets
import os

# more imports
import template.Template as Template
import template.TemplateException as TemplateException


# test fixture


class testTemplate(unittest.TestCase):

    def setUp(self):
        fl = open('/home/fh/file.txt','w')
        self.__testee = Template.Template('/home/fh/file.txt')

    def tearDown(self):
        self.__testee = None

    def test___init__(self):
        """
        test Constructor.
        """
        tmpl = Template.Template('/home/fh/file.txt','content')
        self.assertEquals(tmpl._file, '/home/fh/file.txt')
        self.assertEquals(tmpl._content, 'content')
        self.assertEquals(tmpl._mtime, os.path.getmtime('/home/fh/file.txt'))
       
        self.assertRaises(TemplateException.TemplateException, Template.Template, 'file2')
        self.assertRaises(TemplateException.TemplateException, Template.Template, 'fh')
        
    def test_is_uptodate(self):
        """
        test is_uptodate
        """
        tmpl = Template.Template('/home/fh/file.txt','content')
        self.assertEquals(tmpl.is_uptodate(), 1)       
    
    def test_getid(self):
        """
        test getid
        """
        tmpl = Template.Template('/home/fh/file.txt','content')
        self.assertEquals(tmpl.getid(), '/home/fh/file.txt')
       
     
    def test_instance_boundary(self):
        """
        Make sure the test covers every method in a Template instance.
        """
        tmpl = Template.Template('/home/fh/file.txt')

        tested = sets.Set(['__module__', '__doc__', '__init__', 'is_uptodate', 
                           'getid', ])

        all_dir = tested | sets.Set(dir(tmpl))

        self.assertEquals(all_dir, sets.Set(dir(self.__testee)))
    
    def test_class_boundary(self):
        """
        Make sure the test covers every method in a Template class.
        """
        base_set = sets.Set()
        for base in Template.Template.__bases__:
            base_set |= sets.Set(dir(base))

        tested = sets.Set(['__module__', '__doc__', '__init__', 'is_uptodate', 
                           'getid', ])

        all_dir = tested | base_set

        self.assertEquals(all_dir, sets.Set(dir(Template.Template)))

    
