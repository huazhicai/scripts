# coding:utf-8

scene = {
    'width': 5000,
    'height': 5000,
    'origin': 'center'
}

nodes = [
    {
        'id': 1,
        'type': '',
        'pos': {
            'x': -300,
            'y': -300
        }
    },
    {
        'id': 2,
        'type': '',
        'pos': {
            'x': 300,
            'y': -300
        }
    },
    {
        'id': 3,
        'type': '',
        'pos': {
            'x': 600,
            'y': 500,
        }
    }
]

edges = [
    {
        'start': 1,
        'end': 2,
        'startname': '',
        'endname': '',
        'linktype': 'unit'
    },
    {
        'start': 2,
        'end': 3,
        'startname': '',
        'endname': '',
        'linktype': 'event'
    }
]
