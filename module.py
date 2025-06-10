import pandas as pd

data = pd.read_csv('./data/list Hero.csv')
df = pd.read_csv('./data/fix.csv')

index_to_lane = {
        0: 'Jungler',
        1: 'Mid Laner',
        2: 'Gold Laner',
        3: 'Exp Lane',
        4: 'Roam'
    }

def getHeroData(hero_name):
    heroData = data[data['Hero Name'].str.lower() == hero_name.lower()]
    if not heroData.empty:
        return heroData.iloc[0]
    else:
        return None

def matchingHeroLane(dataHero, idx):
    unmatchedLane = 0

    if isinstance(dataHero, dict):
        dataHero = pd.Series(dataHero)

    heroName = dataHero['Hero Name']

    if heroName is not None:
        # Ambil Recommended Lane dan Second Lane dari df
        hero_row = df[df['Hero Name'] == heroName]
        if not hero_row.empty:
            recLane = hero_row['Recommended Lane'].iloc[0]
            secLane = hero_row['Second Lane'].iloc[0]
            # Ambil lane yang sesuai dengan idx
            target_lane = index_to_lane.get(idx)
            
            # Periksa apakah lane sesuai
            if recLane != target_lane and (pd.isna(secLane) or secLane != target_lane):
                unmatchedLane = 1
        else:
            print(f"Hero {heroName} tidak ditemukan di df.")
            unmatchedLane = 1  # Anggap tidak cocok jika hero tidak ditemukan
    else:
        print("dataHero is empty")
        unmatchedLane = 1

    return unmatchedLane

def calculateTeamStrength(team):
    totalStrength = 0
    hero_data = {}
    
    for i, hero in enumerate(team):
        data = getHeroData(hero)
        
        unmatchedLane = matchingHeroLane(data, i)

        if data is not None:
            totalStrength += data['Strength Rating (%)']
            hero_data[hero] = data  
        else:
            print(f"Hero {hero} tidak ditemukan dalam dataset.")

    return totalStrength, hero_data, unmatchedLane

def calculateWinPercentage(team1, team2):
    team1Strength, team1_data, unmatchedLane1 = calculateTeamStrength(team1)
    team2Strength, team2_data, unmatchedLane2 = calculateTeamStrength(team2)
    
    totalStrength = team1Strength + team2Strength
    if totalStrength == 0:  # Hindari pembagian dengan nol
        return 50.0, 50.0, team1_data, team2_data

    team1Base = (team1Strength / totalStrength) * 100
    team2Base = (team2Strength / totalStrength) * 100
    
    # Terapkan penalti dari lane yang tidak cocok (anggap 5% per mismatch)
    penalty_per_unmatched = 25
    team1Penalty = unmatchedLane1 * penalty_per_unmatched
    team2Penalty = unmatchedLane2 * penalty_per_unmatched

    team1WinPercentage = max(team1Base - team1Penalty, 0)
    team2WinPercentage = max(team2Base - team2Penalty, 0)

    # Normalisasi ulang agar total tetap 100%
    total = team1WinPercentage + team2WinPercentage
    if total > 0:
        team1WinPercentage = (team1WinPercentage / total) * 100
        team2WinPercentage = (team2WinPercentage / total) * 100
    else:
        team1WinPercentage = 50.0
        team2WinPercentage = 50.0

    return team1WinPercentage, team2WinPercentage, team1_data, team2_data

