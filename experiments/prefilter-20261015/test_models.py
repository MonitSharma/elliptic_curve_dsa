import random,unittest
import walk_model as m

class PermutationTests(unittest.TestCase):
    def test_all_small_words_including_off_promise_inputs(self):
        for width in range(4,10):
            for word in range(1<<width):
                for extra in range(4):
                    self.assertEqual(m.inverse_barrel(word,width,extra),m.inverse_barrel_literal(word,width,extra))

    def test_full_sized_signed_words_and_boundaries(self):
        rng=random.Random(20261015)
        for width in range(4,259):
            words=[0,1,(1<<width)-1,1<<(width-1),rng.getrandbits(width)]
            for word in words:
                for extra in range(4):
                    self.assertEqual(m.inverse_barrel(word,width,extra),m.inverse_barrel_literal(word,width,extra))

if __name__=='__main__':unittest.main()
