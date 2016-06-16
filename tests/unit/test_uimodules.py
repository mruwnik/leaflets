import pytest

from collections import defaultdict

from leaflets.models.campaign import AddressStates
from leaflets.views.uimodules import (
    house_comparator, checklist_item, checklist_level,
    CHECKLIST_ITEM_TEMPLATE, CHECKLIST_LEVEL_TEMPLATE
)


@pytest.mark.parametrize('house', ('1', '12', '32424'))
def test_house_comparator_basic_nums(house):
    """Check whetner simple numbers are correctly handled."""
    assert house_comparator(house) == '%.20d' % int(house)


@pytest.mark.parametrize('house', ('gwge', None, '', 'asd', 2424))
def test_house_comparator_non_numeric(house):
    """Check whetner non numeric values are simply returned."""
    assert house_comparator(house) == (house or '')


@pytest.mark.parametrize('house, expected', (
    ('1-132', '%.20d-%.20d' % (1, 132)),
    ('13 33', '%.20d %.20d' % (13, 33)),
    ('1/3', '%.20d/%.20d' % (1, 3)),
    ('1a2b3c4d5e', '%.20da%.20db%.20dc%.20dd%.20de' % (1, 2, 3, 4, 5))
))
def test_house_comparator_compound_nums(house, expected):
    """Check if multiple numbers are correctly extracted."""
    assert house_comparator(house) == expected


@pytest.mark.parametrize('vals, expected', (
    (
        ['4', '1', '', None, 'asd', '00003', '1asd', '11', 'asd1', '2', '1asd1', '1/2'],
        ['', None, '1', '1/2', '1asd', '1asd1', '2', '00003', '4', '11', 'asd', 'asd1']
    ),
))
def test_house_sorting(vals, expected):
    """Check whether house are correctly sorted."""
    assert sorted(vals, key=house_comparator) == expected


class MockItem(object):
    """Mock a single CampaignAddress."""
    class MockAddress(object):
        """Mock an Address."""
        def __init__(self, id, house):
            self.id = id
            self.house = house

    def __init__(self, state, addr_id, house):
        self.state = state
        self.address = self.MockAddress(addr_id, house)


@pytest.mark.parametrize('item, selected', (
    (MockItem(AddressStates.selected, 12, '342'), ''),
    (MockItem(AddressStates.removed, 12, '342'), ''),
    (MockItem(AddressStates.marked, 12, '342'), 'checked'),
))
def test_checklist_item(item, selected):
    """Check if items are correctly rendered."""
    assert checklist_item(item) == CHECKLIST_ITEM_TEMPLATE.format(
        id=12, selected=selected, contents='342'
    )


@pytest.mark.parametrize('state, level_class', (
    (AddressStates.selected, ''), (AddressStates.marked, 'checked')
))
def test_checklist_level(state, level_class):
    """Check whether levels are correctly rendered."""
    item1 = MockItem(state, 1, '431')
    item2 = MockItem(state, 2, 'dwd')
    item3 = MockItem(state, 3, '31')
    item4 = MockItem(state, 4, '1')
    item5 = MockItem(state, 5, '531')

    items = defaultdict(
        MockItem,
        ((item.address.house, item) for item in [item1, item2, item3, item4, item5])
    )
    contents = ''.join(map(checklist_item, [item4, item3, item1, item5, item2]))
    rendered = CHECKLIST_LEVEL_TEMPLATE.format(
        level=5, id='id', label='id', html=contents, level_class=level_class
    )
    assert rendered == checklist_level('id', items, 5)
