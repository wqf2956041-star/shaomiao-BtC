#!/usr/bin/env python3
#
# ╔══════════════════════════════════════════════════════════╗
# ║  r5hhhh2ssi;;iiiiiiiiii;r2hMMMMMMMMMMMMMhhhh5r;ii;;;;; ║
# ║  A233hhhh3Arrrrsiiiiiii2hMMMMhhMMMMMMMMMhhhhMMA;;;;;;; ║
# ║  A25555333552AXAsiiiir3MMhMMhhMMMMhhMMMMMMMMhhM5ii;;; ║
# ║  A22255555352AXXriiirhMhMMhhhMMMMMMhhMMhMMMMMMhM2iiii ║
# ║  ssssXsirsrrrrrrrrrsM3hMM3h3MhMMhMMM3hMh3MMMhhMMMhri ║
# ║  irrrrrrrrrrrrrrrriXh3MMhhh5M2hhh3MM53h53hMMhhhMMMXr ║
# ║  rrrrrrrrrrrrrrrrrrshhMH33h3hA52M5hH22hA33hhhhhhMM3h ║
# ║  rrrrrrrrrrrrrrrrrrA33HM253h53AXA32MAX223555Mhh3M3MS ║
# ║  rrrrrrrrrrrrrrrrrr3X3h33SSH3iH#9GhAhS9h;MHGM33hH3MM ║
# ║  rrrrrrrrrrrsssAAssssrr2hM3hG#99#9#H9####9SMh33523MG ║
# ║  srrsXXXXsXA553MhMHHHH2XAAAX2MS9###S##9#G5XsXsA5HSG ║
# ║  s222hG##MHSSSSSSGSSSGH2MAsAAX3S999999#G2XX2sAMHHHG ║
# ║  5HGGGS#9#SS##SS#####SSGGG5AMAs3MH##SHGG35Hh3MMMHHH ║
# ║  MHGSSS999##99#SSSSS#SGSSSSHMhh3M353HS9GH#9S#GhhMMH ║
# ║  GGSSSS##9####SSSSSSSSGGGGGGHHMh#SGS999SHSS###GMMHH ║
# ║  GGGGGGGGGGGGGGSSSSSSSSSSGGHGHM#9999#999GHSSGGSGGGH ║
# ║  HHHMHHHGGGGGGGGGHHHHMMMMS#99GMG#9999#SS9B&B9SHMhMM ║
# ║  hhhhhhhhhhhhhhh333hhHG3H9&&B&&#SG#9SS9B&&&&&GH9Gh3 ║
# ║  GitHub Crypto Leak Scanner       v2 ║
# ╚══════════════════════════════════════════════════════════╝
"""
GitHub Crypto Credential Leak Scanner
═══════════════════════════════════════
GitHub 公开仓库虚拟货币地址+私钥泄露扫描器 — 覆盖 BTC/ETH/SOL/TRX 等 20+ 链
支持完整私钥/地址/WIF/助记词提取

用法:
    python github_key_scanner.py                       # 无 token
    python github_key_scanner.py --token ghp_xxx       # 有 token 加速
    python github_key_scanner.py --token ghp_xxx --deep    # 深度扫描(46搜索词)

Token: https://github.com/settings/tokens -> classic -> public_repo
"""

import subprocess as _sp, sys as _sys, importlib as _il

try:
    import requests  # type: ignore
except ImportError:
    requests = None

import json, re, os, time, hashlib, argparse, sys, math
import base64
import struct
from typing import Optional, Tuple, List, Dict, Any

