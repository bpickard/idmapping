from unittest import TestCase

from ddt import ddt, data, unpack
from mock import Mock

from idm.plugins.manager import BaseProvider
from idm.utils import select_providers, remove, and_, or_


def make_provider(name, needs=None, provides=None, cost=50):
    if not needs:
        needs = []
    if not provides:
        provides = []
    provider = BaseProvider()
    provider.name = name
    provider.get_provides = Mock(return_value=provides)
    provider.get_needs = Mock(return_value=needs)
    provider.get_cost = Mock(return_value=cost)
    return provider

PROVIDER1 = make_provider('provider1', provides=['a1', 'a2'], needs=['a1'])
PROVIDER2 = make_provider('provider2', provides=['a2', 'a3'], needs=['a2'])
PROVIDER3 = make_provider('provider3', provides=['a1', 'a3'], needs=['a1', 'a3'])
PROVIDER4 = make_provider('provider4', provides=['a1', 'a2', 'a4'], needs=['a1', 'a2'])
PROVIDER5 = make_provider('provider5', provides=['a2', 'a3'], needs=['a2', 'a3'])
PROVIDER6 = make_provider('provider6', provides=['a5', 'a6'])
PROVIDER7 = make_provider('provider7', provides=['a1', 'a2', 'a3'])
PROVIDER8 = make_provider('provider8', provides=['a4'])
PROVIDER9 = make_provider('provider9', provides=['a5'])
PROVIDER10 = make_provider('provider10', provides=['a6'])

PROVIDER_A1 = make_provider('provider A1', provides=['a1', 'a2'], needs=['a1'])
PROVIDER_A2 = make_provider('provider A2', provides=['a2', 'a3'], needs=['a2'])
PROVIDER_A3 = make_provider('provider A3', provides=['a1', 'a3'], needs=['a3'])

PROVIDER_A4 = make_provider('provider A4', provides=['a1', 'a2'])

EDX_PROVIDER = make_provider(
        'edx provider',
        provides=['edx_username', 'remote_id'],
        needs=['edx_username', 'remote_id'])
USERINFO_PROVIDER = make_provider(
        'user info provider',
        provides=['user_id', 'first_name', 'last_name', 'email', 'remote_id', 'student_number', 'employee_number'],
        needs=['user_id', 'remote_id', 'student_number', 'employee_number'])
# REMOTEID_PROVIDER = make_provider(
#         'remote_id provider',
#         provides=['user_id', 'remote_id'],
#         needs=['user_id'])
ALL_REAL_PROVIDERS = [USERINFO_PROVIDER, EDX_PROVIDER]