def generateMatchData(team1, team2, team1_data, team2_data):
    """
    Fungsi ini menerima dua tim (team1 dan team2) yang berisi nama hero yang dipilih oleh pengguna.
    Fungsi ini akan mengembalikan dictionary yang berisi data hero yang diperlukan untuk analisis dan modeling.
    """
    # Data untuk tim 1 (Tim yang dipilih oleh pengguna)
    team1_data_processed = {}
    for i, hero in enumerate(team1):
        hero_data = team1_data.get(hero)
        if hero_data is not None and not hero_data.empty:  # Periksa jika hero_data tidak kosong
            # Jangan masukkan Hero Name atau Role ke dalam fitur
            team1_data_processed.update({
                f'team1_Hero_{i+1}_Win_Rate': hero_data['Win Rate (%)'],
                f'team1_Hero_{i+1}_Popularity': hero_data['Popularity (%)'],
                f'team1_Hero_{i+1}_Ban_Rate': hero_data['Ban Rate (%)'],
                f'team1_Hero_{i+1}_Scaling_Rating': hero_data['Scaling Rating'],
                f'team1_Hero_{i+1}_Cooldown_Rating': hero_data['Cooldown Rating'],
                f'team1_Hero_{i+1}_Item_Dependency_Rating': hero_data['Item Dependency Rating'],
                f'team1_Hero_{i+1}_Mobility_Rating': hero_data['Mobility Rating'],
                f'team1_Hero_{i+1}_Crowd_Control_Rating': hero_data['Crowd Control Rating'],
                f'team1_Hero_{i+1}_Base_Stats_Growth_Rating': hero_data['Base Stats Growth Rating'],
                f'team1_Hero_{i+1}_Ultimate_Impact_Rating_All_Game_Phases': hero_data['Ultimate Impact Rating_All Game Phases'],
                f'team1_Hero_{i+1}_Ultimate_Impact_Rating_Early_Game': hero_data['Ultimate Impact Rating_Early Game'],
                f'team1_Hero_{i+1}_Ultimate_Impact_Rating_Late_Game': hero_data['Ultimate Impact Rating_Late Game'],
                f'team1_Hero_{i+1}_Ultimate_Impact_Rating_Mid_Game': hero_data['Ultimate Impact Rating_Mid Game'],
                f'team1_Hero_{i+1}_Ultimate_Impact_Rating_Support': hero_data['Ultimate Impact Rating_Support'],
                f'team1_Hero_{i+1}_Strength_Rating': hero_data['Strength Rating (%)']
            })
    
    # Data untuk tim 2 (Tim musuh yang dipilih oleh pengguna)
    team2_data_processed = {}
    for i, hero in enumerate(team2):
        hero_data = team2_data.get(hero)
        if hero_data is not None and not hero_data.empty:  # Periksa jika hero_data tidak kosong
            # Jangan masukkan Hero Name atau Role ke dalam fitur
            team2_data_processed.update({
                f'team2_Hero_{i+1}_Win_Rate': hero_data['Win Rate (%)'],
                f'team2_Hero_{i+1}_Popularity': hero_data['Popularity (%)'],
                f'team2_Hero_{i+1}_Ban_Rate': hero_data['Ban Rate (%)'],
                f'team2_Hero_{i+1}_Scaling_Rating': hero_data['Scaling Rating'],
                f'team2_Hero_{i+1}_Cooldown_Rating': hero_data['Cooldown Rating'],
                f'team2_Hero_{i+1}_Item_Dependency_Rating': hero_data['Item Dependency Rating'],
                f'team2_Hero_{i+1}_Mobility_Rating': hero_data['Mobility Rating'],
                f'team2_Hero_{i+1}_Crowd_Control_Rating': hero_data['Crowd Control Rating'],
                f'team2_Hero_{i+1}_Base_Stats_Growth_Rating': hero_data['Base Stats Growth Rating'],
                f'team2_Hero_{i+1}_Ultimate_Impact_Rating_All_Game_Phases': hero_data['Ultimate Impact Rating_All Game Phases'],
                f'team2_Hero_{i+1}_Ultimate_Impact_Rating_Early_Game': hero_data['Ultimate Impact Rating_Early Game'],
                f'team2_Hero_{i+1}_Ultimate_Impact_Rating_Late_Game': hero_data['Ultimate Impact Rating_Late Game'],
                f'team2_Hero_{i+1}_Ultimate_Impact_Rating_Mid_Game': hero_data['Ultimate Impact Rating_Mid Game'],
                f'team2_Hero_{i+1}_Ultimate_Impact_Rating_Support': hero_data['Ultimate Impact Rating_Support'],
                f'team2_Hero_{i+1}_Strength_Rating': hero_data['Strength Rating (%)']
            })
    
    # Gabungkan data tim 1 dan tim 2 serta persentase kemenangan
    team_data = {**team1_data_processed, **team2_data_processed}
    team1WinPercentage, team2WinPercentage, _, _ = calculateWinPercentage(team1, team2)
    team_data['Persentase_Kemenangan_Tim_1'] = team1WinPercentage
    team_data['Persentase_Kemenangan_Tim_2'] = team2WinPercentage
    
    return team_data