# ═══════ BIP39 助记词词库 (2048 words) ═══════
BIP39_WORDS = frozenset({
    'abandon',
    'ability',
    'able',
    'about',
    'above',
    'absent',
    'absorb',
    'abstract',
    'absurd',
    'abuse',
    'access',
    'accident',
    'account',
    'accuse',
    'achieve',
    'acid',
    'acoustic',
    'acquire',
    'across',
    'act',
    'action',
    'actor',
    'actress',
    'actual',
    'adapt',
    'add',
    'addict',
    'address',
    'adjust',
    'admit',
    'adult',
    'advance',
    'advice',
    'aerobic',
    'affair',
    'afford',
    'afraid',
    'again',
    'age',
    'agent',
    'agree',
    'ahead',
    'aim',
    'air',
    'airport',
    'aisle',
    'alarm',
    'album',
    'alcohol',
    'alert',
    'alien',
    'all',
    'alley',
    'allow',
    'almost',
    'alone',
    'alpha',
    'already',
    'also',
    'alter',
    'always',
    'amateur',
    'amazing',
    'among',
    'amount',
    'amused',
    'analyst',
    'anchor',
    'ancient',
    'anger',
    'angle',
    'angry',
    'animal',
    'ankle',
    'announce',
    'annual',
    'another',
    'answer',
    'antenna',
    'antique',
    'anxiety',
    'any',
    'apart',
    'apology',
    'appear',
    'apple',
    'approve',
    'april',
    'arch',
    'arctic',
    'area',
    'arena',
    'argue',
    'arm',
    'armed',
    'armor',
    'army',
    'around',
    'arrange',
    'arrest',
    'arrive',
    'arrow',
    'art',
    'artefact',
    'artist',
    'artwork',
    'ask',
    'aspect',
    'assault',
    'asset',
    'assist',
    'assume',
    'asthma',
    'athlete',
    'atom',
    'attack',
    'attend',
    'attitude',
    'attract',
    'auction',
    'audit',
    'august',
    'aunt',
    'author',
    'auto',
    'autumn',
    'average',
    'avocado',
    'avoid',
    'awake',
    'aware',
    'away',
    'awesome',
    'awful',
    'awkward',
    'axis',
    'baby',
    'bachelor',
    'bacon',
    'badge',
    'bag',
    'balance',
    'balcony',
    'ball',
    'bamboo',
    'banana',
    'banner',
    'bar',
    'barely',
    'bargain',
    'barrel',
    'base',
    'basic',
    'basket',
    'battle',
    'beach',
    'bean',
    'beauty',
    'because',
    'become',
    'beef',
    'before',
    'begin',
    'behave',
    'behind',
    'believe',
    'below',
    'belt',
    'bench',
    'benefit',
    'best',
    'betray',
    'better',
    'between',
    'beyond',
    'bicycle',
    'bid',
    'bike',
    'bind',
    'biology',
    'bird',
    'birth',
    'bitter',
    'black',
    'blade',
    'blame',
    'blanket',
    'blast',
    'bleak',
    'bless',
    'blind',
    'blood',
    'blossom',
    'blouse',
    'blue',
    'blur',
    'blush',
    'board',
    'boat',
    'body',
    'boil',
    'bomb',
    'bone',
    'bonus',
    'book',
    'boost',
    'border',
    'boring',
    'borrow',
    'boss',
    'bottom',
    'bounce',
    'box',
    'boy',
    'bracket',
    'brain',
    'brand',
    'brass',
    'brave',
    'bread',
    'breeze',
    'brick',
    'bridge',
    'brief',
    'bright',
    'bring',
    'brisk',
    'broccoli',
    'broken',
    'bronze',
    'broom',
    'brother',
    'brown',
    'brush',
    'bubble',
    'buddy',
    'budget',
    'buffalo',
    'build',
    'bulb',
    'bulk',
    'bullet',
    'bundle',
    'bunker',
    'burden',
    'burger',
    'burst',
    'bus',
    'business',
    'busy',
    'butter',
    'buyer',
    'buzz',
    'cabbage',
    'cabin',
    'cable',
    'cactus',
    'cage',
    'cake',
    'call',
    'calm',
    'camera',
    'camp',
    'can',
    'canal',
    'cancel',
    'candy',
    'cannon',
    'canoe',
    'canvas',
    'canyon',
    'capable',
    'capital',
    'captain',
    'car',
    'carbon',
    'card',
    'cargo',
    'carpet',
    'carry',
    'cart',
    'case',
    'cash',
    'casino',
    'castle',
    'casual',
    'cat',
    'catalog',
    'catch',
    'category',
    'cattle',
    'caught',
    'cause',
    'caution',
    'cave',
    'ceiling',
    'celery',
    'cement',
    'census',
    'century',
    'cereal',
    'certain',
    'chair',
    'chalk',
    'champion',
    'change',
    'chaos',
    'chapter',
    'charge',
    'chase',
    'chat',
    'cheap',
    'check',
    'cheese',
    'chef',
    'cherry',
    'chest',
    'chicken',
    'chief',
    'child',
    'chimney',
    'choice',
    'choose',
    'chronic',
    'chuckle',
    'chunk',
    'churn',
    'cigar',
    'cinnamon',
    'circle',
    'citizen',
    'city',
    'civil',
    'claim',
    'clap',
    'clarify',
    'claw',
    'clay',
    'clean',
    'clerk',
    'clever',
    'click',
    'client',
    'cliff',
    'climb',
    'clinic',
    'clip',
    'clock',
    'clog',
    'close',
    'cloth',
    'cloud',
    'clown',
    'club',
    'clump',
    'cluster',
    'clutch',
    'coach',
    'coast',
    'coconut',
    'code',
    'coffee',
    'coil',
    'coin',
    'collect',
    'color',
    'column',
    'combine',
    'come',
    'comfort',
    'comic',
    'common',
    'company',
    'concert',
    'conduct',
    'confirm',
    'congress',
    'connect',
    'consider',
    'control',
    'convince',
    'cook',
    'cool',
    'copper',
    'copy',
    'coral',
    'core',
    'corn',
    'correct',
    'cost',
    'cotton',
    'couch',
    'country',
    'couple',
    'course',
    'cousin',
    'cover',
    'coyote',
    'crack',
    'cradle',
    'craft',
    'cram',
    'crane',
    'crash',
    'crater',
    'crawl',
    'crazy',
    'cream',
    'credit',
    'creek',
    'crew',
    'cricket',
    'crime',
    'crisp',
    'critic',
    'crop',
    'cross',
    'crouch',
    'crowd',
    'crucial',
    'cruel',
    'cruise',
    'crumble',
    'crunch',
    'crush',
    'cry',
    'crystal',
    'cube',
    'culture',
    'cup',
    'cupboard',
    'curious',
    'current',
    'curtain',
    'curve',
    'cushion',
    'custom',
    'cute',
    'cycle',
    'dad',
    'damage',
    'damp',
    'dance',
    'danger',
    'daring',
    'dash',
    'daughter',
    'dawn',
    'day',
    'deal',
    'debate',
    'debris',
    'decade',
    'december',
    'decide',
    'decline',
    'decorate',
    'decrease',
    'deer',
    'defense',
    'define',
    'defy',
    'degree',
    'delay',
    'deliver',
    'demand',
    'demise',
    'denial',
    'dentist',
    'deny',
    'depart',
    'depend',
    'deposit',
    'depth',
    'deputy',
    'derive',
    'describe',
    'desert',
    'design',
    'desk',
    'despair',
    'destroy',
    'detail',
    'detect',
    'develop',
    'device',
    'devote',
    'diagram',
    'dial',
    'diamond',
    'diary',
    'dice',
    'diesel',
    'diet',
    'differ',
    'digital',
    'dignity',
    'dilemma',
    'dinner',
    'dinosaur',
    'direct',
    'dirt',
    'disagree',
    'discover',
    'disease',
    'dish',
    'dismiss',
    'disorder',
    'display',
    'distance',
    'divert',
    'divide',
    'divorce',
    'dizzy',
    'doctor',
    'document',
    'dog',
    'doll',
    'dolphin',
    'domain',
    'donate',
    'donkey',
    'donor',
    'door',
    'dose',
    'double',
    'dove',
    'draft',
    'dragon',
    'drama',
    'drastic',
    'draw',
    'dream',
    'dress',
    'drift',
    'drill',
    'drink',
    'drip',
    'drive',
    'drop',
    'drum',
    'dry',
    'duck',
    'dumb',
    'dune',
    'during',
    'dust',
    'dutch',
    'duty',
    'dwarf',
    'dynamic',
    'eager',
    'eagle',
    'early',
    'earn',
    'earth',
    'easily',
    'east',
    'easy',
    'echo',
    'ecology',
    'economy',
    'edge',
    'edit',
    'educate',
    'effort',
    'egg',
    'eight',
    'either',
    'elbow',
    'elder',
    'electric',
    'elegant',
    'element',
    'elephant',
    'elevator',
    'elite',
    'else',
    'embark',
    'embody',
    'embrace',
    'emerge',
    'emotion',
    'employ',
    'empower',
    'empty',
    'enable',
    'enact',
    'end',
    'endless',
    'endorse',
    'enemy',
    'energy',
    'enforce',
    'engage',
    'engine',
    'enhance',
    'enjoy',
    'enlist',
    'enough',
    'enrich',
    'enroll',
    'ensure',
    'enter',
    'entire',
    'entry',
    'envelope',
    'episode',
    'equal',
    'equip',
    'era',
    'erase',
    'erode',
    'erosion',
    'error',
    'erupt',
    'escape',
    'essay',
    'essence',
    'estate',
    'eternal',
    'ethics',
    'evidence',
    'evil',
    'evoke',
    'evolve',
    'exact',
    'example',
    'excess',
    'exchange',
    'excite',
    'exclude',
    'excuse',
    'execute',
    'exercise',
    'exhaust',
    'exhibit',
    'exile',
    'exist',
    'exit',
    'exotic',
    'expand',
    'expect',
    'expire',
    'explain',
    'expose',
    'express',
    'extend',
    'extra',
    'eye',
    'eyebrow',
    'fabric',
    'face',
    'faculty',
    'fade',
    'faint',
    'faith',
    'fall',
    'false',
    'fame',
    'family',
    'famous',
    'fan',
    'fancy',
    'fantasy',
    'farm',
    'fashion',
    'fat',
    'fatal',
    'father',
    'fatigue',
    'fault',
    'favorite',
    'feature',
    'february',
    'federal',
    'fee',
    'feed',
    'feel',
    'female',
    'fence',
    'festival',
    'fetch',
    'fever',
    'few',
    'fiber',
    'fiction',
    'field',
    'figure',
    'file',
    'film',
    'filter',
    'final',
    'find',
    'fine',
    'finger',
    'finish',
    'fire',
    'firm',
    'first',
    'fiscal',
    'fish',
    'fit',
    'fitness',
    'fix',
    'flag',
    'flame',
    'flash',
    'flat',
    'flavor',
    'flee',
    'flight',
    'flip',
    'float',
    'flock',
    'floor',
    'flower',
    'fluid',
    'flush',
    'fly',
    'foam',
    'focus',
    'fog',
    'foil',
    'fold',
    'follow',
    'food',
    'foot',
    'force',
    'forest',
    'forget',
    'fork',
    'fortune',
    'forum',
    'forward',
    'fossil',
    'foster',
    'found',
    'fox',
    'fragile',
    'frame',
    'frequent',
    'fresh',
    'friend',
    'fringe',
    'frog',
    'front',
    'frost',
    'frown',
    'frozen',
    'fruit',
    'fuel',
    'fun',
    'funny',
    'furnace',
    'fury',
    'future',
    'gadget',
    'gain',
    'galaxy',
    'gallery',
    'game',
    'gap',
    'garage',
    'garbage',
    'garden',
    'garlic',
    'garment',
    'gas',
    'gasp',
    'gate',
    'gather',
    'gauge',
    'gaze',
    'general',
    'genius',
    'genre',
    'gentle',
    'genuine',
    'gesture',
    'ghost',
    'giant',
    'gift',
    'giggle',
    'ginger',
    'giraffe',
    'girl',
    'give',
    'glad',
    'glance',
    'glare',
    'glass',
    'glide',
    'glimpse',
    'globe',
    'gloom',
    'glory',
    'glove',
    'glow',
    'glue',
    'goat',
    'goddess',
    'gold',
    'good',
    'goose',
    'gorilla',
    'gospel',
    'gossip',
    'govern',
    'gown',
    'grab',
    'grace',
    'grain',
    'grant',
    'grape',
    'grass',
    'gravity',
    'great',
    'green',
    'grid',
    'grief',
    'grit',
    'grocery',
    'group',
    'grow',
    'grunt',
    'guard',
    'guess',
    'guide',
    'guilt',
    'guitar',
    'gun',
    'gym',
    'habit',
    'hair',
    'half',
    'hammer',
    'hamster',
    'hand',
    'happy',
    'harbor',
    'hard',
    'harsh',
    'harvest',
    'hat',
    'have',
    'hawk',
    'hazard',
    'head',
    'health',
    'heart',
    'heavy',
    'hedgehog',
    'height',
    'hello',
    'helmet',
    'help',
    'hen',
    'hero',
    'hidden',
    'high',
    'hill',
    'hint',
    'hip',
    'hire',
    'history',
    'hobby',
    'hockey',
    'hold',
    'hole',
    'holiday',
    'hollow',
    'home',
    'honey',
    'hood',
    'hope',
    'horn',
    'horror',
    'horse',
    'hospital',
    'host',
    'hotel',
    'hour',
    'hover',
    'hub',
    'huge',
    'human',
    'humble',
    'humor',
    'hundred',
    'hungry',
    'hunt',
    'hurdle',
    'hurry',
    'hurt',
    'husband',
    'hybrid',
    'ice',
    'icon',
    'idea',
    'identify',
    'idle',
    'ignore',
    'ill',
    'illegal',
    'illness',
    'image',
    'imitate',
    'immense',
    'immune',
    'impact',
    'impose',
    'improve',
    'impulse',
    'inch',
    'include',
    'income',
    'increase',
    'index',
    'indicate',
    'indoor',
    'industry',
    'infant',
    'inflict',
    'inform',
    'inhale',
    'inherit',
    'initial',
    'inject',
    'injury',
    'inmate',
    'inner',
    'innocent',
    'input',
    'inquiry',
    'insane',
    'insect',
    'inside',
    'inspire',
    'install',
    'intact',
    'interest',
    'into',
    'invest',
    'invite',
    'involve',
    'iron',
    'island',
    'isolate',
    'issue',
    'item',
    'ivory',
    'jacket',
    'jaguar',
    'jar',
    'jazz',
    'jealous',
    'jeans',
    'jelly',
    'jewel',
    'job',
    'join',
    'joke',
    'journey',
    'joy',
    'judge',
    'juice',
    'jump',
    'jungle',
    'junior',
    'junk',
    'just',
    'kangaroo',
    'keen',
    'keep',
    'ketchup',
    'key',
    'kick',
    'kid',
    'kidney',
    'kind',
    'kingdom',
    'kiss',
    'kit',
    'kitchen',
    'kite',
    'kitten',
    'kiwi',
    'knee',
    'knife',
    'knock',
    'know',
    'lab',
    'label',
    'labor',
    'ladder',
    'lady',
    'lake',
    'lamp',
    'language',
    'laptop',
    'large',
    'later',
    'latin',
    'laugh',
    'laundry',
    'lava',
    'law',
    'lawn',
    'lawsuit',
    'layer',
    'lazy',
    'leader',
    'leaf',
    'learn',
    'leave',
    'lecture',
    'left',
    'leg',
    'legal',
    'legend',
    'leisure',
    'lemon',
    'lend',
    'length',
    'lens',
    'leopard',
    'lesson',
    'letter',
    'level',
    'liar',
    'liberty',
    'library',
    'license',
    'life',
    'lift',
    'light',
    'like',
    'limb',
    'limit',
    'link',
    'lion',
    'liquid',
    'list',
    'little',
    'live',
    'lizard',
    'load',
    'loan',
    'lobster',
    'local',
    'lock',
    'logic',
    'lonely',
    'long',
    'loop',
    'lottery',
    'loud',
    'lounge',
    'love',
    'loyal',
    'lucky',
    'luggage',
    'lumber',
    'lunar',
    'lunch',
    'luxury',
    'lyrics',
    'machine',
    'mad',
    'magic',
    'magnet',
    'maid',
    'mail',
    'main',
    'major',
    'make',
    'mammal',
    'man',
    'manage',
    'mandate',
    'mango',
    'mansion',
    'manual',
    'maple',
    'marble',
    'march',
    'margin',
    'marine',
    'market',
    'marriage',
    'mask',
    'mass',
    'master',
    'match',
    'material',
    'math',
    'matrix',
    'matter',
    'maximum',
    'maze',
    'meadow',
    'mean',
    'measure',
    'meat',
    'mechanic',
    'medal',
    'media',
    'melody',
    'melt',
    'member',
    'memory',
    'mention',
    'menu',
    'mercy',
    'merge',
    'merit',
    'merry',
    'mesh',
    'message',
    'metal',
    'method',
    'middle',
    'midnight',
    'milk',
    'million',
    'mimic',
    'mind',
    'minimum',
    'minor',
    'minute',
    'miracle',
    'mirror',
    'misery',
    'miss',
    'mistake',
    'mix',
    'mixed',
    'mixture',
    'mobile',
    'model',
    'modify',
    'mom',
    'moment',
    'monitor',
    'monkey',
    'monster',
    'month',
    'moon',
    'moral',
    'more',
    'morning',
    'mosquito',
    'mother',
    'motion',
    'motor',
    'mountain',
    'mouse',
    'move',
    'movie',
    'much',
    'muffin',
    'mule',
    'multiply',
    'muscle',
    'museum',
    'mushroom',
    'music',
    'must',
    'mutual',
    'myself',
    'mystery',
    'myth',
    'naive',
    'name',
    'napkin',
    'narrow',
    'nasty',
    'nation',
    'nature',
    'near',
    'neck',
    'need',
    'negative',
    'neglect',
    'neither',
    'nephew',
    'nerve',
    'nest',
    'net',
    'network',
    'neutral',
    'never',
    'news',
    'next',
    'nice',
    'night',
    'noble',
    'noise',
    'nominee',
    'noodle',
    'normal',
    'north',
    'nose',
    'notable',
    'note',
    'nothing',
    'notice',
    'novel',
    'now',
    'nuclear',
    'number',
    'nurse',
    'nut',
    'oak',
    'obey',
    'object',
    'oblige',
    'obscure',
    'observe',
    'obtain',
    'obvious',
    'occur',
    'ocean',
    'october',
    'odor',
    'off',
    'offer',
    'office',
    'often',
    'oil',
    'okay',
    'old',
    'olive',
    'olympic',
    'omit',
    'once',
    'one',
    'onion',
    'online',
    'only',
    'open',
    'opera',
    'opinion',
    'oppose',
    'option',
    'orange',
    'orbit',
    'orchard',
    'order',
    'ordinary',
    'organ',
    'orient',
    'original',
    'orphan',
    'ostrich',
    'other',
    'outdoor',
    'outer',
    'output',
    'outside',
    'oval',
    'oven',
    'over',
    'own',
    'owner',
    'oxygen',
    'oyster',
    'ozone',
    'pact',
    'paddle',
    'page',
    'pair',
    'palace',
    'palm',
    'panda',
    'panel',
    'panic',
    'panther',
    'paper',
    'parade',
    'parent',
    'park',
    'parrot',
    'party',
    'pass',
    'patch',
    'path',
    'patient',
    'patrol',
    'pattern',
    'pause',
    'pave',
    'payment',
    'peace',
    'peanut',
    'pear',
    'peasant',
    'pelican',
    'pen',
    'penalty',
    'pencil',
    'people',
    'pepper',
    'perfect',
    'permit',
    'person',
    'pet',
    'phone',
    'photo',
    'phrase',
    'physical',
    'piano',
    'picnic',
    'picture',
    'piece',
    'pig',
    'pigeon',
    'pill',
    'pilot',
    'pink',
    'pioneer',
    'pipe',
    'pistol',
    'pitch',
    'pizza',
    'place',
    'planet',
    'plastic',
    'plate',
    'play',
    'please',
    'pledge',
    'pluck',
    'plug',
    'plunge',
    'poem',
    'poet',
    'point',
    'polar',
    'pole',
    'police',
    'pond',
    'pony',
    'pool',
    'popular',
    'portion',
    'position',
    'possible',
    'post',
    'potato',
    'pottery',
    'poverty',
    'powder',
    'power',
    'practice',
    'praise',
    'predict',
    'prefer',
    'prepare',
    'present',
    'pretty',
    'prevent',
    'price',
    'pride',
    'primary',
    'print',
    'priority',
    'prison',
    'private',
    'prize',
    'problem',
    'process',
    'produce',
    'profit',
    'program',
    'project',
    'promote',
    'proof',
    'property',
    'prosper',
    'protect',
    'proud',
    'provide',
    'public',
    'pudding',
    'pull',
    'pulp',
    'pulse',
    'pumpkin',
    'punch',
    'pupil',
    'puppy',
    'purchase',
    'purity',
    'purpose',
    'purse',
    'push',
    'put',
    'puzzle',
    'pyramid',
    'quality',
    'quantum',
    'quarter',
    'question',
    'quick',
    'quit',
    'quiz',
    'quote',
    'rabbit',
    'raccoon',
    'race',
    'rack',
    'radar',
    'radio',
    'rail',
    'rain',
    'raise',
    'rally',
    'ramp',
    'ranch',
    'random',
    'range',
    'rapid',
    'rare',
    'rate',
    'rather',
    'raven',
    'raw',
    'razor',
    'ready',
    'real',
    'reason',
    'rebel',
    'rebuild',
    'recall',
    'receive',
    'recipe',
    'record',
    'recycle',
    'reduce',
    'reflect',
    'reform',
    'refuse',
    'region',
    'regret',
    'regular',
    'reject',
    'relax',
    'release',
    'relief',
    'rely',
    'remain',
    'remember',
    'remind',
    'remove',
    'render',
    'renew',
    'rent',
    'reopen',
    'repair',
    'repeat',
    'replace',
    'report',
    'require',
    'rescue',
    'resemble',
    'resist',
    'resource',
    'response',
    'result',
    'retire',
    'retreat',
    'return',
    'reunion',
    'reveal',
    'review',
    'reward',
    'rhythm',
    'rib',
    'ribbon',
    'rice',
    'rich',
    'ride',
    'ridge',
    'rifle',
    'right',
    'rigid',
    'ring',
    'riot',
    'ripple',
    'risk',
    'ritual',
    'rival',
    'river',
    'road',
    'roast',
    'robot',
    'robust',
    'rocket',
    'romance',
    'roof',
    'rookie',
    'room',
    'rose',
    'rotate',
    'rough',
    'round',
    'route',
    'royal',
    'rubber',
    'rude',
    'rug',
    'rule',
    'run',
    'runway',
    'rural',
    'sad',
    'saddle',
    'sadness',
    'safe',
    'sail',
    'salad',
    'salmon',
    'salon',
    'salt',
    'salute',
    'same',
    'sample',
    'sand',
    'satisfy',
    'satoshi',
    'sauce',
    'sausage',
    'save',
    'say',
    'scale',
    'scan',
    'scare',
    'scatter',
    'scene',
    'scheme',
    'school',
    'science',
    'scissors',
    'scorpion',
    'scout',
    'scrap',
    'screen',
    'script',
    'scrub',
    'sea',
    'search',
    'season',
    'seat',
    'second',
    'secret',
    'section',
    'security',
    'seed',
    'seek',
    'segment',
    'select',
    'sell',
    'seminar',
    'senior',
    'sense',
    'sentence',
    'series',
    'service',
    'session',
    'settle',
    'setup',
    'seven',
    'shadow',
    'shaft',
    'shallow',
    'share',
    'shed',
    'shell',
    'sheriff',
    'shield',
    'shift',
    'shine',
    'ship',
    'shiver',
    'shock',
    'shoe',
    'shoot',
    'shop',
    'short',
    'shoulder',
    'shove',
    'shrimp',
    'shrug',
    'shuffle',
    'shy',
    'sibling',
    'sick',
    'side',
    'siege',
    'sight',
    'sign',
    'silent',
    'silk',
    'silly',
    'silver',
    'similar',
    'simple',
    'since',
    'sing',
    'siren',
    'sister',
    'situate',
    'six',
    'size',
    'skate',
    'sketch',
    'ski',
    'skill',
    'skin',
    'skirt',
    'skull',
    'slab',
    'slam',
    'sleep',
    'slender',
    'slice',
    'slide',
    'slight',
    'slim',
    'slogan',
    'slot',
    'slow',
    'slush',
    'small',
    'smart',
    'smile',
    'smoke',
    'smooth',
    'snack',
    'snake',
    'snap',
    'sniff',
    'snow',
    'soap',
    'soccer',
    'social',
    'sock',
    'soda',
    'soft',
    'solar',
    'soldier',
    'solid',
    'solution',
    'solve',
    'someone',
    'song',
    'soon',
    'sorry',
    'sort',
    'soul',
    'sound',
    'soup',
    'source',
    'south',
    'space',
    'spare',
    'spatial',
    'spawn',
    'speak',
    'special',
    'speed',
    'spell',
    'spend',
    'sphere',
    'spice',
    'spider',
    'spike',
    'spin',
    'spirit',
    'split',
    'spoil',
    'sponsor',
    'spoon',
    'sport',
    'spot',
    'spray',
    'spread',
    'spring',
    'spy',
    'square',
    'squeeze',
    'squirrel',
    'stable',
    'stadium',
    'staff',
    'stage',
    'stairs',
    'stamp',
    'stand',
    'start',
    'state',
    'stay',
    'steak',
    'steel',
    'stem',
    'step',
    'stereo',
    'stick',
    'still',
    'sting',
    'stock',
    'stomach',
    'stone',
    'stool',
    'story',
    'stove',
    'strategy',
    'street',
    'strike',
    'strong',
    'struggle',
    'student',
    'stuff',
    'stumble',
    'style',
    'subject',
    'submit',
    'subway',
    'success',
    'such',
    'sudden',
    'suffer',
    'sugar',
    'suggest',
    'suit',
    'summer',
    'sun',
    'sunny',
    'sunset',
    'super',
    'supply',
    'supreme',
    'sure',
    'surface',
    'surge',
    'surprise',
    'surround',
    'survey',
    'suspect',
    'sustain',
    'swallow',
    'swamp',
    'swap',
    'swarm',
    'swear',
    'sweet',
    'swift',
    'swim',
    'swing',
    'switch',
    'sword',
    'symbol',
    'symptom',
    'syrup',
    'system',
    'table',
    'tackle',
    'tag',
    'tail',
    'talent',
    'talk',
    'tank',
    'tape',
    'target',
    'task',
    'taste',
    'tattoo',
    'taxi',
    'teach',
    'team',
    'tell',
    'ten',
    'tenant',
    'tennis',
    'tent',
    'term',
    'test',
    'text',
    'thank',
    'that',
    'theme',
    'then',
    'theory',
    'there',
    'they',
    'thing',
    'this',
    'thought',
    'three',
    'thrive',
    'throw',
    'thumb',
    'thunder',
    'ticket',
    'tide',
    'tiger',
    'tilt',
    'timber',
    'time',
    'tiny',
    'tip',
    'tired',
    'tissue',
    'title',
    'toast',
    'tobacco',
    'today',
    'toddler',
    'toe',
    'together',
    'toilet',
    'token',
    'tomato',
    'tomorrow',
    'tone',
    'tongue',
    'tonight',
    'tool',
    'tooth',
    'top',
    'topic',
    'topple',
    'torch',
    'tornado',
    'tortoise',
    'toss',
    'total',
    'tourist',
    'toward',
    'tower',
    'town',
    'toy',
    'track',
    'trade',
    'traffic',
    'tragic',
    'train',
    'transfer',
    'trap',
    'trash',
    'travel',
    'tray',
    'treat',
    'tree',
    'trend',
    'trial',
    'tribe',
    'trick',
    'trigger',
    'trim',
    'trip',
    'trophy',
    'trouble',
    'truck',
    'true',
    'truly',
    'trumpet',
    'trust',
    'truth',
    'try',
    'tube',
    'tuition',
    'tumble',
    'tuna',
    'tunnel',
    'turkey',
    'turn',
    'turtle',
    'twelve',
    'twenty',
    'twice',
    'twin',
    'twist',
    'two',
    'type',
    'typical',
    'ugly',
    'umbrella',
    'unable',
    'unaware',
    'uncle',
    'uncover',
    'under',
    'undo',
    'unfair',
    'unfold',
    'unhappy',
    'uniform',
    'unique',
    'unit',
    'universe',
    'unknown',
    'unlock',
    'until',
    'unusual',
    'unveil',
    'update',
    'upgrade',
    'uphold',
    'upon',
    'upper',
    'upset',
    'urban',
    'urge',
    'usage',
    'use',
    'used',
    'useful',
    'useless',
    'usual',
    'utility',
    'vacant',
    'vacuum',
    'vague',
    'valid',
    'valley',
    'valve',
    'van',
    'vanish',
    'vapor',
    'various',
    'vast',
    'vault',
    'vehicle',
    'velvet',
    'vendor',
    'venture',
    'venue',
    'verb',
    'verify',
    'version',
    'very',
    'vessel',
    'veteran',
    'viable',
    'vibrant',
    'vicious',
    'victory',
    'video',
    'view',
    'village',
    'vintage',
    'violin',
    'virtual',
    'virus',
    'visa',
    'visit',
    'visual',
    'vital',
    'vivid',
    'vocal',
    'voice',
    'void',
    'volcano',
    'volume',
    'vote',
    'voyage',
    'wage',
    'wagon',
    'wait',
    'walk',
    'wall',
    'walnut',
    'want',
    'warfare',
    'warm',
    'warrior',
    'wash',
    'wasp',
    'waste',
    'water',
    'wave',
    'way',
    'wealth',
    'weapon',
    'wear',
    'weasel',
    'weather',
    'web',
    'wedding',
    'weekend',
    'weird',
    'welcome',
    'west',
    'wet',
    'whale',
    'what',
    'wheat',
    'wheel',
    'when',
    'where',
    'whip',
    'whisper',
    'wide',
    'width',
    'wife',
    'wild',
    'will',
    'win',
    'window',
    'wine',
    'wing',
    'wink',
    'winner',
    'winter',
    'wire',
    'wisdom',
    'wise',
    'wish',
    'witness',
    'wolf',
    'woman',
    'wonder',
    'wood',
    'wool',
    'word',
    'work',
    'world',
    'worry',
    'worth',
    'wrap',
    'wreck',
    'wrestle',
    'wrist',
    'write',
    'wrong',
    'yard',
    'year',
    'yellow',
    'you',
    'young',
    'youth',
    'zebra',
    'zero',
    'zone',
    'zoo',
})


