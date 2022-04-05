import math

image_indices = {
    'Scourge Explosion': 4,
    'Infested Terran Explosion': 10,
    'Needle Spines': 35,
    'Zerg Air Death Explosion (Large)': 58,
    'Zerg Air Death Explosion (Small)': 59,
    'Explosion1 (Small)': 213,
    'Explosion1 (Medium)': 214,
    'Explosion2 (Small)': 332,
    'Explosion2 (Medium)': 333,
    'Stasis Field Hit': 364,
    'Defensive Matrix Hit (Small)': 377,
    'Defensive Matrix Hit (Medium)': 378,
    'Defensive Matrix Hit (Large)': 379,
    'Ensnare Cloud': 383,
    'Plague Cloud': 387,
    'Recall Field': 391,
    'FlameThrower': 421,
    'Burrowing Dust': 423,
    'Phase Disruptor Hit': 427,
    'Nuclear Missile Death': 428,
    'Spider Mine Death': 429,
    'Vespene Geyser Smoke1': 430,
    'Vespene Geyser Smoke2': 431,
    'Vespene Geyser Smoke3': 432,
    'Vespene Geyser Smoke4': 433,
    'Vespene Geyser Smoke5': 434,
    'Grenade Shot Smoke': 441,
    'Scarab/Anti-Matter Missile Overlay': 443,
    'Scarab Hit': 444,
    'Burst Lasers Hit': 447,
    'Building Landing Dust Type1': 494,
    'Building Landing Dust Type2': 495,
    'Building Landing Dust Type3': 496,
    'Building Landing Dust Type4': 497,
    'Building Landing Dust Type5': 498,
    'Sunken Colony Tentacle': 506,
    'Acid Spore': 509,
    'Acid Spore Hit': 510,
    'Glave Wurm Hit [!]': 512,
    'Consume': 517,
    'Guardian Attack Overlay': 518,
    'Dual Photon Blasters Hit': 519,
    'Phase Disruptor': 523,
    'STA/STS Photon Cannon Overlay': 524,
    'Psionic Storm': 525,
    'Arclite Shock Cannon Hit': 533,
    'Siege Tank(Siege) Turret Attack': 537,
    'Yamato Gun Hit': 544,
    'Hallucination Hit': 546,
    'Psionic Shockwave Hit': 548,
    'Archon Beam': 549,
    'EMP Shockwave Hit (Part1)': 555,
    'EMP Shockwave Hit (Part2)': 556,
    'Hallucination Death1': 557,
    'Dark Archon Death': 928,
    'Halo Rockets Trail': 960,
    'Subterranean Spines': 961,
    'Corrosive Acid Hit': 963,
    'Neutron Flare': 964,
    'Mind Control Hit (Small)': 973,
    'Mind Control Hit (Medium)': 974,
    'Mind Control Hit (Large)': 975,
    'Optical Flare Hit (Small)': 976,
    'Optical Flare Hit (Medium)': 977,
    'Optical Flare Hit (Large)': 978,
    'Feedback (Small)': 979,
    'Feedback (Medium)': 980,
    'Feedback Hit (Large)': 981,
    'Maelstrom Hit': 998,
}

def deaths(player, unit, relation, number):
    return 'Deaths(\"' + player + '\", \"' + unit + '\", ' + relation + ', ' + str(number) + ');'


def create_unit(player, unit, number, location):
    return 'Create Unit(\"' + player + '\", \"' + unit + '\", ' + str(number) + ', \"' + location + '\");'
    
def kill_unit(player, unit):
    return 'Kill Unit(\"' + player + '\", \"' + unit + '\");'
    
def kill_unit_at_location(player, unit, number, location):
    return 'Kill Unit At Location(\"' + player + '\", \"' + unit + '\", ' + str(number) + ', \"' + location + '\");'
    
def remove_unit(player, unit):
    return 'Remove Unit(\"' + player + '\", \"' + unit + '\");'
    
def remove_unit_at_location(player, unit, number, location):
    return 'Remove Unit At Location(\"' + player + '\", \"' + unit + '\", ' + str(number) + ', \"' + location + '\");'
    
def set_deaths(player, unit, operation, number):
    return 'Set Deaths(\"' + player + '\", \"' + unit + '\", ' + operation + ', ' + str(number) + ');'
    
def wait(ms):
    return 'Wait(' + str(ms) + ');'

