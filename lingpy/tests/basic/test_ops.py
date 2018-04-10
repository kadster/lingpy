"""
Test wordlist module.
"""
from __future__ import unicode_literals, print_function, division, \
    absolute_import

from lingpy import Wordlist, Alignments
from lingpy.basic.ops import wl2dst, wl2qlc, tsv2triple, triple2tsv, \
    calculate_data, wl2multistate, coverage, clean_taxnames
from lingpy.tests.util import test_data
from lingpy.tests.util_testing import WithTempDir


class TestOps(WithTempDir):
    def setUp(self):
        WithTempDir.setUp(self)
        self.wordlist = Wordlist(test_data('KSL.qlc'))
        self.wordlist2 = Wordlist(test_data('KSL4.qlc'))

    def test_iter_rows(self):
        from lingpy.basic.ops import iter_rows
        assert len(list(
            iter_rows(self.wordlist, 'concept', 'doculect'))[0]) == 3

    def test_wl2dict(self):
        from lingpy.basic.ops import wl2dict

        _ = wl2dict(self.wordlist, dict(s1=['concept', '{0}'],
                                        s2=['cogid', '{0}']), [('ipa', '{0}')])

    def test_wl2dst(self):
        res = wl2dst(self.wordlist, mode='jaccard')
        self.assertIsInstance(res, list)
        res = wl2dst(self.wordlist, mode='jaccard', refB='glossid')
        self.assertIsInstance(res, list)

        _ = wl2dst(self.wordlist, mode='swadesh')
        _ = wl2dst(self.wordlist, mode='shared')
        _ = wl2dst(self.wordlist, mode='swadesh', ignore_missing=True)

        # trigger zero-division-warning in wl2dst
        tmp = Wordlist({
            0: ['doculect', 'concept', 'counterpart', 'cogid'],
            1: ['l1', 'hand', 'hand', '1'],
            2: ['l2 - a (taxon) name)', 'hand', 'hand', '2'],
            3: ['l3', 'foot', 'foot', '3']
        })
        dst = wl2dst(tmp)
        assert dst[0][2] == 1

    def test_wl2qlc(self):
        stamp = 'test-stamp'
        out = self.tmp_path('test')

        wl2qlc(self.wordlist.header, self.wordlist._data,
               filename=out.as_posix(), stamp=stamp)
        out = self.tmp_path('test.qlc')

        with out.open(encoding='utf8') as fp:
            self.assertTrue(fp.read().endswith(stamp))

        # load a worldist with alignments and otuput it as string with msapairs
        tmp = Alignments(test_data('good_file.tsv'), ref='cogid')
        tmp.align(ref="cogid")

        wl2qlc(tmp.header, tmp._data, meta=tmp._meta, filename=out.as_posix(),
               stamp='stampo', ignore=[])
        tmp.get_consensus(ref="cogid")

        wl2qlc([h.upper()
                for h in sorted(tmp.header, key=lambda x: tmp.header[x])],
               tmp._data, meta=tmp._meta, filename=out.as_posix(),
               stamp='stampo', ignore=[], formatter="doculect,concept")
        wl2qlc([h.upper()
                for h in sorted(tmp.header, key=lambda x: tmp.header[x])],
               tmp._data, meta=tmp._meta, filename=out.as_posix(),
               stamp='stampo', ignore=[], formatter="doculect")

    def test_tsv2triple(self):
        out = self.tmp_path('test')
        triples = tsv2triple(self.wordlist, out)
        self.assertIsInstance(triple2tsv(out), list)
        self.assertIsInstance(triple2tsv(triples, output='dict'), dict)

    def test_calculate_data(self):
        for data in ['tree', 'dst', 'cluster']:
            calculate_data(self.wordlist, data)
            calculate_data(self.wordlist, data, mode='shared')

    def test_wl2multistate(self):
        res = wl2multistate(self.wordlist2, 'cogid', '?')
        # the result must be a matrix.
        self.assertIsInstance(res, list)
        self.assertEquals(len(set(len(row) for row in res)), 1)

    def test_coverage(self):
        res = coverage(self.wordlist)
        self.assertEquals(res['Turkish'], 200)

    def test_clean_taxnames(self):
        tmp = Wordlist({
            0: ['doculect', 'concept', 'counterpart'],
            1: ['l1', 'hand', 'hand'],
            2: ['l2 - a (taxon) name)', 'hand', 'hand']
        })

        clean_taxnames(tmp)
        assert tmp.cols[-1] == 'l2___a_taxon_name'

    def test_renumber(self):
        tmp = Wordlist(test_data('good_file.tsv'))
        tmp.renumber('cogid', 'newcogid')
        assert 'newcogid' in tmp.header
        tmp.renumber('mock')
        assert 'mockid' in tmp.header