# ═══════ 已知测试私钥（排除误报）═══════
TEST_PRIVATE_KEYS = frozenset({
    '0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80',
    '0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d',
    '0x5de4111afa1a4b94908f83103eb1f1706367c2e68ca870fc3fb9a804cdab365a',
    '0x7c852118294e51e653712a81e05800f419141751be58f605c371e15141b007a6',
    '0x47e179ec197488593b187f80a00eb0da91f1b9d0b13f8733639f19c30a34926a',
    '0x8b3a350cf5c34c9194ca85829a2df0ec3153be0318b5e2d3348e872092edffba',
    '0x92db14e403b83dfe3df233f83dfa3a0d709d0b5e3c64c7a3b1b4c9b0c9b6b8c7',
    '0x4bbbf85ce3377467afe5d46f804f221813b2bb87f24d81f60f1fcdbf7cbf4356',
    '0xdbda1821b80551c9d65939329250298aa3472ba22f39798e4b6d6c3b5c9a6b8a',
    '0x2a871d0798f97d79848a013d4936a73bf4cc922c825d33c1cf7073dff6d409c6',
    '0xf214f2b2cd398c806f84e317254e0f0b801d0643303237d97d22a6f0f0b4b0b2',
    '0x701b4093c6d9a1b3f7c8c9a6d7b5e3f2a1c4d8e9f0b2a3c4d5e6f7a8b9c0d1e2',
    '0x3e7f0a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f',
    '0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d',
    '0x6cbed15c793ce57650b9877cf6e156fefc4c3d2c2b7b7c7c8c8d8e8f9f9a0a0b0',
    '0x6370fd033278c143179d81c5526140625662b8daa446c22ee2d73db3707e620c',
    '0x646f1ce2fd0510f6c94f1a6a1f7c9c5aeb2f3c5d8e9a6b7c4d5e2f3a4b5c6d7e',
    '0xadd53f9a7e588d003326d1cbf9e4a43c061aadd9bc938c843f79d8d2f5a6e7b8',
    '0x395df67f0c2d2d9fe1ad9d0c5e3a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a',
    '0xe485d09874742f6e1003a0f1f0b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2',
})

