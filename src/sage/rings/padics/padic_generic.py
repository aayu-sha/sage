"""
p-Adic Generic

A generic superclass for all p-adic parents.

AUTHORS:

- David Roe
- Genya Zaytman: documentation
- David Harvey: doctests
- Julian Rueth (2013-03-16): test methods for basic arithmetic

"""

#*****************************************************************************
#       Copyright (C) 2007-2013 David Roe <roed.math@gmail.com>
#                               William Stein <wstein@gmail.com>
#                               Julian Rueth <julian.rueth@fsfe.org>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#  as published by the Free Software Foundation; either version 2 of
#  the License, or (at your option) any later version.
#
#                  http://www.gnu.org/licenses/
#*****************************************************************************
from __future__ import print_function
from __future__ import absolute_import

from sage.misc.prandom import sample
from sage.misc.misc import some_tuples

from sage.categories.principal_ideal_domains import PrincipalIdealDomains
from sage.categories.fields import Fields
from sage.rings.infinity import infinity
from .local_generic import LocalGeneric
from sage.rings.ring import PrincipalIdealDomain
from sage.rings.integer import Integer
from sage.rings.padics.padic_printing import pAdicPrinter
from sage.rings.padics.precision_error import PrecisionError
from sage.misc.cachefunc import cached_method
from sage.structure.richcmp import richcmp_not_equal


