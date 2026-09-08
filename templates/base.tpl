<!DOCTYPE html>
<html lang="en" data-bs-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ get('title', 'NBA Analytics') }} | NBA Analytics</title>

    <!-- Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">

    <!-- Bootstrap 5 -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">

    <!-- Bootstrap Icons -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css" rel="stylesheet">

    <!-- Chart.js -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>

    <!-- Custom CSS -->
    <link rel="stylesheet" href="/static/css/style.css?v=9">
</head>
<body>
    <a class="skip-link" href="#mainContent">Skip to content</a>
    <!-- NAVBAR -->
    <nav class="navbar navbar-expand-xl">
        <div class="container-fluid px-3">
            <a class="navbar-brand" href="/">
                <span class="brand-mark" aria-hidden="true"><i class="bi bi-dribbble"></i></span>
                <span class="brand-text">NBA Analytics</span>
            </a>

            <button class="navbar-toggler border-0" type="button" data-bs-toggle="collapse" data-bs-target="#mainNav" aria-controls="mainNav" aria-expanded="false" aria-label="Toggle navigation">
                <i class="bi bi-list" style="color: var(--accent-cyan); font-size: 1.5rem;"></i>
            </button>

            <div class="collapse navbar-collapse" id="mainNav">
                <ul class="navbar-nav me-auto mb-2 mb-lg-0">
                    <li class="nav-item">
                        <a class="nav-link {{ 'active' if get('page', '') == 'home' else '' }}" href="/">
                            <i class="bi bi-house-door me-1"></i>Home
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link {{ 'active' if get('page', '') == 'teams' else '' }}" href="/team/">
                            <i class="bi bi-people me-1"></i>Teams
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link {{ 'active' if get('page', '') == 'players' else '' }}" href="/player/">
                            <i class="bi bi-person me-1"></i>Players
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link {{ 'active' if get('page', '') == 'coaches' else '' }}" href="/coach/">
                            <i class="bi bi-clipboard-data me-1"></i>Coaches
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link {{ 'active' if get('page', '') == 'games' else '' }}" href="/games/">
                            <i class="bi bi-calendar-event me-1"></i>Games
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link {{ 'active' if get('page', '') == 'leaders' else '' }}" href="/leaders">
                            <i class="bi bi-trophy me-1"></i>Leaders
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link {{ 'active' if get('page', '') == 'compare' else '' }}" href="/compare">
                            <i class="bi bi-arrow-left-right me-1"></i>Compare
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link {{ 'active' if get('page', '') == 'salaries' else '' }}" href="/salaries">
                            <i class="bi bi-currency-dollar me-1"></i>Salaries
                        </a>
                    </li>
                </ul>

                <!-- Search -->
                <div class="search-box">
                    <i class="bi bi-search search-icon"></i>
                    <input type="text" id="globalSearch" aria-label="Search players and teams" placeholder="Search players, teams..." autocomplete="off">
                    <div class="search-results" id="searchResults"></div>
                </div>
            </div>
        </div>
    </nav>

    <!-- MAIN CONTENT -->
    <main id="mainContent">
        {{!base}}
    </main>

    <!-- FOOTER -->
    <footer class="site-footer">
        <div class="footer-inner">
            <span>NBA Analytics <span aria-hidden="true">&middot;</span> Season archive</span>
            <span>Data from <a href="https://www.nba.com" target="_blank" rel="noopener">NBA.com</a>
                <span aria-hidden="true">&middot;</span> <a href="/nba/admin/">Administration</a></span>
        </div>
    </footer>

    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>

    <!-- Chart.js default config for dark theme -->
    <script src="/static/js/common.js?v=9"></script>

</body>
</html>