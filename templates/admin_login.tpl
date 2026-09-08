% rebase('base.tpl', title='Administration', page='admin')

<div class="page-container login-page">
    <div class="login-intro"><div class="eyebrow">NBA Analytics / Administration</div>
        <h1>Manage your data.</h1><p>Sign in to review coverage, collect game logs and manage database backups.</p></div>
    <div class="card"><div class="card-body">
        % if defined('error') and error:
        <div class="alert alert-danger" role="alert">{{ error }}</div>
        % end
        <form method="POST" action="/nba/admin/login">
            <div class="mb-3"><label class="form-label" for="adminUsername">Username</label>
                <input type="text" name="username" id="adminUsername" class="form-control" autocomplete="username" autofocus required></div>
            <div class="mb-4"><label class="form-label" for="adminPassword">Password</label>
                <input type="password" name="password" id="adminPassword" class="form-control" autocomplete="current-password" required></div>
            <button type="submit" class="btn btn-accent w-100">Sign in</button>
        </form>
    </div></div>
    <a href="/" class="d-inline-block mt-4">← Back to dashboard</a>
</div>
