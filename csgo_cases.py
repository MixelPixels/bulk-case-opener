import requests, bs4, sys, time, random

roll_odds = {
    "color-rare-item": 0.003,
    "color-covert": 0.008,
    "color-classified": 0.046,
    "color-restricted": 0.146,
    "color-milspec": 0.797
}

def roll_case(skins, n, weights):
    skins_chosen = random.choices(skins, weights=weights, k=n)
    return skins_chosen

def get_possible_skins(tags, case_rarity):
    rarity_distr = {
        "color-rare-item": 0,
        "color-covert": 0,
        "color-classified": 0,
        "color-restricted": 0,
        "color-milspec": 0
    }
    case_chance = {}
    for name in tags:
        rarity = name.find(class_="quality")["class"][1]
        rarity_distr[rarity] += 1
    for name in tags:
        rarity = name.find(class_="quality")["class"][1]
        name_tag = name.find("h3")
        skin_name = ''.join(name_tag.findAll(text=True))
        case_chance[skin_name] = round(roll_odds[rarity] / rarity_distr[rarity], 6)
        case_rarity[skin_name] = rarity.split('-')[1]
    return case_chance

def get_soup(url: str):
    res = requests.get(url)
    res.raise_for_status()
    return bs4.BeautifulSoup(res.text, 'html.parser')

def assign_float(skins):
    skin_floats = {}
    for skin in skins:
        if skin not in skin_floats:
            skin_floats[skin] = [random.random()]
        else:
            skin_floats[skin].append(random.random())
    return skin_floats

def float_str(float_val):
    if float_val >= 0.0 and float_val < 0.07:
        return "Factory New"
    elif float_val >= 0.07 and float_val < 0.15:
        return "Minimal Wear"
    elif float_val >= 0.15 and float_val < 0.38:
        return "Field-Tested"
    elif float_val >= 0.38 and float_val < 0.45:
        return "Well-Worn"
    else:
        return "Battle-Scarred"

def output_to_csv(skin_floats, case_rarity):
    f = open("case_results.csv", "w")
    f.write("Rarity, Skin, Float, Wear\n")
    for skin in skin_floats.keys():
        for float_val in skin_floats[skin]:
            f.write(f"{case_rarity[skin]}, {skin}, {float_val}, {float_str(float_val)}\n")
    f.close()

def open_cases(n: int, url: str):
    random.seed(int(time.time()))
    case_rarity = {}
    case_soup = get_soup(url)
    tags = case_soup.find_all(class_="col-lg-4 col-md-6 col-widen text-center")
    skins_weights = get_possible_skins(tags, case_rarity)
    skins_chosen = roll_case(list(skins_weights.keys()), n, list(skins_weights.values()))
    skin_floats = assign_float(skins_chosen)
    output_to_csv(skin_floats, case_rarity)

if len(sys.argv) < 3:
    print("Usage: csgo_cases.py n url")
    print("Where: n is the number of cases you would like to open and url is the csgo stash url of the case")
else:
    open_cases(int(sys.argv[1]), sys.argv[2])