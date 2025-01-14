FIND_GENRES = """
Categorize a list of anime/manga titles into genres. The output should be a python dictionary.

Instructions:
1. Use these genres:
   - Action, Adventure, Avant Garde, Award Winning, Boys Love, Comedy, Drama, Fantasy, Girls Love, 
   Gourmet, Horror, Mystery, Romance, Sci-Fi, Slice of Life, Sports, Supernatural, Suspense, Ecchi, 
   Erotica, Hentai.

2. Each title may belong to multiple genres. Assign all applicable genres.

3. For each genre:
   - Provide the genre name.
   - Count how many titles fit the genre.
   - List three example titles.

4. Sort genres from most to least common.

5. Make sure the output is always in the dictionary format of the exampele output

Input:
[List of titles]

Output:
{
    "Action": {
        "count": 23,
        "examples": ["Shingeki no Kyojin", "Kimetsu no Yaiba", "Cowboy Bebop"]
    },
    "Adventure": {
        "count": 17,
        "examples": ["Hunter x Hunter (2011)", "Tengen Toppa Gurren Lagann", "Vinland Saga"]
    },
    ...
}
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