# secp256k1 椭圆曲线阶 (n)
# 有效私钥必须满足 1 <= k < n
SECP256K1_N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

# ═══════ 私钥验证工具函数 ═══════

def is_valid_private_key(hex_key: str) -> bool:
    """验证 64 位 hex 是否为有效 secp256k1 私钥。"""
    try:
        h = hex_key.strip()
        if h.startswith('0x'):
            h = h[2:]
        if len(h) != 64:
            return False
        k = int(h, 16)
        return 1 <= k < SECP256K1_N
    except (ValueError, OverflowError):
        return False


def is_test_key(key: str) -> bool:
    """检查是否为已知测试/开发私钥。"""
    k = key.strip().lower()
    if k.startswith('0x'):
        return k in TEST_PRIVATE_KEYS
    return '0x' + k in TEST_PRIVATE_KEYS


def detect_mnemonic(text: str) -> Optional[Tuple[str, int, int]]:
    """Detect BIP39 mnemonic phrases in text.
    Supports: bare phrase, prefix assignments, comments, multi-line 24 words.
    Returns (phrase, word_count, line_number) or None.
    """
    MNEMONIC_PREFIXES = [
        'mnemonic', 'seed phrase', 'seed', 'phrase', 'recovery phrase',
        'recovery', 'secret phrase', 'secret', 'backup phrase', 'backup',
        'private key', 'wallet', 'export', 'bip39', 'bip 39',
        'twelve words', '12 words', '24 words', 'twenty-four',
        'memonic', 'memorized', 'passphrase',
    ]
    SKIP_LINES = [
        'test test test', 'junk', 'sample mnemonic', 'example mnemonic',
        'this is not a real seed', 'do not use', 'for testing only',
    ]

    lines = text.split('\n')
    for ln, line in enumerate(lines, 1):
        line_lower = line.strip().lower()
        # Skip obvious non-mnemonic lines
        if any(s in line_lower for s in SKIP_LINES):
            continue
        # Remove comment markers, quotes, etc.
        cleaned = line_lower
        # Try to find prefix markers
        best_start = 0
        for pfx in MNEMONIC_PREFIXES:
            for sep in [':', '=', ' ', '', '-', '_']:
                pattern = pfx + sep
                idx = cleaned.find(pattern)
                if idx != -1:
                    after = idx + len(pattern)
                    candidate = cleaned[after:].strip().strip('"\'')
                    words = candidate.split()
                    if len(words) in (12, 15, 18, 21, 24) and all(w in BIP39_WORDS for w in words):
                        return (candidate, len(words), ln)
        # Whole-line check (no prefix needed)
        raw_words = line_lower.strip().strip('"\'#').split()
        if len(raw_words) in (12, 15, 18, 21, 24):
            if all(w in BIP39_WORDS for w in raw_words):
                return (' '.join(raw_words), len(raw_words), ln)
        # Multi-line 24-word detection (words split across lines)
        if len(raw_words) >= 24:
            for chunk_start in range(len(raw_words) - 23):
                chunk = raw_words[chunk_start:chunk_start+24]
                if all(w in BIP39_WORDS for w in chunk):
                    return (' '.join(chunk), 24, ln)
        if len(raw_words) >= 12:
            for chunk_start in range(len(raw_words) - 11):
                chunk = raw_words[chunk_start:chunk_start+12]
                if all(w in BIP39_WORDS for w in chunk):
                    return (' '.join(chunk), 12, ln)
    return None

def detect_keystore(content: str, filename: str = '') -> Optional[Dict[str, Any]]:
    """检测以太坊 JSON Keystore 文件（加密钱包）。"""
    if not (filename.endswith('.json') or 'keystore' in filename.lower() or 'UTC--' in filename):
        return None
    try:
        data = json.loads(content)
        if isinstance(data, dict) and 'address' in data and 'crypto' in data:
            addr = data.get('address', '')
            crypto = data.get('crypto', {})
            ciphertext = crypto.get('ciphertext', '') if isinstance(crypto, dict) else ''
            kdf = crypto.get('kdf', '') if isinstance(crypto, dict) else ''
            version = data.get('version', '')
            cipher = crypto.get('cipher', '') if isinstance(crypto, dict) else ''
            return {
                'address': '0x' + addr if addr and not addr.startswith('0x') else addr,
                'ciphertext_prefix': ciphertext[:16] + '...' if len(ciphertext) > 16 else ciphertext,
                'kdf': kdf,
                'cipher': cipher,
                'version': version,
                'type': 'ethereum-keystore'
            }
    except (json.JSONDecodeError, TypeError):
        pass
    return None


# ═══════ 上下文关键词权重（用于判断 hex 是否为私钥而非哈希）═══════
PRIVATE_KEY_CONTEXT_KEYWORDS = {
    'private_key', 'privatekey', 'private key', 'secret_key', 'secretkey', 'secret key',
    'priv_key', 'privkey', 'pk=', 'pk =', 'secret=', 'secret =',
    'wallet_key', 'walletkey', 'key=', 'key =',
    '0x', 'hex', 'raw_key', 'rawkey',
}

TX_HASH_CONTEXT_KEYWORDS = {
    'txid', 'tx_hash', 'transaction', 'txhash', 'transaction_hash',
    'block_hash', 'txn_hash', 'hash', 'sha256', 'sha-256',
}

ADDRESS_CONTEXT_KEYWORDS = {
    'address', 'to:', 'from:', 'contract', 'wallet', 'account',
}
from urllib.parse import quote
from urllib.request import Request, build_opener
from urllib.error import HTTPError, URLError
from collections import defaultdict, Counter
from datetime import datetime

class _CompatResponse:
    def __init__(self, status_code, text='', headers=None):
        self.status_code = status_code
        self.text = text
        self.headers = headers or {}

    def json(self):
        return json.loads(self.text) if self.text else {}


class _CompatSession:
    def __init__(self):
        self.headers = {}
        self._opener = build_opener()

    def get(self, url, timeout=25):
        req = Request(url, headers=dict(self.headers), method='GET')
        try:
            with self._opener.open(req, timeout=timeout) as resp:
                data = resp.read()
                encoding = resp.headers.get_content_charset() or 'utf-8'
                text = data.decode(encoding, errors='replace')
                return _CompatResponse(resp.status, text, dict(resp.headers.items()))
        except HTTPError as e:
            data = e.read() if hasattr(e, 'read') else b''
            encoding = None
            try:
                encoding = e.headers.get_content_charset()
            except Exception:
                pass
            text = data.decode(encoding or 'utf-8', errors='replace') if data else ''
            return _CompatResponse(getattr(e, 'code', 0) or 0, text, dict(getattr(e, 'headers', {}).items()) if getattr(e, 'headers', None) else {})
        except URLError:
            return None
        except Exception:
            return None


if requests is None:
    class _RequestsCompat:
        Session = _CompatSession
    requests = _RequestsCompat()

import shutil

