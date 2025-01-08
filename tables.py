import pandas as pd
import utils as u


def color_rows(row):
    has_xpa = row["HasXPA"]
    pc = row["PC"]
    xbox_one = row["XboxOne"]
    xbox_series_x = row["XboxSeriesX"]

    if has_xpa and pc and (xbox_one or xbox_series_x):
        color = "background-color: green"
    elif has_xpa and pc and not (xbox_one or xbox_series_x):
        color = "background-color: red"
    elif has_xpa and not pc and (xbox_one or xbox_series_x):
        color = "background-color: red"
    elif not has_xpa and pc and (xbox_one or xbox_series_x):
        color = "background-color: orange"
    else:
        color = "background-color: grey"

    # Return a Series of styles for the entire row
    return [color] * len(row)


def make_tables(yaml_file="data.yaml", updated_games=None):
    games = u.load_yaml(yaml_file)
    platforms_dict = {}
    for game in games:
        for game_name, game_info in game.items():
            if updated_games is not None:
                if game_name in updated_games:
                    platforms = game_info.get("availableOn", [])
                    has_xpa = "XPA" in game_info.get("capabilities", {})
                    platforms_dict[game_name] = {
                        "platforms": platforms,
                        "has_xpa": has_xpa,
                    }
            else:
                platforms = game_info.get("availableOn", [])
                has_xpa = "XPA" in game_info.get("capabilities", {})
                platforms_dict[game_name] = {"platforms": platforms, "has_xpa": has_xpa}

    # Define column names and data types
    columns = {
        "Game": "str",
        "XboxOne": "bool",
        "XboxSeriesX": "bool",
        "PC": "bool",
        "XCloud": "bool",
        "HasXPA": "bool",
    }

    # Create an empty DataFrame with specified column names and types
    df = pd.DataFrame({col: pd.Series(dtype=dt) for col, dt in columns.items()})

    for game, data in platforms_dict.items():
        a = list()
        a.append(game)
        a.append("XboxOne" in data["platforms"])
        a.append("XboxSeriesX" in data["platforms"])
        a.append("PC" in data["platforms"])
        a.append("XCloud" in data["platforms"])
        a.append(data["has_xpa"])
        df.loc[len(df)] = a

    # Apply the color coding to the DataFrame
    styled_df = df.style.apply(color_rows, axis=1)
    return styled_df