class pAdicGeneric(PrincipalIdealDomain, LocalGeneric):
    def __init__(self, base, p, prec, print_mode, names, element_class, category=None):
        """
        Initialization.

        INPUT:

            - base -- Base ring.
            - p -- prime
            - print_mode -- dictionary of print options
            - names -- how to print the uniformizer
            - element_class -- the class for elements of this ring

        EXAMPLES::

            sage: R = Zp(17) #indirect doctest
        """
        if category is None:
            if self.is_field():
                category = Fields()
            else:
                category = PrincipalIdealDomains()
        category = category.Metric().Complete()
        LocalGeneric.__init__(self, base, prec, names, element_class, category)
        self._printer = pAdicPrinter(self, print_mode)

    def some_elements(self):
        r"""
        Returns a list of elements in this ring.

        This is typically used for running generic tests (see :class:`TestSuite`).

        EXAMPLES::

            sage: Zp(2,4).some_elements()
            [0, 1 + O(2^4), 2 + O(2^5), 1 + 2^2 + 2^3 + O(2^4), 2 + 2^2 + 2^3 + 2^4 + O(2^5)]
        """
        p = self(self.prime())
        a = self.gen()
        one = self.one()
        L = [self.zero(), one, p, (one+p+p).inverse_of_unit(), p-p**2]
        if a != p:
            L.extend([a, (one + a + p).inverse_of_unit()])
        if self.is_field():
            L.extend([~(p-p-a),p**(-20)])
        return L

    def _modified_print_mode(self, print_mode):
        """
        Returns a dictionary of print options, starting with self's
        print options but modified by the options in the dictionary
        print_mode.

        INPUT:

            - print_mode -- dictionary with keys in ['mode', 'pos', 'ram_name', 'unram_name', 'var_name', 'max_ram_terms', 'max_unram_terms', 'max_terse_terms', 'sep', 'alphabet']

        EXAMPLES::

            sage: R = Zp(5)
            sage: R._modified_print_mode({'mode': 'bars'})['ram_name']
            '5'
        """
        if print_mode is None:
            print_mode = {}
        elif isinstance(print_mode, str):
            print_mode = {'mode': print_mode}
        for option in ['mode', 'pos', 'ram_name', 'unram_name', 'var_name', 'max_ram_terms', 'max_unram_terms', 'max_terse_terms', 'sep', 'alphabet', 'show_prec']:
            if option not in print_mode:
                print_mode[option] = self._printer.dict()[option]
        return print_mode

    def ngens(self):
        """
        Returns the number of generators of self.

        We conventionally define this as 1: for base rings, we take a
        uniformizer as the generator; for extension rings, we take a
        root of the minimal polynomial defining the extension.

        EXAMPLES::

            sage: Zp(5).ngens()
            1
            sage: Zq(25,names='a').ngens()
            1
        """
        return 1

    def gens(self):
        """
        Returns a list of generators.

        EXAMPLES::

            sage: R = Zp(5); R.gens()
            [5 + O(5^21)]
            sage: Zq(25,names='a').gens()
            [a + O(5^20)]
            sage: S.<x> = ZZ[]; f = x^5 + 25*x -5; W.<w> = R.ext(f); W.gens()
            [w + O(w^101)]
        """
        return [self.gen()]

    def __richcmp__(self, other, op):
        """
        Return 0 if self == other, and 1 or -1 otherwise.

        We consider two p-adic rings or fields to be equal if they are
        equal mathematically, and also have the same precision cap and
        printing parameters.

        EXAMPLES::

            sage: R = Qp(7)
            sage: S = Qp(7,print_mode='val-unit')
            sage: R == S
            False
            sage: S = Qp(7,type='capped-rel')
            sage: R == S
            True
            sage: R is S
            True
        """
        if not isinstance(other, pAdicGeneric):
            return NotImplemented

        lx = self.prime()
        rx = other.prime()
        if lx != rx:
            return richcmp_not_equal(lx, rx, op)

        lx = self.precision_cap()
        rx = other.precision_cap()
        if lx != rx:
            return richcmp_not_equal(lx, rx, op)

        return self._printer.richcmp_modes(other._printer, op)

    #def ngens(self):
    #    return 1

    #def gen(self, n = 0):
    #    if n != 0:
    #        raise IndexError, "only one generator"
    #    return self(self.prime())

    def print_mode(self):
        r"""
        Returns the current print mode as a string.

        INPUT:

            self -- a p-adic field

        OUTPUT:

            string -- self's print mode

        EXAMPLES::

            sage: R = Qp(7,5, 'capped-rel')
            sage: R.print_mode()
            'series'
        """
        return self._printer._print_mode()

    #def element_class(self):
    #    return self._element_class

    def characteristic(self):
        r"""
        Returns the characteristic of self, which is always 0.

        INPUT:

            self -- a p-adic parent

        OUTPUT:

            integer -- self's characteristic, i.e., 0

        EXAMPLES::

            sage: R = Zp(3, 10,'fixed-mod'); R.characteristic()
            0
        """
        return Integer(0)

    def prime(self):
        """
        Returns the prime, ie the characteristic of the residue field.

        INPUT:

            self -- a p-adic parent

        OUTPUT:

            integer -- the characteristic of the residue field

        EXAMPLES::

            sage: R = Zp(3,5,'fixed-mod')
            sage: R.prime()
            3
        """
        return self.prime_pow._prime()

    def uniformizer_pow(self, n):
        """
        Returns p^n, as an element of self.

        If n is infinity, returns 0.

        EXAMPLES::

            sage: R = Zp(3, 5, 'fixed-mod')
            sage: R.uniformizer_pow(3)
            3^3 + O(3^5)
            sage: R.uniformizer_pow(infinity)
            O(3^5)
        """
        if n is infinity:
            return self(0)
        return self(self.prime_pow.pow_Integer_Integer(n))

    def _unram_print(self):
        """
        For printing.  Will be None if the unramified subextension of self is of degree 1 over Z_p or Q_p.

        EXAMPLES::

            sage: Zp(5)._unram_print()
        """
        return None

    def residue_characteristic(self):
        """
        Return the prime, i.e., the characteristic of the residue field.

        OUTPUT:

        integer -- the characteristic of the residue field

        EXAMPLES::

            sage: R = Zp(3,5,'fixed-mod')
            sage: R.residue_characteristic()
            3
        """
        return self.prime()

    def residue_class_field(self):
        """
        Returns the residue class field.

        INPUT:

            self -- a p-adic ring

        OUTPUT:

            the residue field

        EXAMPLES::

            sage: R = Zp(3,5,'fixed-mod')
            sage: k = R.residue_class_field()
            sage: k
            Finite Field of size 3
        """
        from sage.rings.finite_rings.finite_field_constructor import GF
        return GF(self.prime())

    def residue_field(self):
        """
        Returns the residue class field.

        INPUT:

            self -- a p-adic ring

        OUTPUT:

            the residue field

        EXAMPLES::

            sage: R = Zp(3,5,'fixed-mod')
            sage: k = R.residue_field()
            sage: k
            Finite Field of size 3
        """
        return self.residue_class_field()

    def residue_system(self):
        """
        Returns a list of elements representing all the residue classes.

        INPUT:

            self -- a p-adic ring

        OUTPUT:

            list of elements -- a list of elements representing all the residue classes

        EXAMPLES::

            sage: R = Zp(3, 5,'fixed-mod')
            sage: R.residue_system()
            [O(3^5), 1 + O(3^5), 2 + O(3^5)]
        """
        return [self(i) for i in self.residue_class_field()]

    def fraction_field(self, print_mode=None):
        r"""
        Returns the fraction field of this ring or field.

        For `\ZZ_p`, this is the `p`-adic field with the same options,
        and for extensions, it is just the extension of the fraction
        field of the base determined by the same polynomial.

        The fraction field of a capped absolute ring is capped relative,
        and that of a fixed modulus ring is floating point.

        INPUT:

        - ``print_mode`` -- a dictionary containing print options.
          Defaults to the same options as this ring.

        OUTPUT:

        - the fraction field of this ring.

        EXAMPLES::

            sage: R = Zp(5, print_mode='digits')
            sage: K = R.fraction_field(); repr(K(1/3))[3:]
            '31313131313131313132'
            sage: L = R.fraction_field({'max_ram_terms':4}); repr(L(1/3))[3:]
            '3132'
            sage: U.<a> = Zq(17^4, 6, print_mode='val-unit', print_max_terse_terms=3)
            sage: U.fraction_field()
            Unramified Extension in a defined by x^4 + 7*x^2 + 10*x + 3 with capped relative precision 6 over 17-adic Field
            sage: U.fraction_field({"pos":False}) == U.fraction_field()
            False
        """
        if self.is_field() and print_mode is None:
            return self
        if print_mode is None:
            return self.change(field=True)
        else:
            return self.change(field=True, **print_mode)

    def integer_ring(self, print_mode=None):
        r"""
        Returns the ring of integers of this ring or field.

        For `\QQ_p`, this is the `p`-adic ring with the same options,
        and for extensions, it is just the extension of the ring
        of integers of the base determined by the same polynomial.

        INPUT:

        - ``print_mode`` -- a dictionary containing print options.
          Defaults to the same options as this ring.

        OUTPUT:

        - the ring of elements of this field with nonnegative valuation.

        EXAMPLES::

            sage: K = Qp(5, print_mode='digits')
            sage: R = K.integer_ring(); repr(R(1/3))[3:]
            '31313131313131313132'
            sage: S = K.integer_ring({'max_ram_terms':4}); repr(S(1/3))[3:]
            '3132'
            sage: U.<a> = Qq(17^4, 6, print_mode='val-unit', print_max_terse_terms=3)
            sage: U.integer_ring()
            Unramified Extension in a defined by x^4 + 7*x^2 + 10*x + 3 with capped relative precision 6 over 17-adic Ring
            sage: U.fraction_field({"pos":False}) == U.fraction_field()
            False
        """
        #Currently does not support fields with non integral defining polynomials.  This should change when the padic_general_extension framework gets worked out.
        if not self.is_field() and print_mode is None:
            return self
        if print_mode is None:
            return self.change(field=False)
        else:
            return self.change(field=False, **print_mode)

    def teichmuller(self, x, prec = None):
        r"""
        Returns the teichmuller representative of x.

        INPUT:

            - self -- a p-adic ring
            - x -- something that can be cast into self

        OUTPUT:

            - element -- the teichmuller lift of x

        EXAMPLES::

            sage: R = Zp(5, 10, 'capped-rel', 'series')
            sage: R.teichmuller(2)
            2 + 5 + 2*5^2 + 5^3 + 3*5^4 + 4*5^5 + 2*5^6 + 3*5^7 + 3*5^9 + O(5^10)
            sage: R = Qp(5, 10,'capped-rel','series')
            sage: R.teichmuller(2)
            2 + 5 + 2*5^2 + 5^3 + 3*5^4 + 4*5^5 + 2*5^6 + 3*5^7 + 3*5^9 + O(5^10)
            sage: R = Zp(5, 10, 'capped-abs', 'series')
            sage: R.teichmuller(2)
            2 + 5 + 2*5^2 + 5^3 + 3*5^4 + 4*5^5 + 2*5^6 + 3*5^7 + 3*5^9 + O(5^10)
            sage: R = Zp(5, 10, 'fixed-mod', 'series')
            sage: R.teichmuller(2)
            2 + 5 + 2*5^2 + 5^3 + 3*5^4 + 4*5^5 + 2*5^6 + 3*5^7 + 3*5^9 + O(5^10)
            sage: R = Zp(5,5)
            sage: S.<x> = R[]
            sage: f = x^5 + 75*x^3 - 15*x^2 +125*x - 5
            sage: W.<w> = R.ext(f)
            sage: y = W.teichmuller(3); y
            3 + 3*w^5 + w^7 + 2*w^9 + 2*w^10 + 4*w^11 + w^12 + 2*w^13 + 3*w^15 + 2*w^16 + 3*w^17 + w^18 + 3*w^19 + 3*w^20 + 2*w^21 + 2*w^22 + 3*w^23 + 4*w^24 + O(w^25)
            sage: y^5 == y
            True
            sage: g = x^3 + 3*x + 3
            sage: A.<a> = R.ext(g)
            sage: b = A.teichmuller(1 + 2*a - a^2); b
            (4*a^2 + 2*a + 1) + 2*a*5 + (3*a^2 + 1)*5^2 + (a + 4)*5^3 + (a^2 + a + 1)*5^4 + O(5^5)
            sage: b^125 == b
            True

        AUTHORS:

        - Initial version: David Roe
        - Quadratic time version: Kiran Kedlaya <kedlaya@math.mit.edu> (3/27/07)
        """
        if prec is None:
            prec = self.precision_cap()
        else:
            prec = min(Integer(prec), self.precision_cap())
        ans = self(x, prec)
        ans._teichmuller_set_unsafe()
        return ans

    def teichmuller_system(self):
        r"""
        Returns a set of teichmuller representatives for the invertible elements of `\ZZ / p\ZZ`.

        INPUT:

        - self -- a p-adic ring

        OUTPUT:

        - list of elements -- a list of teichmuller representatives for the invertible elements of `\ZZ / p\ZZ`

        EXAMPLES::

            sage: R = Zp(3, 5,'fixed-mod', 'terse')
            sage: R.teichmuller_system()
            [1 + O(3^5), 242 + O(3^5)]

        Check that :trac:`20457` is fixed::

            sage: F.<a> = Qq(5^2,6)
            sage: F.teichmuller_system()[3]
            (2*a + 2) + (4*a + 1)*5 + 4*5^2 + (2*a + 1)*5^3 + (4*a + 1)*5^4 + (2*a + 3)*5^5 + O(5^6)

        NOTES:

        Should this return 0 as well?
        """
        R = self.residue_class_field()
        prec = self.precision_cap()
        return [self.teichmuller(self(i).lift_to_precision(prec)) for i in R if i != 0]