@ddt
class UtilsTestCase(TestCase):

    def setUp(self):
        super(UtilsTestCase, self).setUp()

    # @data(
    #     ({'a1': [PROVIDER1]}, {'a2'}, {'a1'}, {PROVIDER1}),
    #     ({'a1': [PROVIDER1], 'a2': [PROVIDER1, PROVIDER2]}, {'a1', 'a2'}, set(), {PROVIDER1}),
    #     ({'a1': [PROVIDER1, PROVIDER3], 'a2': [PROVIDER2, PROVIDER3]}, {'a1', 'a2'}, set(), {PROVIDER3})
    # )
    # @unpack
    # def test__select_providers(self, provided_by, wants, given, expected):
    #     actual = _select_providers(provided_by, wants, given)
    #     self.assertSetEqual(actual, expected)

    # @TODO Test costs
    @data(
        ([PROVIDER1], ['a2'], {'a1'}, {PROVIDER1}),
        ([PROVIDER3], ['a1'], {'a3'}, {PROVIDER3}),
        ([PROVIDER3], ['a1', 'a3'], {'a3'}, {PROVIDER3}),
        # ([PROVIDER1], ['a1'], {'a2'}, {}),
        ([PROVIDER1, PROVIDER2], ['a2'], {'a1'}, {PROVIDER1}),
        ([PROVIDER1, PROVIDER2], ['a3'], {'a2'}, {PROVIDER2}),
        ([PROVIDER1, PROVIDER2], ['a1', 'a2'], {'a1'}, {PROVIDER1}),
        ([PROVIDER1, PROVIDER2], ['a2', 'a3'], {'a2'}, {PROVIDER2}),
        ([PROVIDER1, PROVIDER2], ['a1', 'a3'], {'a1'}, {PROVIDER1, PROVIDER2}),
        ([PROVIDER3, PROVIDER4], ['a1', 'a2', 'a3', 'a4'], {'a3'}, {PROVIDER3, PROVIDER4}),
        ([PROVIDER1, PROVIDER4, PROVIDER5], ['a1', 'a3', 'a4'], {'a1'}, {PROVIDER4, PROVIDER5}),
        (ALL_REAL_PROVIDERS, ['last_name', 'first_name', 'edx_username', 'user_id', 'email'], {'edx_username'},
         {EDX_PROVIDER, USERINFO_PROVIDER})

        # ([PROVIDER1, PROVIDER2, PROVIDER3], ['a1', 'a3'], set(), {PROVIDER3}),
        # # select providers with total lowest cost
        # ([PROVIDER4, PROVIDER5, PROVIDER6, PROVIDER7, PROVIDER8, PROVIDER9, PROVIDER10],
        #  ['a1', 'a2', 'a3', 'a4', 'a5', 'a6'], set(), {PROVIDER4, PROVIDER5, PROVIDER6}),
        # # test dependencies
        # ([PROVIDER_A1, PROVIDER_A2, PROVIDER_A3], ['a3'], {'a1'}, {PROVIDER_A1, PROVIDER_A2})
    )
    @unpack
    def test_select_providers(self, providers, wants, given, expected):
        actual = select_providers(providers, wants, given)
        self.assertSetEqual(actual, expected)

    @data(
        (['a'], 'a', []),
        (['a'], 'b', ['a']),
        (['a', 'b'], 'a', ['b']),
        (['a', 'b', ['a', 'c']], 'a', ['b']),
        (['a', 'b', ['a', 'c']], 'c', ['a', 'b']),
        (['a', 'b', ['a', 'c']], ['a', 'c'], ['b']),
        (['a', 'b', ['a', 'c']], ['a', 'd'], ['b']),
    )
    @unpack
    def test_remove(self, origin, elements, expect):
        actual = remove(origin, elements)
        self.assertListEqual(actual, expect)

    @data(
        (and_([]), 'a', ['a']),
        (and_([]), ['a', 'b'], ['a', 'b']),
        (and_([]), or_(['a']), [or_('a')]),
    )
    @unpack
    def test_op_add(self, op, elements, expected):
        op.add(elements)
        self.assertItemsEqual(expected, op)

    @data(
        (and_(['a', 'b', 'c']), 'b', ['a', 'c']),
        (and_(['a', 'b', 'c', 'd']), ['b', 'c'], ['a', 'd']),
        (or_(['a', 'b', 'c']), 'b', []),
    )
    @unpack
    def test_op_remove(self, op, elements, expected):
        op.op_remove(elements)
        self.assertItemsEqual(expected, op)

    @data(
        (and_(['a', 'b']), ['a', 'b'], True),
        (and_(['a', 'b']), ['a'], False),
        (and_(['a', 'b', or_(['c', 'd'])]), ['a', 'b', 'c'], True),
        (and_(['a', 'b', or_(['c', 'd'])]), ['a', 'b', 'd'], True),
        (and_(['a', 'b', or_(['c', 'd'])]), ['a', 'c', 'd'], False),
        (or_(['a', 'b']), ['a', 'b'], True),
        (or_(['a', 'b']), ['a'], True),
        (or_(['a', 'b', or_(['c', 'd'])]), ['a'], True),
        (or_(['a', 'b', or_(['c', 'd'])]), ['c'], True),
        (or_(['a', 'b', or_(['c', 'd'])]), ['e'], False),
        (or_(['a', 'b', and_(['c', 'd'])]), ['c'], False),
        (or_(['a', 'b', and_(['c', 'd'])]), ['c', 'd'], True),
    )
    @unpack
    def test_operator_eval(self, op, values, result):
        self.assertEqual(op.eval(values), result)