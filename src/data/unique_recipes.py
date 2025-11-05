"""
Unique Vendor Recipe Database
Based on https://poedb.tw/us/Vendor_recipe_system#VendorrecipesystemUnique
"""

# Recipe format:
# {
#     'name': 'Recipe Name',
#     'result': 'Item Name',
#     'ingredients': [
#         {'item': 'Item Name', 'quantity': 1},
#         ...
#     ],
#     'category': 'Category Name'
# }

UNIQUE_RECIPES = [
    # The Goddess Series
    {
        'name': 'The Goddess Scorned',
        'result': 'The Goddess Scorned',
        'ingredients': [
            {'item': 'The Goddess Bound', 'quantity': 1},
            {'item': "Graceful Assault", 'quantity': 1},
        ],
        'category': 'Goddess Series',
        'description': 'Upgrade The Goddess Bound to The Goddess Scorned'
    },
    {
        'name': 'The Goddess Unleashed',
        'result': 'The Goddess Unleashed',
        'ingredients': [
            {'item': 'The Goddess Scorned', 'quantity': 1},
            {'item': "Romira's Banquet", 'quantity': 1},
            {'item': "Slitherpinch", 'quantity': 1},
        ],
        'category': 'Goddess Series',
        'description': 'Upgrade The Goddess Scorned to The Goddess Unleashed'
    },

    # Loreweave Recipe
    {
        'name': 'Loreweave',
        'result': 'Loreweave',
        'ingredients': [
            {'item': 'Unique Ring', 'quantity': 60},
        ],
        'category': 'Popular Recipes',
        'description': 'Vendor 60 unique rings to get Loreweave'
    },

    # Atziri's Splendour Recipes
    {
        'name': "Atziri's Splendour (Armour)",
        'result': "Atziri's Splendour",
        'ingredients': [
            {'item': "Atziri's Acuity", 'quantity': 1},
            {'item': "Atziri's Mirror", 'quantity': 1},
            {'item': "The Vertex", 'quantity': 1},
            {'item': "Doryani's Catalyst", 'quantity': 1},
        ],
        'category': "Atziri's Items",
        'description': 'Creates Armour variant of Atziri\'s Splendour'
    },
    {
        'name': "Atziri's Splendour (Evasion)",
        'result': "Atziri's Splendour",
        'ingredients': [
            {'item': "Atziri's Acuity", 'quantity': 1},
            {'item': "Atziri's Mirror", 'quantity': 1},
            {'item': "The Vertex", 'quantity': 1},
            {'item': "Doryani's Fist", 'quantity': 1},
        ],
        'category': "Atziri's Items",
        'description': 'Creates Evasion variant of Atziri\'s Splendour'
    },
    {
        'name': "Atziri's Splendour (Energy Shield)",
        'result': "Atziri's Splendour",
        'ingredients': [
            {'item': "Atziri's Acuity", 'quantity': 1},
            {'item': "Atziri's Mirror", 'quantity': 1},
            {'item': "The Vertex", 'quantity': 1},
            {'item': "Doryani's Invitation", 'quantity': 1},
        ],
        'category': "Atziri's Items",
        'description': 'Creates Energy Shield variant of Atziri\'s Splendour'
    },

    # The Anima Stone
    {
        'name': 'The Anima Stone',
        'result': 'The Anima Stone',
        'ingredients': [
            {'item': 'Primordial Might', 'quantity': 1},
            {'item': 'Primordial Eminence', 'quantity': 1},
            {'item': 'Primordial Harmony', 'quantity': 1},
        ],
        'category': 'Golem Items',
        'description': 'Combine Primordial jewels to create The Anima Stone'
    },

    # Voidforge Recipe
    {
        'name': 'Voidforge',
        'result': 'Voidforge',
        'ingredients': [
            {'item': 'Starforge', 'quantity': 1},
            {'item': 'Infernal Blade', 'quantity': 1},
        ],
        'category': 'Special Weapons',
        'description': 'Combine Starforge with Infernal Blade to create Voidforge'
    },

    # Duskblight/Dusktoe/Duskblight Recipe
    {
        'name': 'Sunspite',
        'result': 'Sunspite',
        'ingredients': [
            {'item': 'Duskblight', 'quantity': 1},
            {'item': 'Dusktoe', 'quantity': 1},
            {'item': 'Duskblight', 'quantity': 1},
        ],
        'category': 'Dusk Series',
        'description': 'Combine Dusk items to create Sunspite'
    },

    # The Searing Touch
    {
        'name': 'The Searing Touch (Upgraded)',
        'result': 'The Searing Touch',
        'ingredients': [
            {'item': 'The Searing Touch', 'quantity': 1},
            {'item': 'Orb of Chance', 'quantity': 1},
        ],
        'category': 'Staff Upgrades',
        'description': 'Upgrade The Searing Touch'
    },
]

# Currency items commonly used in recipes
CURRENCY_ITEMS = {
    'Orb of Chance': 'currency',
    'Chaos Orb': 'currency',
    'Divine Orb': 'currency',
    'Exalted Orb': 'currency',
    'Orb of Fusing': 'currency',
    'Chromatic Orb': 'currency',
    'Jeweller\'s Orb': 'currency',
}


def get_all_recipes():
    """Get all available recipes"""
    return UNIQUE_RECIPES


def get_recipes_by_category(category):
    """Get recipes filtered by category"""
    return [r for r in UNIQUE_RECIPES if r['category'] == category]


def get_recipe_categories():
    """Get all unique categories"""
    return list(set(r['category'] for r in UNIQUE_RECIPES))


def search_recipes(query):
    """Search recipes by name or result"""
    query = query.lower()
    return [
        r for r in UNIQUE_RECIPES
        if query in r['name'].lower() or query in r['result'].lower()
    ]


def get_recipe_by_name(name):
    """Get specific recipe by name"""
    for recipe in UNIQUE_RECIPES:
        if recipe['name'] == name:
            return recipe
    return None


def is_currency_item(item_name):
    """Check if item is a currency item"""
    return item_name in CURRENCY_ITEMS
