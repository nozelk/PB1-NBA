-- =============================================
-- NBA Analytics Database Schema
-- 10 tables, fully normalized
-- =============================================

-- TEAMS
CREATE TABLE IF NOT EXISTS teams (
    id INTEGER PRIMARY KEY,
    full_name TEXT NOT NULL UNIQUE,
    abbreviation TEXT,
    nickname TEXT,
    city TEXT,
    state TEXT,
    conference TEXT,
    division TEXT,
    year_founded INTEGER,
    arena TEXT,
    owner TEXT,
    gm TEXT,
    logo_path TEXT
);

-- PLAYERS
CREATE TABLE IF NOT EXISTS players (
    id INTEGER PRIMARY KEY,
    first_name TEXT,
    last_name TEXT,
    display_name TEXT NOT NULL,
    position TEXT,
    height TEXT,
    weight INTEGER,
    country TEXT,
    school TEXT,
    birthdate TEXT,
    draft_year INTEGER,
    draft_round INTEGER,
    draft_number INTEGER,
    from_year INTEGER,
    to_year INTEGER,
    image_path TEXT
);

-- COACHES
CREATE TABLE IF NOT EXISTS coaches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    image_path TEXT
);

-- PLAYER SEASON STATS
CREATE TABLE IF NOT EXISTS player_season_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_id INTEGER NOT NULL,
    team_id INTEGER NOT NULL,
    season_year INTEGER NOT NULL,
    age INTEGER,
    gp INTEGER,
    gs INTEGER,
    min REAL,
    fgm REAL,
    fga REAL,
    fg_pct REAL,
    fg3m REAL,
    fg3a REAL,
    fg3_pct REAL,
    ftm REAL,
    fta REAL,
    ft_pct REAL,
    oreb REAL,
    dreb REAL,
    reb REAL,
    ast REAL,
    stl REAL,
    blk REAL,
    tov REAL,
    pf REAL,
    pts REAL,
    plus_minus REAL,
    off_rating REAL,
    def_rating REAL,
    net_rating REAL,
    pace REAL,
    pie REAL,
    FOREIGN KEY (player_id) REFERENCES players(id),
    FOREIGN KEY (team_id) REFERENCES teams(id),
    UNIQUE(player_id, team_id, season_year)
);

-- TEAM SEASON STATS
CREATE TABLE IF NOT EXISTS team_season_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    team_id INTEGER NOT NULL,
    season_year INTEGER NOT NULL,
    wins INTEGER,
    losses INTEGER,
    win_pct REAL,
    conf_rank INTEGER,
    div_rank INTEGER,
    home_wins INTEGER,
    home_losses INTEGER,
    away_wins INTEGER,
    away_losses INTEGER,
    playoff_result TEXT,
    fgm REAL,
    fga REAL,
    fg_pct REAL,
    fg3m REAL,
    fg3a REAL,
    fg3_pct REAL,
    ftm REAL,
    fta REAL,
    ft_pct REAL,
    oreb REAL,
    dreb REAL,
    reb REAL,
    ast REAL,
    stl REAL,
    blk REAL,
    tov REAL,
    pf REAL,
    pts REAL,
    opp_pts REAL,
    pace REAL,
    off_rating REAL,
    def_rating REAL,
    net_rating REAL,
    payroll INTEGER,
    payroll_rank INTEGER,
    FOREIGN KEY (team_id) REFERENCES teams(id),
    UNIQUE(team_id, season_year)
);

-- COACH SEASONS
CREATE TABLE IF NOT EXISTS coach_seasons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    coach_id INTEGER NOT NULL,
    team_id INTEGER NOT NULL,
    season_year INTEGER NOT NULL,
    wins INTEGER,
    losses INTEGER,
    season_type TEXT DEFAULT 'Regular Season',
    FOREIGN KEY (coach_id) REFERENCES coaches(id),
    FOREIGN KEY (team_id) REFERENCES teams(id),
    UNIQUE(coach_id, team_id, season_year, season_type)
);

