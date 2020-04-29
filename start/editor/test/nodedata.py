#coding:utf-8

nodes = [{
    "name": "Tile Collepsed",
    "category": "Tiles/Actions",
    "visibility": "unit",
    "events":{
        "Collepsed Succ": "DemoEvent",
        "Collepsed Fail": "DemoEvent"
    },
    "function": "flow_callback_tile_collasped",
    "args":{
        "collapsed_tile":"unit",
        "other_unit":"unit",
    }
},
{
    "name": "Wake Enemy",
    "category": "AI",
    "visibility": "all",
    "events":{
        "WakeUp": "DemoEvent"
    },
    "function": "flow_callback_ai_enemy",
    "args": {
        "enemy":"unit",
    },
},
{
    "name":"Multiply",
    "args":{
        "a":"float",
        "b":"float",
    },
    "returns":{
        "product":"float",
    },
    "query": True,
    "function": " return function(t) t.product = t.a * t.b return t end ",
},
{
    "name": "Giant Dust",
    "events": {
        "Armpit Left": "DemoEvent",
        "Armpit Right": "DemoEvent",
        "Elbow Left": "DemoEvent",
        "Elbow Right": "DemoEvent",
        "Hip Left": "DemoEvent",
        "Hip Right": "DemoEvent",
        "Knee Left": "DemoEvent",
        "Knee Right": "DemoEvent"
    },
    "function_map": [
        ["Armpit Left", "CinematicGiant.cb_dust_armpit_left"],
        ["Armpit Right", "CinematicGiant.cb_dust_armpit_right"],
        ["Elbow Left", "CinematicGiant.cb_dust_elbow_left"],
        ["Elbow Right", "CinematicGiant.cb_dust_elbow_right"],
        ["Hip Left", "CinematicGiant.cb_dust_hip_left"],
        ["Hip Right", "CinematicGiant.cb_dust_hip_right"],
        ["Knee Left", "CinematicGiant.cb_dust_knee_left"],
        ["Knee Right", "CinematicGiant.cb_dust_knee_right"],
    ],
    "args": {
        "unit": "unit",
    },
}]