STARTUP_ANIMATION_SECONDS = 4.0
STARTUP_FRAME_DELAY = 0.12
STARTUP_FRAMES = [
    r"""s3hhhAXi;iriiiii;iAhMMMMMMMMMMhhh3s;ii;;;;;;;;;issriii
A5333h32XsXsiii;XhMMMhhMMMhMMMMMhMM2;;;;;iirssXA2Xrrii
A25555535AXXriiAMhMMhhMMMMhhMhMMMMMM2iiiirsA5555Ariiii
AAAAXsA2ArririsMhMMhhMhMMMMhMhhMMhMMMXiirXA5222Xsiiiii
rrrsrrrrrrrrri2hhMh3hhhMhMM3hh3MMhhMMhirsXA2AAXAsriiii
rrrrrrrrrrrrriAhMM3h3323h3H2353hhhhhMM5532XXAsrrriiiii
rrrrrrrrrrrrrr23Mh23h32s22hXA23553hhh3GGHM32Arrrrrrrii
rrrrrrrrrrrrrs52M5hHMA5MM2X2h3s33333M3HHHHhXrrrrrrrrsX
rrrrrrrrrrrrrs2Ah3h##MMB99HS9#3##Hh3MhMMH3Xrrrrrrrs3MH
rrrrrsssssAXsssrAhhhS99##G#9##9Gh3355MGHMAXXXAAAXsAhhM
srrsrrrrsA23h335Xs225M#9#HS###S3AXsX3SSGMMGGHHGHMh2553
sAX5hM5hHHGGHGSGM22sXAh#99#99S3sXsAMHGGGHHHHHGSSGGh225
5HGG#9####S####SSGS353X3HGSGGG33M3MMHHHHHMMHGGSSSSGGH3
HGSS#99#99#SSSSSGGSSHMh3H3hG9SH###GhhMHS#GHGSGHGGGSSSM
GSGGGSSSSSSSSSSSSSGGHHMG9#999#HGSS#GHGHGSSGGGGMMMHGGGG
HHHHHGHHGGGGHHHMMMG###HG#99####BB9GHMMMMMMMMMMMMMMMMMM
h33hhhhhhh333hhGShG&&&&B9##9B&&&&BM##Hh33333333333hhhh
333333555535553hhHhG##B9SH2MH#BShHhhhh5255355555555553
5555555555AAA22AAGHAAMGA;iX;;sMG5G5AAAAAAA533555555555
5533333335H9hA22AhG5AS3;hA#sh53HHhA222AAM9h3h3h333h333
AAAAAAAAAA9&&#3sA5G3h5M9h5@A2MhSGA22AX5#&&GXAAAAAA2222
rrrrrrrrrXBBB&92A2SHh3M9sH@5X3H9hA22AhB&BB#srrrrrrrrrr""",
    r"""s3hhhAXi;iiiiiii;iAhMMMMMMMMMMhhM3s;;i;;;;;;;;;issriii
A533hhh2XsXsiii;XhMMMhhMMMhMMMMMhMM2;;;;;iirsssA2Xrrii
A22555535AXXriiXMhMMhhMMMMhhMhMMMMMH2iiiirsA5555Ariiii
AAAAXsA2ArrrrisMhMMhhhhMMMMhMhhMMhMMMXiirsA5222Xsiiiii
rrrsrrrrrrrrriAhhMh33hhMhMM3hh3MMhhMMhiisXA2AAXAsriiii
irrirrrrrrrrriAhMM3h3323h3H2355hhhhhMM5532XXXsrrriiiii
rrrrrrrrrrrrrr23Mh23h32s22hXA23253hhh3HGHM32Arrrrrrrii
rrrrrrrrrrrrrs52M5hHMA2MM2X2h3s33333M3HHHHhXrrrrrrrrsX
rrrrrrrrrrrrrs2Ah3h##MM999HS9#3##Hh3MhMMH3Xrrrrrrrs5MH
rrrrrsssssAXsssrAhhhS99##G#9##9Gh3355MGHMAXXXAAXXsAhhM
srrsrrrrXA23h355XX222M#9#HS###S3AXsX3SSGMMGGHHGHMh2553
sXX5hM53HHGGHGSGM22sXAh#99#99S3sXsAhHGGGHHHHHGSSGGh225
5HGG#9####S####SSGS353X3HGSGGG53M3MHHHHHHMMHGGSSSSGGH3
HGSS##9#99#SSSSSGSSSHMh3H3hG9SH###GhMMHS#GHGSGHGGGSSSh
GGGGSSSSSSSSSSSSSGGGHHHG9##99#HGSS#GHGHGSSGGGGMMMHGGGG
HHHHHGHHGGGGHHHMMHG#9#HG9#MH###BB#GHMMMMMMMMMMMMMMMMMM
h3hhhhhhhhh333hG#B&@&&&BShhMGB&&&@@&#Hh333333333hhhhhh
333333555535555hMHGS#9&9GMGGS#&9GHHMhh5255555555555553
5555555553AAA22AAAAAAHHXHHMGGM3hXAAAAAA2AA535555555555
5533333335M9hAA222222XisHSMMSM22222222AAM9h3h3h33hh333
AAAAAAAAAX#&&#3s2222A5GGh3GG#9HA22A2AX5S&&HXAAAAAA2225
rrrrrrrrrs9&B&BAA2222AH9M35H99HA2222AMB&BB9srrrrrrrrrr""",
    r"""s3hh3AXi;iiiiiii;iAhMMMMMMMMMMMhh3s;;i;;;;;;;;;issriii
A5533h32XsXsiii;XhMMMhhMMMhMMMMMhMM2;;;;;iirXsXA2Xriii
A25555535AXXriiAMhMMhhMMMMhMMhMMMMhM2iiiirsA5555Ariiii
AAAAXXA2ArrrrisMhMMhhhMMMMMhMhhMMhMMMXiirX25222Xsiiiii
rrrsrrrrrrrrri2hhMh33hhMhMM3hh3MMhhMMhirsXA2AAXXsriiii
rrrrrrrrrrrrriAhMM3h3323h3H2353hhhhhMM5532XXAsrrriiiii
rrrrrrrrrrrrrr23Mh23h32s22hXA23253hhh3GGHM32Arrrrrrrii
rrrrrrrrrrrrrs52M5hHMA5MM2X2h3s33333M3HHHHhXrrrrrrrrsX
rrrrrrrrrrrrrs2Ah3h##MM999HS9#3##Hh3MhMMH3Xrrrrrrrs3MH
rrrrrsssssAXsssrAhhhS99##G#9##9Gh3325MGHMAXXXAAXXsAhhM
srrsrrrrXA23h355Xs225M#9#HS###S3AXsX3SSGMMGGHHGHMh2553
sXX5hM53HHGGHGSGM22sXAh#99#99S3sXsAMHGGGHHHHHGSSGGh225
5HGG#9####S####SSGG353X3HGSGGG53M3MMHHHHHMMHGGSSSSGGH3
HGSS#99#99#SSSSSGGSSHMh3H3hG9SH9##GhhMHS#GHGSGHGGGSSSM
GSGGSSSSSSSSSSSSSSGGHHMG9#999#HGS##GHGHGSSGGGGMMMHGGGG
HHHHHGHHGGGGHHHMMMH#9#HG#99####B&SMHMMMMMMMMMMMMMMMMMM
h3hhhhhhhh3333hG#MHB@&&B###9BB&BGGH&#Hh33333333333hhhh
333333555535553hMMGH##B9SM2MGSGHMGMMhh5255355555555553
5555555553AAA22AA3S3M3MX;iX;;sG5GG5XAAAAA2533555555555
5533333335H9hA2223G2GH;rhA#sMshGHHA222AAHBh3hh3333h333
AAAAAAAAXAB&&#5s2Ghh33MB32@sH9AMGG22AX3#&&HsAAAAAA2225
rrrrrrrriXBBB&#22#Ghh3H&rH@2AM2h#SAA2hB&BB#srrrrrrrrrr"""
]


def autoplay_startup_gif():
    try:
        if not STARTUP_FRAMES:
            return
        loops = max(1, int(STARTUP_ANIMATION_SECONDS / STARTUP_FRAME_DELAY / len(STARTUP_FRAMES)))
        _sys.stdout.write('\x1b[2J\x1b[H\x1b[?25l')
        _sys.stdout.flush()
        try:
            for _ in range(loops):
                for frame in STARTUP_FRAMES:
                    _sys.stdout.write('\x1b[H')
                    _sys.stdout.write(frame)
                    _sys.stdout.write('\n')
                    _sys.stdout.flush()
                    time.sleep(STARTUP_FRAME_DELAY)
        finally:
            _sys.stdout.write('\x1b[2J\x1b[H\x1b[?25h')
            _sys.stdout.flush()
    except Exception:
        pass

# ═══════ ANSI ═══════
class C:
    R='\033[91m';G='\033[92m';Y='\033[93m';B='\033[94m';M='\033[95m';C='\033[96m';W='\033[97m';D='\033[90m'
    BOLD='\033[1m';RESET='\033[0m'
def dim(s):return f'{C.D}{s}{C.RESET}'
def bold(s):return f'{C.BOLD}{s}{C.RESET}'
def red(s):return f'{C.R}{s}{C.RESET}'
def green(s):return f'{C.G}{s}{C.RESET}'
def cyan(s):return f'{C.C}{s}{C.RESET}'
def yellow(s):return f'{C.Y}{s}{C.RESET}'

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

# ═══════ 搜索词 ═══════
# 精准搜索策略：搜变量赋值 + 文件名 + 关键词组合
# 优先找：私钥赋值 -> 助记词 -> keystore -> 扩展密钥
SEARCH_DEEP = [
    # === 环境变量私钥赋值（最高命中率） ===
    'PRIVATE_KEY=0x path:.env',
    'PRIVATE_KEY= path:.env',
    'PRIVATE_KEY=0x path:.txt',
    '"PRIVATE_KEY" "0x" language:python',
    '"PRIVATE_KEY" "0x" language:javascript',
    '"PRIVATE_KEY" "0x" language:typescript',
    '"PRIVATE_KEY" "0x" language:go',
    '"PRIVATE_KEY" "0x" language:rust',
    '"PRIVATE_KEY" "0x" language:java',
    '"SECRET_KEY" "0x" path:.env',
    '"API_KEY" "0x" path:.env',
    '"WALLET" "PRIVATE" language:python',
    '"WALLET" "PRIVATE" language:javascript',
    # === 助记词/种子短语 ===
    '"mnemonic" "phrase" path:.env',
    '"mnemonic" "phrase" path:.txt',
    '"mnemonic" "phrase" path:.json',
    '"mnemonic" "phrase" path:.md',
    '"seed" "phrase" path:.env',
    '"seed" "phrase" path:.txt',
    '"seed" "phrase" path:.json',
    '"seed" "phrase" path:.md',
    '"recovery" "phrase" path:.txt',
    '"recovery" "phrase" path:.json',
    '"secret" "phrase" path:.txt',
    '"secret" "phrase" path:.env',
    '"backup" "phrase" path:.txt',
    '"backup" "phrase" path:.json',
    # === Keystore / 钱包文件 ===
    'filename:keystore "crypto" "ciphertext"',
    'filename:keystore "address" "crypto"',
    '"UTC--" "keystore"',
    '"UTC--" "address"',
    'filename:keystore language:json',
    'filename:wallet.dat',
    'filename:exported_account',
    '"wallet" "password" path:.txt',
    '"wallet" "backup" path:.txt',
    # === 扩展密钥 / HD 钱包 ===
    '"xprv" path:.txt',
    '"xprv" path:.json',
    '"xpub" path:.txt',
    '"xpub" path:.json',
    '"xpriv" path:.txt',
    # === 配置文件中的硬编码 ===
    'filename:config.json "private"',
    'filename:config.json "secret"',
    'filename:config.yaml "private_key"',
    'filename:config.py "private_key"',
    'filename:settings.py "private_key"',
    'filename:secrets.txt path:.env',
    'filename:accounts.json "private"',
    'filename:accounts.txt "private"',
]
SEARCH_FAST = SEARCH_DEEP[:15]

# ═══════ 密钥正则 — 精准匹配(含上下文验证) ═══════
# 分两步: 1) 正则提取 2) classify_key 精确归类 + 曲线验证
# 策略：优先匹配高价值目标（私钥 > 助记词 > keystore > 地址）
# ═══════ 加密货币密钥正则 ═══════
CRYPTO_REGEX = re.compile(
    # ETH 私钥 (0x + 64 hex chars)
    r'0x[a-fA-F0-9]{64}'
    # BTC WIF 私钥 (base58, 51-52 chars starting with 5/K/L)
    r'|5[KL][1-9A-HJ-NP-Za-km-z]{49,50}'
    # BIP39 助记词 (12/18/24 words)
    r'|(?:^|(?<=[\n\r\s]))(?:[a-z]+ ){11}[a-z]+(?:\n|\r|\s|$)'
    # SOL 私钥 JSON 数组
    r'|\[\s*\d+\s*(?:,\s*\d+\s*){63}\]'
    # Keystore 文件
    r'|\{"address":"[a-fA-F0-9]{40}","crypto":'
)

# ═══════ 高价值 AI 密钥正则 ═══════
HIGH_VALUE_REGEX = re.compile(
    r'sk-ant-[A-Za-z0-9_-]{40,}'                              # Anthropic Claude
    r'|sk-proj-\w{60,}'                                       # OpenAI Pro
    r'|sk-svcacct-\w{60,}'                                    # OpenAI Service
    r'|sk-admin-\w{40,}'                                       # OpenAI Admin
    r'|AIza[0-9A-Za-z_-]{35,}'                                 # Google Gemini
    r'|gemini-[0-9A-Za-z]{30,}'                                # Gemini API Key
    r'|nvapi-[0-9a-fA-F-]{30,}'                                # NVIDIA API
    r'|gsk_[A-Za-z0-9_-]{30,}'                                 # Groq
    r'|hf_[A-Za-z0-9]{30,}'                                    # HuggingFace
    r'|xai-[A-Za-z0-9]{30,}'                                   # xAI/Grok
    r'|pplx-[A-Za-z0-9]{30,}'                                  # Perplexity
)

# ═══════ 原始扫描正则 ═══════
KEY_REGEX = re.compile(
    # === 1. 私钥（最高价值） ===
    # 以太坊/通用 0x + 64 hex 私钥
    r'0x[a-fA-F0-9]{64}'
    # 比特币 WIF 私钥（5H/5J/5K/L/K开头）
    r'|[5KL][1-9A-HJ-NP-Za-km-z]{50,51}'
    # 扩展私钥 BIP32
    r'|xprv[1-9A-HJ-NP-Za-km-z]{103,108}'
    # Solana base58 私钥（87-88字符）
    r'|[1-9A-HJ-NP-Za-km-z]{87,88}'
    # === 2. 扩展公钥（可推导子地址） ===
    r'|xpub[1-9A-HJ-NP-Za-km-z]{103,108}'
    # === 3. 地址（辅助验证用） ===
    # 以太坊/BNB/ERC20（42位含0x）
    r'|0x[a-fA-F0-9]{40}'
    # 比特币 P2PKH
    r'|1[a-km-zA-HJ-NP-Z1-9]{25,34}'
    # 比特币 P2SH
    r'|3[a-km-zA-HJ-NP-Z1-9]{25,34}'
    # 比特币 Bech32
    r'|bc1[a-z0-9]{39,59}'
    # TRC20
    r'|T[a-zA-HJ-NP-Z0-9]{33}'
)

