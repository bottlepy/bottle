import unittest
import sys, os.path
from bottle import SimpleTemplate, TemplateError

class TestSimpleTemplate(unittest.TestCase):
    def testElse1(self):
        tpl1 = """
               %if 1:
               {{"Hello"}}
               %else :
               {{"Goodbye"}}
               %end
               """
        self.assertEqual("Hello", ''.join(SimpleTemplate(tpl1).render()).strip())
    def testElse2(self):
        tpl2 = """
               %if 1:
               {{"Hello"}}
               %else:
               {{"Goodbye"}}
               %end
               """
        self.assertEqual("Hello", ''.join(SimpleTemplate(tpl2).render()).strip())



if __name__ == '__main__':
    unittest.main()

