"""Formato covering-code/v1: expand(json) reproduz o código de data/codes, byte a byte na forma canônica.

Roda com:  python3 -m unittest discover -s tests -v   (só biblioteca padrão; pytest também serve)
"""
import copy
import glob
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts", "codes"))
import codefmt as cf  # noqa: E402

STRUCTURED = sorted(glob.glob(os.path.join(ROOT, "data", "structured", "*.json")))


def read(path, mode="r"):
    with open(path, mode) as f:
        return f.read()


def txt_of(js):
    return os.path.join(ROOT, "data", "codes", os.path.basename(js)[:-5] + ".txt")


def canonical_sha_of_txt(path):
    with open(path) as f:
        lines = f.read().split()
    return hashlib.sha256(("\n".join(sorted(lines)) + "\n").encode()).hexdigest()


class ExpandReproducesTxt(unittest.TestCase):
    def test_every_code_in_data_codes_has_a_structured_json(self):
        names = {os.path.basename(p)[:-4] for p in glob.glob(os.path.join(ROOT, "data", "codes", "*.txt"))}
        self.assertEqual(names, {os.path.basename(p)[:-5] for p in STRUCTURED})

    def test_expand_gives_exactly_the_canonical_sha256_of_the_txt(self):
        for js in STRUCTURED:
            with self.subTest(js=os.path.basename(js)):
                doc = cf.load(js)
                words = cf.check_doc(doc)
                self.assertEqual(cf.canonical_sha256(words), canonical_sha_of_txt(txt_of(js)))
                self.assertEqual(set(words), set(read(txt_of(js)).split()))

    def test_expand_cli_output_is_byte_identical_to_canonical_text(self):
        js = os.path.join(ROOT, "data", "structured", "q7_n9_R4_M1351.json")
        out = subprocess.run([sys.executable, os.path.join(ROOT, "scripts/codes/expand.py"), js],
                             capture_output=True, text=True, check=True).stdout
        self.assertEqual(hashlib.sha256(out.encode()).hexdigest(),
                         "54dbdade1337432303847d2fd0d1c13b506de08ba518e1694c5fb37ed0e81162")

    def test_known_structures_are_recorded(self):
        def shape(name):
            d = cf.load(os.path.join(ROOT, "data", "structured", name + ".json"))
            lb = d["linear_base"]
            return (lb["k"], len(lb["coset_syndromes"]),
                    [(len(b["generators"]), len(b["reps"])) for b in d["subcode_cosets"]], len(d["patch_words"]))
        self.assertEqual(shape("q7_n9_R4_M1351"), (3, 3, [(1, 46)], 0))
        self.assertEqual(shape("q7_n9_R4_M1285"), (3, 3, [(1, 36)], 4))
        self.assertEqual(shape("q7_n8_R3_M1887"), (3, 5, [], 172))

    def test_1285_parity_check_is_the_generator_matrix_of_gen_py(self):
        d = cf.load(os.path.join(ROOT, "data", "structured", "q7_n9_R4_M1285.json"))
        p = json.loads(read(os.path.join(ROOT, "data", "search", "p1285.json")))
        A = p["A"].split()
        self.assertEqual([h[6:] for h in d["linear_base"]["parity_check"]], A)

        def s(v):
            return "".join(str((v // 7**i) % 7) for i in range(6))

        self.assertEqual(sorted(d["linear_base"]["coset_syndromes"]), sorted(["000000", s(p["s1"]), s(p["s2"])]))


class GeneratorsRegenerateTheCodes(unittest.TestCase):
    def test_gen_py_regenerates_1285_byte_for_byte(self):
        with tempfile.TemporaryDirectory() as t:
            out = os.path.join(t, "c.txt")
            subprocess.run([sys.executable, os.path.join(ROOT, "scripts/search/gen.py"),
                            os.path.join(ROOT, "data/search/p1285.json"), out], check=True, capture_output=True)
            self.assertEqual(read(out, "rb"), read(os.path.join(ROOT, "data/codes/q7_n9_R4_M1285.txt"), "rb"))

    def test_structure_py_regenerates_every_committed_json(self):
        r = subprocess.run([sys.executable, os.path.join(ROOT, "scripts/codes/build_structured.py"), "--check"],
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)


class ExpandRejectsBrokenDocuments(unittest.TestCase):
    def setUp(self):
        self.doc = cf.load(os.path.join(ROOT, "data", "structured", "q7_n9_R4_M1285.json"))

    def test_changed_patch_word_breaks_the_sha256(self):
        d = copy.deepcopy(self.doc)
        w = d["patch_words"][0]
        d["patch_words"][0] = w[:-1] + str((int(w[-1]) + 1) % 7)
        with self.assertRaisesRegex(cf.FormatError, "sha256"):
            cf.check_doc(d)

    def test_overlapping_blocks_are_a_duplicate_error(self):
        d = copy.deepcopy(self.doc)
        d["subcode_cosets"][0]["reps"].append(d["subcode_cosets"][0]["reps"][0])
        d["M"] += 7
        with self.assertRaisesRegex(cf.FormatError, "duplicada"):
            cf.expand(d)

    def test_wrong_M_is_rejected(self):
        d = copy.deepcopy(self.doc)
        d["M"] -= 1
        with self.assertRaisesRegex(cf.FormatError, "M="):
            cf.expand(d)

    def test_digit_not_below_q_is_rejected(self):
        d = copy.deepcopy(self.doc)
        d["patch_words"][0] = "7" + d["patch_words"][0][1:]
        with self.assertRaisesRegex(cf.FormatError, "dígito"):
            cf.expand(d)

    def test_parity_check_not_orthogonal_to_generator_is_rejected(self):
        d = copy.deepcopy(self.doc)
        h = d["linear_base"]["parity_check"][0]
        d["linear_base"]["parity_check"][0] = h[:-1] + str((int(h[-1]) + 1) % 7)
        with self.assertRaisesRegex(cf.FormatError, "H G"):
            cf.expand(d)


if __name__ == "__main__":
    unittest.main()
