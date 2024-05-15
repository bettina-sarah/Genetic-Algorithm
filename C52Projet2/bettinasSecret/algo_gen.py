import numpy as np
import random
import math

population = 1000
taux_croissance = 10
preference = 1  # pourcentage a 100 mtn

brown = random.randrange(int(population * 1 / 3), int(population * 0.5))
blue = random.randrange(int(brown * 1 / 3), int(brown * 0.5))
combo = population - (brown + blue)
print("-- brown:", brown, "-- blue:", blue, "-- combo:", combo, "-- somme:", brown + blue + combo)

# 1. blue + blue
# 2. combo + blue (vider blue)
# ATTENTION: PREFERENCE INFLUENCE rien a date !
restant_blue = blue % 2
if restant_blue:  # si impair, on assigne combo a au blue restant
    couples_blue_blue = (blue - 1) / 2
    combo -= restant_blue
else:
    couples_blue_blue = blue / 2
couples_combo_blue = restant_blue
print("*** 1. ***")
print("-- Couples blue-blue:", couples_blue_blue, "-- restant blue:", restant_blue)
print("*** 2. ***")
print("-- combo mtn:", combo, "-- couples combo_blue:", couples_combo_blue)

# 3. brown + combo
couples_brown_combo = min(brown, combo)
brown -= couples_brown_combo
combo -= couples_brown_combo
print("*** 3. ***")
print("-- Couples brown-combo:", couples_brown_combo, "-- brown restants:", brown, "-- combo restants:", combo)

# 3b AJOUTÉ ICI PAS DANS L'EXCEL, SI combo plus que brun ! - combo entre eux:

couples_combo_combo = combo / 2
combo -= couples_combo_combo * 2  # redondant
print("*** 3b. ***")
print("-- Couples combo-combo:", couples_brown_combo, "-- combos restants:", combo)

# 4. MAtch final: brown+brown
couples_brown_brown = brown / 2
brown -= couples_brown_brown * 2  # redondant mais possiblement necessaire?
print("*** 4. ***")
print("-- Couples brown-brown:", couples_brown_brown, "-- brown restants:", brown)

# 5. taux de croissance - random
croissance_blue_blue = random.randrange(int(taux_croissance * 1 / 3), int(taux_croissance * 0.5))
croissance_combo_blue = random.randrange(int((taux_croissance - croissance_blue_blue) * 1 / 3),
                                         int((taux_croissance - croissance_blue_blue) * 0.5))
croissance_brown_brown = random.randrange(int((taux_croissance - croissance_blue_blue - croissance_combo_blue) * 1 / 3),
                                          int((taux_croissance - croissance_blue_blue - croissance_combo_blue) * 0.5))
try:
    croissance_combo_combo = random.randrange(
        int((taux_croissance - croissance_blue_blue - croissance_combo_blue - croissance_brown_brown) * 1 / 3),
        int((taux_croissance - croissance_blue_blue - croissance_combo_blue - croissance_brown_brown) * 0.5))
except:
    croissance_combo_combo = 1

croissance_brown_combo = taux_croissance - (croissance_blue_blue + croissance_combo_blue +
                                                croissance_brown_brown + croissance_combo_combo)

print("*** 5. Taux croissance (couples) ***")
print("--blue-blue:", croissance_blue_blue, "--combo-blue:", croissance_combo_blue, "--brown-brown:",
      croissance_brown_brown,
      "--combo-combo:", croissance_combo_combo, "--brown-combo:", croissance_brown_combo)

# Tab probabilités