-- GAMES (team game log)
CREATE TABLE IF NOT EXISTS games (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    game_id TEXT NOT NULL,
    season_year INTEGER NOT NULL,
    game_date TEXT,
    matchup TEXT,
    team_id INTEGER NOT NULL,
    opponent_id INTEGER,
    wl TEXT,
    pts INTEGER,
    opp_pts INTEGER,
    fgm REAL,
    fga REAL,
    fg_pct REAL,
    fg3m REAL,
    fg3a REAL,
    fg3_pct REAL,
    ftm REAL,
    fta REAL,
    ft_pct REAL,
    oreb REAL,
    dreb REAL,
    reb REAL,
    ast REAL,
    stl REAL,
    blk REAL,
    tov REAL,
    pf REAL,
    plus_minus REAL,
    season_type TEXT DEFAULT 'Regular Season',
    FOREIGN KEY (team_id) REFERENCES teams(id),
    FOREIGN KEY (opponent_id) REFERENCES teams(id),
    UNIQUE(game_id, team_id)
);

-- PLAYER GAME STATS
CREATE TABLE IF NOT EXISTS player_game_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_id INTEGER NOT NULL,
    team_id INTEGER NOT NULL,
    game_id TEXT NOT NULL,
    season_year INTEGER NOT NULL,
    game_date TEXT,
    matchup TEXT,
    wl TEXT,
    min REAL,
    fgm REAL,
    fga REAL,
    fg_pct REAL,
    fg3m REAL,
    fg3a REAL,
    fg3_pct REAL,
    ftm REAL,
    fta REAL,
    ft_pct REAL,
    oreb REAL,
    dreb REAL,
    reb REAL,
    ast REAL,
    stl REAL,
    blk REAL,
    tov REAL,
    pf REAL,
    pts REAL,
    plus_minus REAL,
    game_score REAL,
    FOREIGN KEY (player_id) REFERENCES players(id),
    FOREIGN KEY (team_id) REFERENCES teams(id),
    UNIQUE(player_id, game_id)
);

-- SALARIES
CREATE TABLE IF NOT EXISTS salaries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_id INTEGER NOT NULL,
    team_id INTEGER NOT NULL,
    season_year INTEGER NOT NULL,
    salary INTEGER NOT NULL,
    FOREIGN KEY (player_id) REFERENCES players(id),
    FOREIGN KEY (team_id) REFERENCES teams(id),
    UNIQUE(player_id, team_id, season_year)
);

-- ROSTERS
CREATE TABLE IF NOT EXISTS rosters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_id INTEGER NOT NULL,
    team_id INTEGER NOT NULL,
    season_year INTEGER NOT NULL,
    position TEXT,
    jersey_num INTEGER,
    FOREIGN KEY (player_id) REFERENCES players(id),
    FOREIGN KEY (team_id) REFERENCES teams(id),
    UNIQUE(player_id, team_id, season_year)
);

-- AWARDS
CREATE TABLE IF NOT EXISTS awards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_id INTEGER NOT NULL,
    award_type TEXT NOT NULL,
    season_year INTEGER,
    description TEXT,
    FOREIGN KEY (player_id) REFERENCES players(id)
);

-- =============================================
-- INDEXES for query performance
-- =============================================
CREATE INDEX IF NOT EXISTS idx_pss_player ON player_season_stats(player_id);
CREATE INDEX IF NOT EXISTS idx_pss_team ON player_season_stats(team_id);
CREATE INDEX IF NOT EXISTS idx_pss_season ON player_season_stats(season_year);
CREATE INDEX IF NOT EXISTS idx_tss_team ON team_season_stats(team_id);
CREATE INDEX IF NOT EXISTS idx_tss_season ON team_season_stats(season_year);
CREATE INDEX IF NOT EXISTS idx_games_team ON games(team_id);
CREATE INDEX IF NOT EXISTS idx_games_season ON games(season_year);
CREATE INDEX IF NOT EXISTS idx_games_date ON games(game_date);
CREATE INDEX IF NOT EXISTS idx_games_gameid ON games(game_id);
CREATE INDEX IF NOT EXISTS idx_pgs_player ON player_game_stats(player_id);
CREATE INDEX IF NOT EXISTS idx_pgs_game ON player_game_stats(game_id);
CREATE INDEX IF NOT EXISTS idx_pgs_season ON player_game_stats(season_year);
CREATE INDEX IF NOT EXISTS idx_salaries_player ON salaries(player_id);
CREATE INDEX IF NOT EXISTS idx_salaries_team ON salaries(team_id);
CREATE INDEX IF NOT EXISTS idx_rosters_team_season ON rosters(team_id, season_year);
CREATE INDEX IF NOT EXISTS idx_coach_seasons_coach ON coach_seasons(coach_id);
CREATE INDEX IF NOT EXISTS idx_coach_seasons_team ON coach_seasons(team_id);
CREATE INDEX IF NOT EXISTS idx_awards_player ON awards(player_id);