% rebase('base.tpl', title='Admin Login', page='admin')

<div class="page-container" style="max-width:420px;margin:80px auto;">
    <div class="card">
        <div class="card-header text-center">
            <h4 style="margin:0;"><i class="bi bi-shield-lock me-2"></i>Admin Login</h4>
        </div>
        <div class="card-body">
            % if defined('error') and error:
            <div class="alert alert-danger" style="background:rgba(255,45,85,0.15);border:1px solid var(--accent-red);color:var(--accent-red);border-radius:8px;padding:0.75rem;margin-bottom:1rem;">
                <i class="bi bi-x-circle me-1"></i>{{ error }}
            </div>
            % end
            <form method="POST" action="/nba/admin/login">
                <div class="mb-3">
                    <label class="form-label" style="color:var(--text-secondary);font-size:0.85rem;">Username</label>
                    <input type="text" name="username" class="form-control" autofocus required
                           style="background:var(--bg-secondary);border-color:var(--border-color);color:var(--text-primary);">
                </div>
                <div class="mb-3">
                    <label class="form-label" style="color:var(--text-secondary);font-size:0.85rem;">Password</label>
                    <input type="password" name="password" class="form-control" required
                           style="background:var(--bg-secondary);border-color:var(--border-color);color:var(--text-primary);">
                </div>
                <button type="submit" class="btn btn-accent w-100">
                    <i class="bi bi-box-arrow-in-right me-2"></i>Sign In
                </button>
            </form>
        </div>
    </div>
</div>