#     def different(self):
#         raise NotImplementedError

#     def automorphisms(self):
#         r"""
#         Returns the group of automorphisms of `\ZZ_p`, i.e. the trivial group.
#         """
#         raise NotImplementedError

#     def galois_group(self):
#         r"""
#         Returns the Galois group of `\ZZ_p`, i.e. the trivial group.
#         """
#         raise NotImplementedError

#     def hasGNB(self):
#         r"""
#         Returns whether or not `\ZZ_p` has a Gauss Normal Basis.
#         """
#         raise NotImplementedError

    def extension(self, modulus, prec = None, names = None, print_mode = None, implementation='FLINT', **kwds):
        """
        Create an extension of this p-adic ring.

        EXAMPLES::

            sage: k = Qp(5)
            sage: R.<x> = k[]
            sage: l.<w> = k.extension(x^2-5); l
            Eisenstein Extension in w defined by x^2 - 5 with capped relative precision 40 over 5-adic Field

            sage: F = list(Qp(19)['x'](cyclotomic_polynomial(5)).factor())[0][0]
            sage: L = Qp(19).extension(F, names='a')
            sage: L
            Unramified Extension in a defined by x^2 + 8751674996211859573806383*x + 1 with capped relative precision 20 over 19-adic Field
        """
        from sage.rings.padics.factory import ExtensionFactory
        if print_mode is None:
            print_mode = {}
        elif isinstance(print_mode, str):
            print_mode = {'print_mode': print_mode}
        else:
            if not isinstance(print_mode, dict):
                print_mode = dict(print_mode)
            for option in ['mode', 'pos', 'max_ram_terms', 'max_unram_terms', 'max_terse_terms', 'sep', 'alphabet']:
                if option in print_mode:
                    print_mode["print_" + option] = print_mode[option]
                    del print_mode[option]
                elif "print_" + option not in print_mode:
                    if "print_" + option in kwds:
                        print_mode["print_" + option] = kwds["print_" + option]
                    else:
                        print_mode["print_" + option] = self._printer.dict()[option]
            for option in ['ram_name', 'unram_name', 'var_name']:
                if option not in print_mode:
                    if option in kwds:
                        print_mode[option] = kwds[option]
                    else:
                        print_mode[option] = self._printer.dict()[option]
        return ExtensionFactory(base=self, modulus=modulus, prec=prec, names=names, check = True, implementation=implementation, **print_mode)

    def _test_add(self, **options):
        """
        Test addition of elements of this ring.

        INPUT:

        - ``options`` -- any keyword arguments accepted by :meth:`_tester`.

        EXAMPLES::

            sage: Zp(3)._test_add()

        .. SEEALSO::

            :class:`TestSuite`

        """
        tester = self._tester(**options)
        elements = tester.some_elements()

        for x in elements:
            y = x + self.zero()
            tester.assertEqual(y,x)
            tester.assertEqual(y.precision_absolute(),x.precision_absolute())
            tester.assertEqual(y.precision_relative(),x.precision_relative())

        for x,y in some_tuples(elements, 2, tester._max_runs):
            z = x + y
            tester.assertIs(z.parent(), self)
            zprec = min(x.precision_absolute(), y.precision_absolute())
            if not self.is_floating_point():
                tester.assertEqual(z.precision_absolute(), zprec)
            tester.assertGreaterEqual(z.valuation(), min(x.valuation(),y.valuation()))
            if x.valuation() != y.valuation():
                tester.assertEqual(z.valuation(), min(x.valuation(),y.valuation()))
            tester.assert_(y.is_equal_to(z-x,zprec))
            tester.assert_(x.is_equal_to(z-y,zprec))

    def _test_sub(self, **options):
        """
        Test subtraction on elements of this ring.

        INPUT:

        - ``options`` -- any keyword arguments accepted by :meth:`_tester`.

        EXAMPLES::

            sage: Zp(3)._test_sub()

        .. SEEALSO::

            :class:`TestSuite`

        """
        tester = self._tester(**options)

        elements = list(tester.some_elements())
        for x in elements:
            y = x - self.zero()
            tester.assertEqual(y, x)
            tester.assertEqual(y.precision_absolute(), x.precision_absolute())
            tester.assertEqual(y.precision_relative(), x.precision_relative())

        for x,y in some_tuples(elements, 2, tester._max_runs):
            z = x - y
            tester.assertIs(z.parent(), self)
            zprec = min(x.precision_absolute(), y.precision_absolute())
            if not self.is_floating_point():
                tester.assertEqual(z.precision_absolute(), zprec)
            tester.assertGreaterEqual(z.valuation(), min(x.valuation(),y.valuation()))
            if x.valuation() != y.valuation():
                tester.assertEqual(z.valuation(), min(x.valuation(),y.valuation()))
            tester.assert_((-y).is_equal_to(z - x,zprec))
            tester.assert_(x.is_equal_to(z + y,zprec))

    def _test_invert(self, **options):
        """
        Test multiplicative inversion of elements of this ring.

        INPUT:

        - ``options`` -- any keyword arguments accepted by :meth:`_tester`.

        EXAMPLES::

            sage: Zp(3)._test_invert()

        .. SEEALSO::

            :class:`TestSuite`

        """
        tester = self._tester(**options)

        elements = tester.some_elements()
        for x in elements:
            try:
                y = ~x
            except (ZeroDivisionError, PrecisionError, ValueError):
                tester.assertFalse(x.is_unit())
                if not self.is_fixed_mod(): tester.assertTrue(x.is_zero())
            else:
                try:
                    e = y * x
                except ZeroDivisionError:
                    tester.assertTrue(self.is_floating_point() and (x.is_zero() or y.is_zero()))
                else:
                    tester.assertFalse(x.is_zero())
                    tester.assertIs(y.parent(), self if self.is_fixed_mod() else self.fraction_field())
                    tester.assertTrue(e.is_one())
                    tester.assertEqual(e.precision_relative(), x.precision_relative())
                    tester.assertEqual(y.valuation(), -x.valuation())

    def _test_mul(self, **options):
        """
        Test multiplication of elements of this ring.

        INPUT:

        - ``options`` -- any keyword arguments accepted by :meth:`_tester`.

        EXAMPLES::

            sage: Zp(3)._test_mul()

        .. SEEALSO::

            :class:`TestSuite`

        """
        tester = self._tester(**options)

        elements = list(tester.some_elements())
        for x,y in some_tuples(elements, 2, tester._max_runs):
            z = x * y
            tester.assertIs(z.parent(), self)
            if self.is_capped_relative() or self.is_floating_point():
                tester.assertEqual(z.precision_relative(), min(x.precision_relative(), y.precision_relative()))
            else:
                tester.assertLessEqual(z.precision_relative(), min(x.precision_relative(), y.precision_relative()))
            if not z.is_zero():
                tester.assertEqual(z.valuation(), x.valuation() + y.valuation())

    def _test_div(self, **options):
        """
        Test division of elements of this ring.

        INPUT:

        - ``options`` -- any keyword arguments accepted by :meth:`_tester`.

        EXAMPLES::

            sage: Zp(3)._test_div()

        .. SEEALSO::

            :class:`TestSuite`

        """
        tester = self._tester(**options)

        elements = list(tester.some_elements())
        for x,y in some_tuples(elements, 2, tester._max_runs):
            try:
                z = x / y
            except (ZeroDivisionError, PrecisionError, ValueError):
                if self.is_fixed_mod(): tester.assertFalse(y.is_unit())
                else: tester.assertTrue(y.is_zero())
            else:
                try:
                    xx = z*y
                except ZeroDivisionError:
                    tester.assertTrue(self.is_floating_point() and (z.is_zero() or y.is_zero()))
                else:
                    tester.assertFalse(y.is_zero())
                    tester.assertIs(z.parent(), self if self.is_fixed_mod() else self.fraction_field())
                    tester.assertEqual(z.precision_relative(), min(x.precision_relative(), y.precision_relative()))
                    tester.assertEqual(z.valuation(), x.valuation() - y.valuation())
                    tester.assertEqual(xx, x)

    def _test_neg(self, **options):
        """
        Test the negation operator on elements of this ring.

        INPUT:

        - ``options`` -- any keyword arguments accepted by :meth:`_tester`.

        EXAMPLES::

            sage: Zp(3)._test_neg()

        .. SEEALSO::

            :class:`TestSuite`
        """
        tester = self._tester(**options)
        for x in tester.some_elements():
            y = -x
            tester.assertIs(y.parent(), self)
            tester.assertTrue((x+y).is_zero())
            tester.assertEqual(y.valuation(),x.valuation())
            tester.assertEqual(x.precision_absolute(),y.precision_absolute())
            tester.assertEqual(x.precision_relative(),y.precision_relative())
            tester.assertEqual(x.is_zero(),y.is_zero())
            tester.assertEqual(x.is_unit(),y.is_unit())

    def _test_log(self, **options):
        """
        Test the log operator on elements of this ring.

        INPUT:

        - ``options`` -- any keyword arguments accepted by :meth:`_tester`.

        EXAMPLES::

            sage: Zp(3)._test_log()

        .. SEEALSO::

            :class:`TestSuite`
        """
        tester = self._tester(**options)
        for x in tester.some_elements():
            if x.is_zero(): continue
            l = x.log(p_branch=0)
            tester.assertIs(l.parent(), self)
            tester.assertGreater(l.valuation(), 0)
            if self.is_capped_absolute() or self.is_capped_relative():
                tester.assertEqual(x.precision_relative(), l.precision_absolute())

        if self.is_capped_absolute() or self.is_capped_relative():
            # In the fixed modulus setting, rounding errors may occur
            elements = list(tester.some_elements())
            for x, y, b in some_tuples(elements, 3, tester._max_runs):
                if x.is_zero() or y.is_zero(): continue
                r1 = x.log(pi_branch=b) + y.log(pi_branch=b)
                r2 = (x*y).log(pi_branch=b)
                tester.assertEqual(r1, r2)

            p = self.prime()
            for x in tester.some_elements():
                if x.is_zero(): continue
                if p == 2:
                    a = 4 * x.unit_part()
                else:
                    a = p * x.unit_part()
                b = a.exp().log()
                c = (1+a).log().exp()
                tester.assertEqual(a, b)
                tester.assertEqual(1+a, c)

    def _test_teichmuller(self, **options):
        """
        Test Teichmuller lifts.

        INPUT:

        - ``options`` -- any keyword arguments accepted by :meth:`_tester`.

        EXAMPLES::

            sage: Zp(3)._test_teichmuller()

        .. SEEALSO::

            :class:`TestSuite`
        """
        tester = self._tester(**options)

        for x in tester.some_elements():
            try:
                y = self.teichmuller(x)
            except ValueError:
                tester.assertTrue(x.valuation() < 0 or x.precision_absolute()==0)
            else:
                try:
                    tester.assertEqual(x.residue(), y.residue())
                except (NotImplementedError, AttributeError):
                    pass
                tester.assertEqual(y**self.residue_field().order(), y)

    def _test_convert_residue_field(self, **options):
        r"""
        Test that conversion of residue field elements back to this ring works.

        INPUT:

         - ``options`` -- any keyword arguments accepted by :meth:`_tester`.

        EXAMPLES::

            sage: Zp(3)._test_convert_residue_field()

        .. SEEALSO::

            :class:`TestSuite`
        """
        tester = self._tester(**options)

        for x in tester.some_elements():
            if x.valuation() < 0:
                continue
            if x.precision_absolute() <= 0:
                continue
            y = x.residue()
            z = self(y)
            tester.assertEqual(z.residue(), y)

    @cached_method
    def _log_unit_part_p(self):
        """
        Compute the logarithm of the unit-part of `p`.

        If `\pi` is the uniformizer in this ring, then we can uniquely write
        `p=\pi^e u` where `u` is a `\pi`-adic unit. This method computes the
        logarithm of `u`.

        This is a helper method for
        :meth:`sage.rings.padics.padic_generic_element.pAdicGenericElement.log`.

        TESTS::

            sage: R = Qp(3,5)
            sage: R._log_unit_part_p()
            O(3^5)

            sage: S.<x> = ZZ[]
            sage: W.<pi> = R.extension(x^3-3)
            sage: W._log_unit_part_p()
            O(pi^15)

            sage: W.<pi> = R.extension(x^3-3*x-3)
            sage: W._log_unit_part_p()
            2 + pi + 2*pi^2 + pi^4 + pi^5 + 2*pi^7 + 2*pi^8 + pi^9 + 2*pi^10 + pi^11 + pi^12 + 2*pi^14 + O(pi^15)

        """
        return self(self.prime()).unit_part().log()

    @cached_method
    def _exp_p(self):
        """
        Compute the exponential of `p`.

        This is a helper method for
        :meth:`sage.rings.padics.padic_generic_element.pAdicGenericElement.exp`.

        TESTS::

            sage: R = Qp(3, 5)
            sage: R._exp_p()
            1 + 3 + 3^2 + 2*3^3 + 2*3^4 + O(3^5)

            sage: S.<x> = ZZ[]
            sage: W.<pi> = R.extension(x^3-3)
            sage: W._exp_p()
            1 + pi^3 + pi^6 + 2*pi^9 + 2*pi^12 + O(pi^15)
            sage: R._exp_p() == W._exp_p()
            True

            sage: W.<pi> = R.extension(x^3-3*x-3)
            sage: W._exp_p()
            1 + pi^3 + 2*pi^4 + pi^5 + pi^7 + pi^9 + pi^10 + 2*pi^11 + pi^12 + pi^13 + 2*pi^14 + O(pi^15)
            sage: R._exp_p() == W._exp_p()
            True

        """
        p = self.prime()
        if p == 2:
            # the exponential of 2 does not exist, so we compute the
            # exponential of 4 instead.
            p = 4
        return self(p)._exp(self.precision_cap())

    def frobenius_endomorphism(self, n=1):
        """
        INPUT:

        -  ``n`` -- an integer (default: 1)

        OUTPUT:

        The `n`-th power of the absolute arithmetic Frobenius
        endomorphism on this field.

        EXAMPLES::

            sage: K.<a> = Qq(3^5)
            sage: Frob = K.frobenius_endomorphism(); Frob
            Frobenius endomorphism on Unramified Extension ... lifting a |--> a^3 on the residue field
            sage: Frob(a) == a.frobenius()
            True

        We can specify a power::

            sage: K.frobenius_endomorphism(2)
            Frobenius endomorphism on Unramified Extension ... lifting a |--> a^(3^2) on the residue field

        The result is simplified if possible::

            sage: K.frobenius_endomorphism(6)
            Frobenius endomorphism on Unramified Extension ... lifting a |--> a^3 on the residue field
            sage: K.frobenius_endomorphism(5)
            Identity endomorphism of Unramified Extension ...

        Comparisons work::

            sage: K.frobenius_endomorphism(6) == Frob
            True
        """
        from .morphism import FrobeniusEndomorphism_padics
        return FrobeniusEndomorphism_padics(self, n)

    def _test_elements_eq_transitive(self, **options):
        """
        The operator ``==`` is not transitive for `p`-adic numbers. We disable
        the check of the category framework by overriding this method.

        EXAMPLES:

            sage: R = Zp(3)
            sage: R(3) == R(0,1)
            True
            sage: R(0,1) == R(6)
            True
            sage: R(3) == R(6)
            False
            sage: R._test_elements_eq_transitive()

        """
        pass

def local_print_mode(obj, print_options, pos = None, ram_name = None):
    r"""
    Context manager for safely temporarily changing the print_mode
    of a p-adic ring/field.

    EXAMPLES::

        sage: R = Zp(5)
        sage: R(45)
        4*5 + 5^2 + O(5^21)
        sage: with local_print_mode(R, 'val-unit'):
        ....:     print(R(45))
        5 * 9 + O(5^21)

    NOTES::

        For more documentation see localvars in parent_gens.pyx
    """
    if isinstance(print_options, str):
        print_options = {'mode': print_options}
    elif not isinstance(print_options, dict):
        raise TypeError("print_options must be a dictionary or a string")
    if pos is not None:
        print_options['pos'] = pos
    if ram_name is not None:
        print_options['ram_name'] = ram_name
    for option in ['mode', 'pos', 'ram_name', 'unram_name', 'var_name', 'max_ram_terms', 'max_unram_terms', 'max_terse_terms', 'sep', 'alphabet']:
        if option not in print_options:
            print_options[option] = obj._printer.dict()[option]
    return pAdicPrinter(obj, print_options)