# ═══════ 加密货币检测 ═══════
def detect_crypto_keys(content):
    """检测文件中的加密货币私钥/地址"""
    results = []
    for m in CRYPTO_REGEX.finditer(content):
        key = m.group(0)
        if len(key) < 20:
            continue
        # 分类
        if key.startswith('0x') and len(key) == 66:
            cat = 'ETH_PRIVATE_KEY'
        elif key[0] in ('5', 'K', 'L') and len(key) in (51, 52):
            cat = 'BTC_WIF'
        elif key.startswith('[') and len(key) > 100:
            cat = 'SOL_PRIVATE_KEY'
        elif 'crypto' in key and 'address' in key:
            cat = 'ETH_KEYSTORE'
        elif len(key.split()) >= 12 and all(w.isalpha() for w in key.split()):
            cat = 'BIP39_MNEMONIC'
        else:
            cat = 'CRYPTO_OTHER'
        results.append({'key': key, 'cat': cat, 'line': content[:m.start()].count('\n') + 1})
    return results

def classify_key(key, context='', filename=''):
    """精确归类密钥 — 含 secp256k1 曲线验证 + 测试密钥过滤"""
    k = key.strip()
    ctx = (context + filename).lower()

    # === 私钥检测（最高优先级） ===

    # 1) 0x + 64 hex（以太坊式私钥）
    if re.match(r'^0x[a-fA-F0-9]{64}$', k):
        if is_test_key(k):
            return 'test_key', 'Hardhat/Test-PK', 'low'
        if is_valid_private_key(k):
            # 按上下文细分
            if 'sol' in ctx or 'solana' in ctx:
                return 'private_key', 'Solana-PK', 'critical'
            if 'btc' in ctx or 'bitcoin' in ctx:
                return 'private_key', 'Bitcoin-PK', 'critical'
            if 'trx' in ctx or 'tron' in ctx:
                return 'private_key', 'TRON-PK', 'critical'
            return 'private_key', 'ETH-EVM-PK', 'critical'
        else:
            return 'invalid_key', 'Invalid-PK', 'low'

    # 2) 比特币 WIF 私钥
    if re.match(r'^[5KL][1-9A-HJ-NP-Za-km-z]{50,51}$', k):
        return 'private_key', 'BTC-WIF', 'critical'

    # 3) BIP32 扩展私钥
    if k.startswith('xprv'):
        return 'private_key', 'BIP32-Extended', 'critical'

    # 4) Solana base58 私钥
    if re.match(r'^[1-9A-HJ-NP-Za-km-z]{87,88}$', k):
        return 'private_key', 'Solana-Base58', 'critical'

    # === 扩展公钥 ===
    if k.startswith('xpub'):
        return 'public_key', 'BIP32-Extended-Pub', 'high'

    # === 地址检测 ===
    if re.match(r'^0x[a-fA-F0-9]{40}$', k):
        # Ethereum 地址 - 通过上下文细分
        for kw, chain in [('bsc','BNB-Chain'),('bnb','BNB-Chain'),('polygon','Polygon'),
            ('matic','Polygon'),('avax','Avalanche-C'),('avalanche','Avalanche-C'),
            ('arbi','Arbitrum'),('arbitrum','Arbitrum'),('op','Optimism'),
            ('optimism','Optimism')]:
            if kw in ctx:
                return 'address', chain, 'low'
        return 'address', 'Ethereum', 'low'

    if re.match(r'^1[a-km-zA-HJ-NP-Z1-9]{25,34}$', k):
        return 'address', 'Bitcoin-P2PKH', 'low'
    if re.match(r'^3[a-km-zA-HJ-NP-Z1-9]{25,34}$', k):
        return 'address', 'Bitcoin-P2SH', 'low'
    if k.startswith('bc1'):
        return 'address', 'Bitcoin-Bech32', 'low'
    if re.match(r'^T[a-zA-HJ-NP-Z0-9]{33}$', k):
        return 'address', 'TRON-TRC20', 'low'

    return 'other', 'Unknown', 'low'

CAT_LABEL = {
    'private_key':'** 私钥 **',
    'public_key':'** 扩展公钥 **',
    'address':'地址',
    'mnemonic':'** 助记词 **',
    'keystore':'** 加密钱包 **',
    'test_key':'测试密钥(排除)',
    'invalid_key':'无效密钥(排除)',
    'other':'其他'
}
SEV_COLOR = {'critical':red,'high':yellow,'medium':cyan,'low':dim}

# ═══════ 高熵检测 ═══════
def shannon_entropy(s):
    if not s:return 0
    f=Counter(s);n=len(s)
    return -sum(c/n*math.log2(c/n) for c in f.values())

def detect_high_entropy(content, min_len=32, min_entropy=4.0):
    found=[]
    for m in re.finditer(r'''["'`]?([A-Za-z0-9+/=_-]{'''+str(min_len)+r''',})["'`]?''', content):
        c=m.group(1)
        if c.isdigit() or c.isalpha():continue
        if shannon_entropy(c)>=min_entropy:
            ln=content[:m.start()].count('\n')+1
            found.append((c,ln))
    return found

def mask_key(k):
    return k

def key_hash(k):
    return hashlib.sha256(k.encode()).hexdigest()[:16]

# ═══════ 扫描引擎 ═══════
class Scanner:
    def __init__(self,token=''):
        self.s=requests.Session()
        h={'Accept':'application/vnd.github.v3+json','User-Agent':'Crypto-Scanner/1.0'}
        if token:h['Authorization']=f'Bearer {token}'
        self.s.headers.update(h)
        self.rpm=30 if token else 10
        self.delay=60/self.rpm+1
        self.seen=set()

    def _get(self,url):
        while True:
            try:r=self.s.get(url,timeout=25)
            except:return None
            if r.status_code==403 and 'rate limit' in r.text.lower():
                wt=max(int(r.headers.get('X-RateLimit-Reset',0))-time.time(),60)+5
                sys.stdout.write(f'\r    {yellow(chr(0x231B))} 限速,等{int(wt)}s...');sys.stdout.flush()
                time.sleep(wt);continue
            return r

    def search(self,q):
        url=f'https://api.github.com/search/code?q={quote(q,safe=":")}&per_page=100&sort=indexed'
        r=self._get(url)
        if not r or r.status_code!=200:return[]
        return r.json().get('items',[])

    def download(self,repo,path):
        for br in('main','master'):
            try:
                r=self.s.get(f'https://raw.githubusercontent.com/{repo}/{br}/{path}',timeout=10)
                if r.status_code==200:return r.text
            except:continue
        return None

    def extract(self,content,filename=''):
        """从文件内容中提取所有类型的加密凭证"""
        keys=[]

        # 1) 正则提取私钥/地址
        for m in KEY_REGEX.finditer(content):
            key=m.group(0)
            ln=content[:m.start()].count('\n')+1
            sp=content.split('\n')
            ctx=sp[ln-1].strip()[:150] if 0<ln<=len(sp) else ''
            cat,prov,sev=classify_key(key,ctx,filename)
            if cat in ('test_key','invalid_key'):
                continue  # 跳过测试/无效密钥
            keys.append({'key':key,'cat':cat,'provider':prov,'severity':sev,'line':ln,'context':ctx})

        # 2) 助记词检测
        mn = detect_mnemonic(content)
        if mn:
            phrase, wc, ln = mn
            keys.append({
                'key': phrase, 'cat': 'mnemonic', 'provider': f'BIP39-{wc}words',
                'severity': 'critical', 'line': ln,
                'context': phrase[:80]
            })

        # 3) Keystore 文件检测
        ks = detect_keystore(content, filename)
        if ks:
            keys.append({
                'key': ks['address'], 'cat': 'keystore',
                'provider': f'{ks["kdf"]}/{ks["cipher"]}',
                'severity': 'critical', 'line': 1,
                'context': f'ethereum-keystore v{ks["version"]}'
            })

        return keys

    def run(self,queries,entropy=False):
        print(f'\n  {bold("Queries")}:{len(queries)} | {bold("RPM")}:{self.rpm} | '
              f'{bold("Entropy")}:{green("ON") if entropy else dim("OFF")}')
        print(f'  {dim(chr(0x2500)*60)}\n')
        all_keys=[];tf=0
        for qi,q in enumerate(queries):
            items=self.search(q);nf=0;qkeys=0
            print(f'  {cyan(chr(0x25B6))} [{qi+1:2d}/{len(queries)}] {bold(q[:62])}')
            for it in items:
                repo=it['repository']['full_name'];path=it['path']
                fid=f'{repo}/{path}'
                if fid in self.seen:continue
                self.seen.add(fid);nf+=1;tf+=1
                stars=it['repository'].get('stargazers_count',0)
                lang=it['repository'].get('language','?')
                print(f'     {dim(chr(0x2514))} {dim(repo)}/{dim(path)}  {yellow(chr(0x2B50)+str(stars)) if stars>10 else dim(chr(0x2B50)+str(stars))}  {dim(lang)}',end=' ')
                content=self.download(repo,path)
                if not content:
                    print(f'{red(chr(0x2717))}')
                    continue
                fkeys=0
                for ek in self.extract(content,path):
                    sev_sym=SEV_COLOR.get(ek['severity'],dim)('*')
                    all_keys.append({'repo':repo,'file':path,'line':ek['line'],'key':ek['key'],
                        'cat':ek['cat'],'provider':ek['provider'],'severity':ek['severity'],
                        'context':ek['context'],'stars':stars,'repo_url':it['repository']['html_url'],
                        'repo_lang':lang,'source':'regex'})
                    fkeys+=1;qkeys+=1
                if entropy:
                    for estr,ln in detect_high_entropy(content):
                        all_keys.append({'repo':repo,'file':path,'line':ln,'key':estr,
                            'cat':'other','provider':'HighEntropy','severity':'medium',
                            'context':'','stars':stars,'repo_url':it['repository']['html_url'],
                            'repo_lang':lang,'source':'entropy'})
                        fkeys+=1;qkeys+=1
                if fkeys:
                    print(f'{green(chr(0x2713))} {bold(str(fkeys))} keys')
                else:
                    print(f'{dim(chr(0x2713))}')
            print(f'  {dim(chr(0x2514))} {bold(f"files:{nf}")}  keys:{bold(str(qkeys))}  total_files:{tf}  total_keys:{bold(str(len(all_keys)))}')
            if qi<len(queries)-1:
                sys.stdout.write(f'  {dim(f"wait {self.delay:.0f}s...")}')
                sys.stdout.flush()
                time.sleep(self.delay)
                sys.stdout.write('\r'+' '*30+'\r')
                sys.stdout.flush()
        print()
        seen_u=set();dedup=[]
        for k in all_keys:
            uid=f'{k["repo"]}{k["file"]}{k["line"]}{key_hash(k["key"])}'
            if uid not in seen_u:seen_u.add(uid);dedup.append(k)
        return all_keys,dedup


