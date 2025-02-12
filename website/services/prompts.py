FIND_GENRES = """
You will be given a list of anime titles. Find the top 10 genres and put them into a JSON

Instructions:
1. Be very creative with the genres and try and uncover what the user is most interested in.

3. Sort genres from most to least common.

4. Return genres in this exact JSON format:
{
    "Philosophical Sci-Fi": {
        "examples": ["Ghost in the Shell: Stand Alone Complex", "Ergo Proxy", "Akira"]
    },
    "Time Manipulation & Alternate Realities": {
        "examples": ["Steins;Gate", "Re:Zero – Starting Life in Another World", "Tatami Galaxy"]
    },
    ...
"""

FIND_THEMES = """
Analyze a list of anime/manga titles and categorize each title by its central themes. Return the result as a Python dictionary.

Instructions:
1. Identify meaningful and creative themes for each title based on its core story, setting, and character elements. Themes may include concepts like friendship, revenge, redemption, identity, time travel, survival, war, family bonds, morality, or any other relevant ideas.

2. Each title may be associated with multiple themes. Assign all applicable themes.

3. For each theme:
   - Provide the theme name.
   - Count how many titles fit the theme.
   - List three example titles that exemplify this theme.

4. Sort themes from most to least common.

Input:
[List of titles]

Output:
{
    "Power of Dreams": {
        "count": 18,
        "examples": ["One Piece", "Naruto", "Bakuman"]
    },
    "Existential Despair": {
        "count": 5,
        "examples": ["Neon Genesis Evangelion", "Texhnolyze", "Serial Experiments Lain"]
    },
    "Battle of Ideals": {
        "count": 9,
        "examples": ["Death Note", "Code Geass", "Psycho-Pass"]
    },
    ...
}
"""