def masked_memoryAddr(index):
    return 'Masked MemoryAddr(0x00666458, Set To, ' + str(index) + ', 0x0000ffff);'

def add_comment(ob_num, count_num, part_num, multipart, options):
    comment = 'Comment(\"'
    
    if options[0]:
        comment += 'Ob '
    comment += str(ob_num)
    if options[0]:
        comment += ' '
    else:
        comment += '-'
        
    if options[1]:
        comment += 'Count '
    comment += str(count_num)
    
    if multipart:
        if options[1]:
            comment += ' '
        else:
            comment += '-'
            
        if options[2]:
            comment += 'Part '
        comment += str(part_num)
    
    comment += '\");\n'
    
    return comment
#explosion = [loc, name, player]
def count_triggers(ob_num=1, count_num=1, last_count=False, trig_owner='', force='', death_counters = [], death_type='', comment_options=[], timing_type='', unit_explosions=[], sprite_explosions = [], wall_actions=[], delay=1):
    triggers = []
    conditions = []
    actions = []
    
    conditions.append(deaths(death_counters[3], death_counters[0], 'Exactly', ob_num))
    conditions.append(deaths(death_counters[3], death_counters[1], 'Exactly', count_num))
    conditions.append(deaths(death_counters[3], death_counters[2], 'Exactly', 0))
 
    sprites_used = False
    explosions_by_sprite = {}
    explosions_by_unit = {}
    units_used = {}
    locations = []
    
    for wall in wall_actions:
        if wall[3] == 'c':
            actions.append(create_unit(wall[2], wall[0], 1, wall[1]))
        if wall[3] == 'r':
            actions.append(remove_unit_at_location('All Players', wall[0], 'All', wall[1]))

    for explosion in sprite_explosions:
        name = explosion[1]
        explosions_by_sprite[name] = explosions_by_sprite.get(name, []) + [explosion]
        locations.append(explosion[0])
    for explosion in unit_explosions:
        name = explosion[1]
        explosions_by_unit[name] = explosions_by_unit.get(name, []) + [explosion]
        locations.append(explosion[0])
        units_used[name] = units_used.get(name, []) + [explosion[2]]

    for name in explosions_by_sprite.keys():
        actions.append(masked_memoryAddr(image_indices[name]))
        for explosion in explosions_by_sprite[name]:
            actions.append(create_unit(explosion[2], 'Scanner Sweep', 1, explosion[0]))
    if len(sprite_explosions) > 0:
        actions.append(remove_unit('All Players', 'Scanner Sweep'))
        
    for name in explosions_by_unit.keys():
        for explosion in explosions_by_unit[name]:
            actions.append(create_unit(explosion[2], explosion[1], 1, explosion[0]))
            
    if death_type == 'remove':
        for unit in units_used:
            for player in set(units_used[unit]):
                actions.append(kill_unit(player, unit))
        
    for loc in set(locations):
        if death_type == 'kill':
            actions.append(kill_unit_at_location('All players', 'Men', 'All', loc))
        if death_type == 'remove':
            actions.append(remove_unit_at_location('All players', 'Zerg Zergling', 'All', loc))
    
    if last_count:
        operation = 'Set To'
    else:
        operation = 'Add'
    actions.append(set_deaths(death_counters[3], death_counters[1], operation, 1))
    if timing_type == 'frames':
        actions.append(set_deaths(death_counters[3], death_counters[2], 'Set To', delay))
    if timing_type == 'waits':
        actions.append(wait(42*(delay - 1)))

    trigger_start = 'Trigger(\"' + trig_owner + '\"){\n\n' + 'Conditions:\n'
    for condition in conditions:
        trigger_start += condition + '\n'
    trigger_start += '\n' + 'Actions:\n'
    
    num_actions = len(actions)
    num_parts = math.ceil(num_actions/62)
    triggers = []
    i = 0
    while i < num_parts:
        trigger = trigger_start
        if num_parts - i == 1:
            end_index = num_actions
        else:
            end_index = 62*(i + 1)
        for j in range(62*i, end_index):
            trigger += actions[j] + '\n'
        trigger += 'Preserve Trigger();' + '\n'
        trigger += add_comment(ob_num, count_num, i+1, num_parts > 1, comment_options)
        trigger += '}\n\n' + '//-----------------------------------------------------------------//\n'
        triggers.append(trigger)
        i += 1
        
    return triggers