# ═══════ Gist 搜索引擎 ═══════
class GistSearcher:
    """搜索 GitHub Gist 中泄露的私钥/助记词"""
    def __init__(self, token=''):
        self.s = requests.Session()
        h = {'Accept': 'application/vnd.github.v3+json', 'User-Agent': 'Crypto-Scanner/1.0'}
        if token:
            h['Authorization'] = f'Bearer {token}'
        self.s.headers.update(h)
        self.rpm = 30 if token else 10
        self.delay = 60 / self.rpm + 1
        self.seen = set()

    def search(self, q):
        url = f'https://api.github.com/gists/public?per_page=100'
        r = self._get(url)
        if not r or r.status_code != 200:
            return []
        items = r.json()
        results = []
        for gist in items:
            gist_id = str(gist.get('id', ''))
            if gist_id in self.seen:
                continue
            self.seen.add(gist_id)
            desc = (gist.get('description', '') or '').lower()
            files = gist.get('files', {})
            # 根据搜索词在描述或文件名中匹配
            q_lower = q.lower()
            if q_lower in desc:
                results.append(gist)
                continue
            for fname in files:
                if q_lower in fname.lower():
                    results.append(gist)
                    break
        return results

    def _get(self, url):
        while True:
            try:
                r = self.s.get(url, timeout=25)
            except Exception:
                return None
            if r.status_code == 403 and 'rate limit' in r.text.lower():
                wt = max(int(r.headers.get('X-RateLimit-Reset', 0)) - time.time(), 60) + 5
                sys.stdout.write(f'\r    {yellow(chr(0x231B))} Gist 限速,等{int(wt)}s...')
                sys.stdout.flush()
                time.sleep(wt)
                continue
            return r

    def download_gist(self, gist):
        """下载 Gist 中所有文件内容"""
        files = gist.get('files', {})
        contents = []
        for fname, finfo in files.items():
            raw_url = finfo.get('raw_url', '')
            if raw_url:
                try:
                    r = self.s.get(raw_url, timeout=10)
                    if r.status_code == 200:
                        contents.append((fname, r.text))
                except Exception:
                    pass
        return contents

    def scan_gists(self, queries, entropy=False):
        """扫描 Gist 中的密钥泄露"""
        all_keys = []
        print(f'\n  {bold("Gist Scan")} | {bold("Queries")}:{len(queries)}')
        print(f'  {dim(chr(0x2500) * 60)}\n')
        for qi, q in enumerate(queries[:10]):  # Gist API 只搜最近，限制查询量
            items = self.search(q)
            if not items:
                continue
            print(f'  {cyan(chr(0x25B6))} [{qi + 1:2d}/{min(len(queries),10)}] {bold(q[:62])}')
            for gist in items:
                gist_id = gist.get('id', '?')
                owner = gist.get('owner', {}).get('login', 'anonymous')
                desc = (gist.get('description', '') or '')[:40]
                print(f'     {dim(chr(0x2514))} {dim(owner)}/{dim(gist_id)}  {dim(desc)}', end=' ')
                file_contents = self.download_gist(gist)
                if not file_contents:
                    print(f'{red(chr(0x2717))}')
                    continue
                fkeys = 0
                for fname, fcontent in file_contents:
                    # 正则提取
                    for ek in _extract_keys(fcontent, fname):
                        ek.update({'repo': f'gist:{owner}/{gist_id}', 'file': fname,
                                   'stars': 0, 'repo_url': gist.get('html_url', ''),
                                   'repo_lang': 'gist', 'source': 'gist-regex'})
                        all_keys.append(ek)
                        fkeys += 1
                    # 助记词检测
                    mn = detect_mnemonic(fcontent)
                    if mn:
                        phrase, wc, ln = mn
                        all_keys.append({
                            'repo': f'gist:{owner}/{gist_id}', 'file': fname,
                            'line': ln, 'key': phrase,
                            'cat': 'mnemonic', 'provider': f'BIP39-{wc}words',
                            'severity': 'critical', 'context': phrase[:80],
                            'stars': 0, 'repo_url': gist.get('html_url', ''),
                            'repo_lang': 'gist', 'source': 'gist-mnemonic'
                        })
                        fkeys += 1
                    # Keystore 检测
                    ks = detect_keystore(fcontent, fname)
                    if ks:
                        all_keys.append({
                            'repo': f'gist:{owner}/{gist_id}', 'file': fname,
                            'line': 1, 'key': ks['address'],
                            'cat': 'keystore', 'provider': f'{ks["kdf"]}/{ks["cipher"]}',
                            'severity': 'critical', 'context': f'ethereum-keystore v{ks["version"]}',
                            'stars': 0, 'repo_url': gist.get('html_url', ''),
                            'repo_lang': 'gist', 'source': 'gist-keystore'
                        })
                        fkeys += 1
                    # 高熵检测
                    if entropy:
                        for estr, eln in detect_high_entropy(fcontent):
                            all_keys.append({
                                'repo': f'gist:{owner}/{gist_id}', 'file': fname,
                                'line': eln, 'key': estr,
                                'cat': 'other', 'provider': 'HighEntropy',
                                'severity': 'medium', 'context': '',
                                'stars': 0, 'repo_url': gist.get('html_url', ''),
                                'repo_lang': 'gist', 'source': 'gist-entropy'
                            })
                            fkeys += 1
                if fkeys:
                    print(f'{green(chr(0x2713))} {bold(str(fkeys))} keys')
                else:
                    print(f'{dim(chr(0x2713))}')
            if qi < min(len(queries), 10) - 1:
                sys.stdout.write(f'  {dim("wait 2s...")}')
                sys.stdout.flush()
                time.sleep(2)
                sys.stdout.write('\r' + ' ' * 20 + '\r')
                sys.stdout.flush()
        return all_keys


# ═══════ Pastebin 扫描引擎 ═══════
class PastebinScraper:
    """抓取 Pastebin 最新公开粘贴内容中的加密货币凭证"""
    def __init__(self):
        self.s = requests.Session()
        self.s.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        self.seen = set()

    def get_recent(self, limit=30):
        """获取 Pastebin 最新公开粘贴列表"""
        try:
            r = self.s.get('https://scrape.pastebin.com/api/scraping', timeout=15)
            if r.status_code != 200:
                return []
            # 返回的是 XML 格式的最新粘贴列表
            import xml.etree.ElementTree as ET
            root = ET.fromstring(r.text)
            items = []
            for item in root.findall('.//paste') or root.findall('paste'):
                paste_id = item.find('key').text if item.find('key') is not None else ''
                if paste_id and paste_id not in self.seen:
                    self.seen.add(paste_id)
                    items.append(paste_id)
                    if len(items) >= limit:
                        break
            return items
        except Exception:
            return []

    def get_raw(self, paste_id):
        """获取 Paste 原始内容"""
        try:
            r = self.s.get(f'https://scrape.pastebin.com/api/scraping/get/{paste_id}', timeout=15)
            if r.status_code == 200:
                return r.text
        except Exception:
            pass
        return None

    def scan_recent(self, limit=30):
        """扫描最新 Pastebin 粘贴"""
        all_keys = []
        paste_ids = self.get_recent(limit)
        if not paste_ids:
            print(f'  {yellow("Pastebin: no recent pastes or API unavailable")}')
            return all_keys
        print(f'\n  {bold("Pastebin Scan")} | {limit} recent pastes')
        print(f'  {dim(chr(0x2500) * 60)}\n')
        for pi, pid in enumerate(paste_ids):
            sys.stdout.write(f'  {cyan(chr(0x25B6))} [{pi + 1:2d}/{len(paste_ids)}] pastebin.com/{pid} ')
            sys.stdout.flush()
            content = self.get_raw(pid)
            if not content:
                print(f'{red(chr(0x2717))}')
                continue
            fkeys = 0
            # 正则提取
            for ek in _extract_keys(content, f'pastebin-{pid}'):
                ek.update({'repo': f'pastebin:{pid}', 'file': f'pastebin-{pid}.txt',
                           'stars': 0, 'repo_url': f'https://pastebin.com/{pid}',
                           'repo_lang': 'text', 'source': 'pastebin-regex'})
                all_keys.append(ek)
                fkeys += 1
            # 助记词
            mn = detect_mnemonic(content)
            if mn:
                phrase, wc, ln = mn
                all_keys.append({
                    'repo': f'pastebin:{pid}', 'file': f'pastebin-{pid}.txt',
                    'line': ln, 'key': phrase,
                    'cat': 'mnemonic', 'provider': f'BIP39-{wc}words',
                    'severity': 'critical', 'context': phrase[:80],
                    'stars': 0, 'repo_url': f'https://pastebin.com/{pid}',
                    'repo_lang': 'text', 'source': 'pastebin-mnemonic'
                })
                fkeys += 1
            if fkeys:
                print(f'{green(chr(0x2713))} {bold(str(fkeys))} keys')
            else:
                print(f'{dim("-")}')
        return all_keys


# ═══════ 通用密钥提取函数（给 Gist/Pastebin 复用）═══════
def _extract_keys(content, filename=''):
    """从文本中提取密钥（正则 + 分类 + 验证）"""
    keys = []
    for m in KEY_REGEX.finditer(content):
        key = m.group(0)
        ln = content[:m.start()].count('\n') + 1
        sp = content.split('\n')
        ctx = sp[ln - 1].strip()[:150] if 0 < ln <= len(sp) else ''
        cat, prov, sev = classify_key(key, ctx, filename)
        if cat in ('test_key', 'invalid_key'):
            continue  # 过滤测试/无效密钥
        keys.append({
            'key': key, 'cat': cat, 'provider': prov,
            'severity': sev, 'line': ln, 'context': ctx
        })
    return keys

