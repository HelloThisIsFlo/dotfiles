# Terraform abbreviations
# Replaces lewisacidic/fish-terraform plugin with hand-managed abbrs.

# ── Core workflow ────────────────────────────────────────────────────

abbr -a tf     'terraform'
abbr -a tfi    'terraform init'
abbr -a tfp    'terraform plan'
abbr -a tfa    'terraform apply'
abbr -a tfaa   'terraform apply -auto-approve'
abbr -a tfd    'terraform destroy'
abbr -a tfd!   'terraform destroy -auto-approve'
abbr -a tfv    'terraform validate'

# ── Combined commands ────────────────────────────────────────────────

abbr -a tfip   'terraform init && terraform plan'
abbr -a tfia   'terraform init && terraform apply'
abbr -a tfia!  'terraform init && terraform apply -auto-approve'

# ── Inspect ──────────────────────────────────────────────────────────

abbr -a tfo    'terraform output'
abbr -a tfor   'terraform output --raw'
abbr -a tfoj   'terraform output --json'
abbr -a tfs    'terraform show'
abbr -a tfc    'terraform console'
abbr -a tfg    'terraform graph'

# ── State and resources ──────────────────────────────────────────────

abbr -a tfst   'terraform state'
abbr -a tfimp  'terraform import'
abbr -a tft    'terraform taint'
abbr -a tfunt  'terraform untaint'
abbr -a tfr    'terraform refresh'

# ── Misc ─────────────────────────────────────────────────────────────

abbr -a tfget  'terraform get'
abbr -a tfprov 'terraform providers'
abbr -a tfw    'terraform workspace'
abbr -a tfver  'terraform version'
