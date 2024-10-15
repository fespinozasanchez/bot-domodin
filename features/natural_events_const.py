import random as ra

EVENTS = {
    "Terremoto": {
        "msg": "¡Ha ocurrido un terremoto, las estructuras tiemblan, todos pierden {propiedades} propiedades!",
        "tier": [1,2,3,4,5,6,7,8,9,10],
        "tier_weight": [0.25, 0.25, 0.15, 0.1, 0.1, 0.05, 0.03, 0.03, 0.02, 0.02],
        "chance": 0.2,
        "url": "https://pillan.inf.uct.cl/~fespinoza/desastres/terremoto.webp",
        "color":"all"
    },
    "Huracan": {
        "msg": "¡Un huracán ha arrasado la costa, aumentando el desgaste de {propiedades} propiedades de cada usuario!",
        "tier": [1,2,3,4,5,6,7,8,9,10],
        "tier_weight": [0.25, 0.25, 0.15, 0.1, 0.1, 0.05, 0.03, 0.03, 0.02, 0.02],
        "chance": 0.2,
        "url" : "https://pillan.inf.uct.cl/~fespinoza/desastres/huracan.webp",
        "color":"all"
    },
    "Tsunami": {
        "msg": "¡Un tsunami imparable ha inundado la ciudad, {propiedades} propiedades azules han sido destruidas  para cada usuario!",
        "tier": [1,2,3,4,5,6,7,8,9,10],
        "tier_weight": [0.25, 0.25, 0.15, 0.1, 0.1, 0.05, 0.03, 0.03, 0.02, 0.02],
        "chance": 0.05,
        "url" : "https://pillan.inf.uct.cl/~fespinoza/desastres/tsunami.webp",
        "color":"blue"
    },
    "Volcan": {
        "msg": "¡Una erupción volcánica cubre el cielo de cenizas, {propiedades} propiedades rojas han sido destruidas para cada usuario!",
        "tier": [1,2,3,4,5,6,7,8,9,10],
        "tier_weight": [0.25, 0.25, 0.15, 0.1, 0.1, 0.05, 0.03, 0.03, 0.02, 0.02],
        "chance": 0.05,
        "url" : "https://pillan.inf.uct.cl/~fespinoza/desastres/volcan.webp",
        "color":"red"
    },
    "Incendio": {
        "msg": "¡Un incendio devastador se ha propagado,{propiedades} propiedades naranjas han sido destruidas para cada usuario!",
        "tier": [1,2,3,4,5,6,7,8,9,10],
        "tier_weight": [0.25, 0.25, 0.15, 0.1, 0.1, 0.05, 0.03, 0.03, 0.02, 0.02],
        "chance": 0.05,
        "url" : "https://pillan.inf.uct.cl/~fespinoza/desastres/incendio.webp",
        "color":"orange"
    },
    "Tornado": {
        "msg": "¡Un tornado furioso ha arrasado el vecindario, {propiedades} propiedades moradas han sido destruidas para cada usuario!",
        "tier": [1,2,3,4,5,6,7,8,9,10],
        "tier_weight": [0.25, 0.25, 0.15, 0.1, 0.1, 0.05, 0.03, 0.03, 0.02, 0.02],
        "chance": 0.05,
        "url" : "https://pillan.inf.uct.cl/~fespinoza/desastres/tornado.webp",
        "color":"purple"
    },
    "Avalancha": {
        "msg": "¡Una avalancha de nieve y rocas desciende rápidamente, {propiedades} propiedades rosadas han sido destruidas para cada usuario!",
        "tier": [1,2,3,4,5,6,7,8,9,10],
        "tier_weight": [0.25, 0.25, 0.15, 0.1, 0.1, 0.05, 0.03, 0.03, 0.02, 0.02],
        "chance": 0.05,
        "url" : "https://pillan.inf.uct.cl/~fespinoza/desastres/avalancha.webp",
        "color":"pink"
    },
    "Tormenta Electrica": {
        "msg": "¡Una tormenta eléctrica ha caído sobre la ciudad, {propiedades} propiedades amarillas han sido destruidas!",
        "tier": [1,2,3,4,5,6,7,8,9,10],
        "tier_weight": [0.25, 0.25, 0.15, 0.1, 0.1, 0.05, 0.03, 0.03, 0.02, 0.02],
        "chance": 0.05,
        "url" : "https://pillan.inf.uct.cl/~fespinoza/desastres/tormenta.webp",
        "color":"yellow"
    },
    "Meteorito de la Jurasica": {
        "msg": "¡Un meteorito de la era jurásica ha caído! El impacto es tan devastador que todos pierden todas sus propiedades.",
        "chance": 0.001,
        "tier": [1],
        "tier_weight": [1],
        "url" : "https://pillan.inf.uct.cl/~fespinoza/desastres/meteorito.webp",
        "color":"all"
    },

    "Domingo de Diosito": {
        "msg": "¡Es domingo de Diosito! Hoy todos los usuarios disfrutan de un día libre y reciben experiencia no pagada.",
        "chance": 0.299,
        "tier": [1],
        "tier_weight":[1],
        "url" : "https://pillan.inf.uct.cl/~fespinoza/desastres/normal.webp",
        "color":"all"
    }
}


def get_event_chance():
    return ra.choices(list(EVENTS.keys()), [v["chance"] for v in EVENTS.values()])[0]


def get_event_data( event_chance):
    return EVENTS[event_chance]


def get_event_tier(event_data):
    return ra.choices(event_data["tier"], event_data["tier_weight"])[0]

def get_event_msg(event_data):
    return event_data["msg"]

# a= get_event_chance()
# # b= get_event_data(a)
# # c= get_event_tier(b)
# # d= get_event_msg(b)
# # print(c,d.format(propiedades=15))


# data= get_event_data(a)
# msg= data["msg"]
# tier= data["tier"][0]
# print(msg.format(propiedades=15), tier)