# ═══════ 报告引擎 ═══════
class Report:
    def __init__(self,all_keys,dedup,out):
        self.all=all_keys;self.dedup=dedup;self.out=out
        os.makedirs(out,exist_ok=True)

    def stats(self):
        d=self.dedup;a=self.all
        cats=defaultdict(lambda:{'raw':0,'uniq':0,'repos':set(),'files':set(),'prov':Counter()})
        for k in a:cats[k['cat']]['raw']+=1
        for k in d:
            c=cats[k['cat']];c['uniq']+=1;c['repos'].add(k['repo'])
            c['files'].add(f"{k['repo']}/{k['file']}");c['prov'][k['provider']]+=1
        for c in cats.values():c['repos']=len(c['repos']);c['files']=len(c['files'])
        return cats

    def generate(self):
        ts=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cats=self.stats()
        tr=len(self.all);tu=len(self.dedup)
        trepos=len(set(k['repo'] for k in self.dedup))
        tfiles=len(set(f"{k['repo']}/{k['file']}" for k in self.dedup))

        # TXT
        L=[]
        def h(s):L.append(bold(s))
        def p(s):L.append(s)
        p(chr(0x2550)*66)
        p('  GitHub Crypto Leak Scan Report')
        p('  (私钥/助记词/Keystore/地址泄露扫描)')
        p(chr(0x2550)*66)
        p(f'  {ts}')
        p(f'  Raw:{bold(f"{tr:,}")}  Unique:{bold(f"{tu:,}")}  Repos:{bold(f"{trepos:,}")}  Files:{bold(f"{tfiles:,}")}')
        p('')
        for ck in('private_key','mnemonic','keystore','public_key','address','other'):
            c=cats[ck]
            if c['uniq']==0:continue
            label = CAT_LABEL.get(ck, ck)
            p(f'  {bold(label)}: {c["raw"]:,}/{c["uniq"]:,}  repos{c["repos"]:,}  files{c["files"]:,}')
            for prov,cnt in c['prov'].most_common():
                prov_display = prov[:28] + '..' if len(prov) > 28 else prov
                p(f'     {prov_display:<28s} {cnt:>6,}')
        p('')
        p(chr(0x2500)*66)
        p('  Top 30 (by Stars)')
        p(chr(0x2500)*66)
        for i,k in enumerate(sorted(self.dedup,key=lambda x:-x['stars'])[:30],1):
            sev_sym=SEV_COLOR.get(k.get('severity','medium'),dim)
            stars_str = dim(chr(0x2B50) + str(k['stars']))
            p(f'  [{i:2d}] {sev_sym("*")} {bold(k["repo"])}  {stars_str}')
            p(f'       {dim(k["file"])}:{k["line"]}  [{k["provider"]}]  {dim(k.get("source","?"))}')
            p(f'       {mask_key(k["key"])}')
            if k.get('context'):p(f'       {dim(k["context"][:100])}')
            p('')
        langs=Counter(k.get('repo_lang','?') for k in self.dedup)
        p(chr(0x2500)*66)
        p('  Languages')
        p(chr(0x2500)*66)
        for lang,cnt in langs.most_common(10):p(f'  {lang:<18s} {cnt:>6,}')
        report='\n'.join(L)
        with open(os.path.join(self.out,'scan_summary.txt'),'w',encoding='utf-8')as f:
            f.write(re.sub(r'\033\[\d+m','',report))

        # MD
        md=[]
        md.append('# GitHub Crypto Leak Scan Report\n')
        md.append(f'> {ts}\n')
        md.append('## Core Data\n')
        md.append('| Metric | Value |');md.append('|--------|-------|')
        md.append(f'| Raw | {tr:,} |');md.append(f'| Unique | {tu:,} |')
        md.append(f'| Repos | {trepos:,} |');md.append(f'| Files | {tfiles:,} |')
        md.append('')
        md.append('## By Category\n')
        md.append('| Category | Raw | Unique | Repos | Files |');md.append('|----------|-----|--------|-------|-------|')
        for ck in('private_key','mnemonic','keystore','address','other'):
            c=cats[ck]
            if c['uniq']==0:continue
            label = CAT_LABEL.get(ck, ck)
            md.append(f'| {label} | {c["raw"]:,} | {c["uniq"]:,} | {c["repos"]:,} | {c["files"]:,} |')
        md.append('')
        md.append('## By Provider\n')
        for ck in('private_key','mnemonic','keystore','address'):
            c=cats[ck]
            if c['uniq']==0:continue
            label = CAT_LABEL.get(ck, ck)
            md.append(f'### {label}\n')
            for prov,cnt in c['prov'].most_common():
                md.append(f'- {prov}: {cnt:,}')
        md.append('')
        md.append('## Top 20\n')
        for i,k in enumerate(sorted(self.dedup,key=lambda x:-x['stars'])[:20],1):
            md.append(f'{i}. **{k["repo"]}** {chr(0x2B50)}{k["stars"]:,}')
            md.append(f'   `{k["file"]}:{k["line"]}` [{k["provider"]}] `{mask_key(k["key"])}`')
            md.append('')
        with open(os.path.join(self.out,'report.md'),'w',encoding='utf-8')as f:
            f.write('\n'.join(md))

        # JSON
        json_out={
            'time':ts,'raw':tr,'unique':tu,'repos':trepos,'files':tfiles,
            'categories':{ck:{'label':CAT_LABEL.get(ck,ck),'raw':c['raw'],'unique':c['uniq'],
                'repos':c['repos'],'files':c['files'],
                'providers':dict(c['prov'].most_common())} for ck,c in cats.items() if c['uniq']>0},
            'top100':[{'repo':k['repo'],'file':k['file'],'line':k['line'],
                'provider':k['provider'],'severity':k['severity'],
                'key':k['key'],'key_masked':mask_key(k['key']),'key_hash':key_hash(k['key']),
                'stars':k['stars'],'language':k.get('repo_lang','?'),
                'source':k.get('source','?'),'context':k.get('context','')}
                for k in sorted(self.dedup,key=lambda x:-x['stars'])[:100]],
        }
        with open(os.path.join(self.out,'scan_result.json'),'w',encoding='utf-8')as f:
            json.dump(json_out,f,ensure_ascii=False,indent=2)

        return os.path.join(self.out,'scan_summary.txt'),os.path.join(self.out,'report.md'),os.path.join(self.out,'scan_result.json')


# ═══════ CLI ═══════
def main():
    autoplay_startup_gif()

    BANNER = [
        r'????????????????????????????????????????????????????????????????',
        r'?  r5hhhh2ssi;;iiiiiiiiii;r2hMMMMMMMMMMMMMhhhh5r;ii;;;;;    ?',
        r'?  A233hhhh3Arrrrsiiiiiii2hMMMMhhMMMMMMMMMhhhhMMA;;;;;;;    ?',
        r'?  A25555333552AXAsiiiir3MMhMMhhMMMMhhMMMMMMMMhhM5ii;;;     ?',
        r'?  A22255555352AXXriiirhMhMMhhhMMMMMMhhMMhMMMMMMhM2iiii     ?',
        r'?  ssssXsirsrrrrrrrrrsM3hMM3h3MhMMhMMM3hMh3MMMhhMMMhri      ?',
        r'?  irrrrrrrrrrrrrrrriXh3MMhhh5M2hhh3MM53h53hMMhhhMMMXr      ?',
        r'?  rrrrrrrrrrrrrrrrrrshhMH33h3hA52M5hH22hA33hhhhhhMM3h      ?',
        r'?  rrrrrrrrrrrrrrrrrrA33HM253h53AXA32MAX223555Mhh3M3MS      ?',
        r'?  rrrrrrrrrrrrrrrrrr3X3h33SSH3iH#9GhAhS9h;MHGM33hH3MM      ?',
        r'?  rrrrrrrrrrrsssAAssssrr2hM3hG#99#9#H9####9SMh33523MG      ?',
        r'?  srrsXXXXsXA553MhMHHHH2XAAAX2MS9###S##9#G5XsXsA5HSG       ?',
        r'?  s222hG##MHSSSSSSGSSSGH2MAsAAX3S999999#G2XX2sAMHHHG       ?',
        r'?  5HGGGS#9#SS##SS#####SSGGG5AMAs3MH##SHGG35Hh3MMMHHH       ?',
        r'?  MHGSSS999##99#SSSSS#SGSSSSHMhh3M353HS9GH#9S#GhhMMH       ?',
        r'?  GGSSSS##9####SSSSSSSSGGGGGGHHMh#SGS999SHSS###GMMHH       ?',
        r'?  GGGGGGGGGGGGGGSSSSSSSSSSGGHGHM#9999#999GHSSGGSGGGH       ?',
        r'?  HHHMHHHGGGGGGGGGHHHHMMMMS#99GMG#9999#SS9B&B9SHMhMM       ?',
        r'?  hhhhhhhhhhhhhhh333hhHG3H9&&B&&#SG#9SS9B&&&&&GH9Gh3       ?',
        r'?  GitHub Crypto Leak Scanner           v2                     ?',
        r'????????????????????????????????????????????????????????????????',
    ]
    for line in BANNER:
        print(dim(line))

    p = argparse.ArgumentParser(
        description='GitHub Crypto Leak Scanner v2 - 虚拟货币私钥/助记词/地址泄露扫描',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''[90m
  扫描源:
    github   - GitHub 公开仓库代码搜索（默认）
    gist     - GitHub Gist 搜索
    pastebin - Pastebin 最新公开粘贴
    all      - 全部源（最全面）

  示例:
    %(prog)s                                        # 交互模式
    %(prog)s --token ghp_xxx --deep                    # 深度扫描 GitHub
    %(prog)s --token ghp_xxx --sources all --deep      # 全源扫描
    %(prog)s --token ghp_xxx --sources gist,pastebin   # 只扫 Gist+Pastebin
[0m''')
    p.add_argument('--token', '-t', default='', help='GitHub PAT (optional but recommended)')
    p.add_argument('--deep', '-d', action='store_true', help='Deep scan (45 search terms)')
    p.add_argument('--entropy', '-e', action='store_true', help='High-entropy detection')
    p.add_argument('--output', '-o', default=None, help='Output dir')
    p.add_argument('--sources', '-s', default='github',
                    help='Scan sources: github, gist, pastebin, or comma-separated (default: github)')

    args = p.parse_args()

    token = args.token.strip() or os.environ.get('GITHUB_TOKEN', '')
    deep = args.deep
    entropy = args.entropy
    out_dir = args.output or OUTPUT_DIR
    sources = [s.strip().lower() for s in args.sources.split(',')]

    if not token and not deep and not entropy and not args.token and not os.environ.get('GITHUB_TOKEN') and args.sources == 'github':
        print(f'\n  {bold(">>> Interactive Mode <<<")}\n')
        choice = input('  Use GitHub Token? (y/n) [n]: ').strip().lower()
        if choice == 'y':
            token = input('  Paste your GitHub Token: ').strip()
            if not token:
                print(f'  {red("No token entered, running without token.")}')
        elif choice not in ('', 'n'):
            print(f'  {yellow("Invalid choice, running without token.")}')

        print(f'\n  {bold("Select scan mode:")}')
        print(f'    {cyan("[1]")} Fast         (12 queries, GitHub only, ~2 min)')
        print(f'    {cyan("[2]")} Deep         (45 queries, GitHub only, ~8 min)')
        print(f'    {cyan("[3]")} Full         (Deep + Gist + Pastebin)')
        mode = input('  Choice [2]: ').strip() or '2'
        if mode == '1':
            deep, entropy = False, False
            sources = ['github']
        elif mode == '2':
            deep, entropy = True, False
            sources = ['github']
        elif mode == '3':
            deep, entropy = True, False
            sources = ['all']
        else:
            deep, entropy = True, False

    if 'all' in sources:
        sources = ['github', 'gist', 'pastebin']

    queries = SEARCH_DEEP if deep else SEARCH_FAST

    print(f'\n  {bold("GitHub Crypto Leak Scanner v2")}')
    print(f'  {"Token" if token else "No-Token"} | {len(queries)} queries | '
          f'{",".join(sources)} | {"entropy" if entropy else "no-entropy"}')
    print(f'  {dim(f"Output: {out_dir}")}')

    all_keys = []

    # === GitHub 仓库扫描 ===
    if 'github' in sources:
        print(f'\n  {bold("=== Source: GitHub Repos ===")}')
        scanner = Scanner(token)
        repo_keys, dedup = scanner.run(queries, entropy=entropy)
        all_keys.extend(repo_keys)

    # === GitHub Gist 扫描 ===
    if 'gist' in sources:
        print(f'\n  {bold("=== Source: GitHub Gists ===")}')
        gist_scanner = GistSearcher(token)
        gist_keys = gist_scanner.scan_gists(queries, entropy=entropy)
        all_keys.extend(gist_keys)

    # === Pastebin 扫描 ===
    if 'pastebin' in sources:
        print(f'\n  {bold("=== Source: Pastebin ===")}')
        paste_scanner = PastebinScraper()
        paste_keys = paste_scanner.scan_recent(limit=30)
        all_keys.extend(paste_keys)

    # === 去重 ===
    seen_u = set()
    dedup = []
    for k in all_keys:
        uid = f'{k["repo"]}{k["file"]}{k["line"]}{key_hash(k["key"])}'
        if uid not in seen_u:
            seen_u.add(uid)
            dedup.append(k)

    if all_keys:
        r = Report(all_keys, dedup, out_dir)
        txt, md, js = r.generate()
        print(f'\n  {green(chr(0x2713))} TXT : {txt}')
        print(f'  {green(chr(0x2713))} MD  : {md}')
        print(f'  {green(chr(0x2713))} JSON: {js}')
    else:
        print(f'\n  {yellow(chr(0x26A0))} No keys found.')
        print('    1. Rate limited -> wait or use token')
        print('    2. Invalid token -> https://github.com/settings/tokens (classic)')
        print('    3. Try --sources all for broader coverage')

if __name__ == '__main__':
    main()

