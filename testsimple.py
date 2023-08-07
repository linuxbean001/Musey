import unittest
import simple1
class TestCap(unittest.TestCase):
    def text_one_word(self):
        text = "Python"
        result = simple1.captext(text)
        self.assertEquals(result,"Python")  
    def text_multiple_word(self):
        text = "monty python"
        result = simple1.captext(text)
        self.assertEquals(result,"Monty Python")
if __name__=='__main__':
    unittest.main()


  


