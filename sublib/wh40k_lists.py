subfaction_types = ["Order Convictions", "Forge World Choice", "Brotherhood", "Noble Household", "Chapter",
                    "Chaos Allegiance", "Dread Household", "Legion", "Plague Company",
                    "Cult of the Legion", "Craftworld Selection", "Kabal", "Wych Cult",
                    "Haemonculus Coven", "Cult Creed", "League", "Dynasty Choice", "Clan Kultur", "Sept Choice", "Hive Fleet"]

selection_non_unit_types = ["**Chapter Selector**", "Game Type", "Detachment Command Cost", "Battle Size", "Arks of Omen Compulsory Type"]

phases_list = ["Any time", "Before battle", "During deployment", "At the start of battle round", "Any phase", "Any of your phases", "At the start of your turn",
               "At the start of enemy turn", "Command phase", "Enemy Command phase", "Movement phase", "Enemy Movement phase", "Psychic phase",
               "Enemy Psychic phase", "Shooting phase", "Enemy Shooting phase", "Being targeted", "Charge phase", "Enemy Charge phase", "Fight phase",
               "Enemy Fight phase", "Morale phase", "Enemy Morale phase", "Taking casualties", "Enemy taking casualties", "End of your turn", "End of enemy turn"]

ignore_phases_list = []

valid_stratagems_type = ["Battle Tactic Stratagem", "Strategic Ploy Stratagem", "Epic Deed Stratagem", "Requisition Stratagem", "Wargear Stratagem", "Core Stratagem"]
invalid_stratagems_type = ["(Supplement)", "Crusher Stampede", "Crusade", "Fallen Angels"]

unit_rename_dict = {"War Dog Brigand Squadron": "War Dog Brigand",
                    "War Dog Executioner Squadron": "War Dog Executioner",
                    "War Dog Huntsman Squadron": "War Dog Huntsman",
                    "War Dog Karnivore Squadron": "War Dog Karnivore",
                    "War Dog Stalker Squadron": "War Dog Stalker",
                    "Armiger Helverins": "Armiger Helverin",
                    "Armiger Warglaives": "Armiger Warglaive",
                    "Knight Moiraxes": "Knight Moirax",
                    "Kâhl": "Khl",
                    "KÃ¢hl": "Khl",
                    "Brôkhyr Thunderkyn w/ bolt cannons": "Brkhyr Thunderkyn",
                    "Brôkhyr Thunderkyn w/ graviton blast cannons": "Brkhyr Thunderkyn",
                    "Brôkhyr Thunderkyn  w/ SP conversion beamers": "Brkhyr Thunderkyn",
                    "BrÃ´khyr Thunderkyn w/ bolt cannons": "Brkhyr Thunderkyn",
                    "BrÃ´khyr Thunderkyn w/ graviton blast cannons": "Brkhyr Thunderkyn",
                    "BrÃ´khyr Thunderkyn  w/ SP conversion beamers": "Brkhyr Thunderkyn",
                    "Hearthguard w/ disintegrators and plasma blade gauntlets": "Einhyr Hearthguard",
                    "Hearthguard w/ disintegrators and concussion gauntlets": "Einhyr Hearthguard",
                    "Hearthguard w/ plasma guns and concussion gauntlets": "Einhyr Hearthguard",
                    "Hearthguard w/ plasma guns and plasma blade gauntlets": "Einhyr Hearthguard",
                    "Cthonian Beserks w/ heavy plasma axes": "Cthonian Beserks",
                    "Cthonian Beserks w/ concussion mauls": "Cthonian Beserks",
                    "Hearthkyn Warriors w/ ion blasters": "Hearthkyn Warriors",
                    "Hearthkyn Warriors w/ bolters": "Hearthkyn Warriors",
                    "Ûthar the Destined": "thar the Destined",
                    "Ã›thar the Destined": "thar the Destined",
                    "Brôkhyr Iron-master": "Brkhyr Iron-master",
                    "BrÃ´khyr Iron-master": "Brkhyr Iron-master"
                    }

subfaction_rename_dict = {"Order: Our Martyred Lady": "Order of Our Martyred Lady",
                          "Order: Argent Shroud": "Order of the Argent Shroud",
                          "Order: Bloody Rose": "Order of the Bloody Rose",
                          "Order: Ebon Chalice": "Order of the Ebon Chalice",
                          "Order: Sacred Rose": "Order of the Sacred Rose",
                          "Order: Valorous Heart": "Order of the Valorous Heart",
                          "Death Korps of Krieg": "Astra Militarum"
                          }

army_of_renown_list = ["Kill Team Strike Force", "Vanguard Spearhead", "Mechanicus Defence Cohort", "Skitarii Veteran Cohort", "Freeblade Lance", "Disciples of Belakor",
                       "Terminus Est Assault Force", "Warpmeld Pact", "Coteries of the Haemonculi", "Cult of the Cryptek", "Annihilation Legion", "Speed Freeks Speed Mob",
                       "Cogs of Vashtorr"]

current_army_of_renown = ""

def clean_list():
    global ignore_phases_list, current_army_of_renown
    ignore_phases_list = []
    current_army_of_renown = ""
