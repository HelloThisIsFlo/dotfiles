# Kubectl abbreviations
# Replaces lewisacidic/fish-kubectl-abbr plugin with hand-managed abbrs.
# Organised by resource type, most-used first.

# ── General ──────────────────────────────────────────────────────────

abbr -a k      'kubectl'
abbr -a kaf    'kubectl apply -f'
abbr -a keti   'kubectl exec -t -i'
abbr -a kdel   'kubectl delete'
abbr -a kdelf  'kubectl delete -f'
abbr -a kpf    'kubectl port-forward'
abbr -a kga    'kubectl get all'
abbr -a kgaa   'kubectl get all --all-namespaces'
abbr -a kcp    'kubectl cp'

# ── Config / context ─────────────────────────────────────────────────

abbr -a kcuc   'kubectl config use-context'
abbr -a kcsc   'kubectl config set-context'
abbr -a kcdc   'kubectl config delete-context'
abbr -a kccc   'kubectl config current-context'
abbr -a kcgc   'kubectl config get-contexts'
abbr -a kcn    'kubectl config set-context --current --namespace'

# ── Logs ─────────────────────────────────────────────────────────────

abbr -a kl     'kubectl logs'
abbr -a klf    'kubectl logs -f'
abbr -a kls    'kubectl logs --since'
abbr -a klfs   'kubectl logs -f --since'
abbr -a klt    'kubectl logs -t'

# ── Pods ─────────────────────────────────────────────────────────────

abbr -a kgp      'kubectl get pods'
abbr -a kgpa     'kubectl get pods --all-namespaces'
abbr -a kgpw     'kubectl get pods --watch'
abbr -a kgpwide  'kubectl get pods -o wide'
abbr -a kgpall   'kubectl get pods --all-namespaces -o wide'
abbr -a kgpl     'kubectl get pods -l'
abbr -a kgpn     'kubectl get pods -n'
abbr -a kep      'kubectl edit pods'
abbr -a kdp      'kubectl describe pods'
abbr -a kdelp    'kubectl delete pods'

# ── Services ─────────────────────────────────────────────────────────

abbr -a kgs      'kubectl get svc'
abbr -a kgsa     'kubectl get svc --all-namespaces'
abbr -a kgsw     'kubectl get svc --watch'
abbr -a kgswide  'kubectl get svc -o wide'
abbr -a kes      'kubectl edit svc'
abbr -a kds      'kubectl describe svc'
abbr -a kdels    'kubectl delete svc'

# ── Ingress ──────────────────────────────────────────────────────────

abbr -a kgi    'kubectl get ingress'
abbr -a kgia   'kubectl get ingress --all-namespaces'
abbr -a kei    'kubectl edit ingress'
abbr -a kdi    'kubectl describe ingress'
abbr -a kdeli  'kubectl delete ingress'

# ── Namespaces ───────────────────────────────────────────────────────

abbr -a kgns    'kubectl get namespaces'
abbr -a kens    'kubectl edit namespace'
abbr -a kdns    'kubectl describe namespace'
abbr -a kdelns  'kubectl delete namespace'

# ── ConfigMaps ───────────────────────────────────────────────────────

abbr -a kgcm    'kubectl get configmaps'
abbr -a kgcma   'kubectl get configmaps --all-namespaces'
abbr -a kecm    'kubectl edit configmap'
abbr -a kdcm    'kubectl describe configmap'
abbr -a kdelcm  'kubectl delete configmap'

# ── Secrets ──────────────────────────────────────────────────────────

abbr -a kgsec    'kubectl get secret'
abbr -a kgseca   'kubectl get secret --all-namespaces'
abbr -a kdsec    'kubectl describe secret'
abbr -a kdelsec  'kubectl delete secret'

# ── Deployments ──────────────────────────────────────────────────────

abbr -a kgd      'kubectl get deployment'
abbr -a kgda     'kubectl get deployment --all-namespaces'
abbr -a kgdw     'kubectl get deployment --watch'
abbr -a kgdwide  'kubectl get deployment -o wide'
abbr -a ked      'kubectl edit deployment'
abbr -a kdd      'kubectl describe deployment'
abbr -a kdeld    'kubectl delete deployment'
abbr -a ksd      'kubectl scale deployment'
abbr -a krsd     'kubectl rollout status deployment'

# ── ReplicaSets / rollouts ───────────────────────────────────────────

abbr -a kgrs   'kubectl get replicaset'
abbr -a kdrs   'kubectl describe replicaset'
abbr -a kers   'kubectl edit replicaset'
abbr -a krh    'kubectl rollout history'
abbr -a kru    'kubectl rollout undo'

# ── StatefulSets ─────────────────────────────────────────────────────

abbr -a kgss      'kubectl get statefulset'
abbr -a kgssa     'kubectl get statefulset --all-namespaces'
abbr -a kgssw     'kubectl get statefulset --watch'
abbr -a kgsswide  'kubectl get statefulset -o wide'
abbr -a kess      'kubectl edit statefulset'
abbr -a kdss      'kubectl describe statefulset'
abbr -a kdelss    'kubectl delete statefulset'
abbr -a ksss      'kubectl scale statefulset'
abbr -a krsss     'kubectl rollout status statefulset'

# ── Nodes ────────────────────────────────────────────────────────────

abbr -a kgno    'kubectl get nodes'
abbr -a keno    'kubectl edit node'
abbr -a kdno    'kubectl describe node'
abbr -a kdelno  'kubectl delete node'

# ── PVCs ─────────────────────────────────────────────────────────────

abbr -a kgpvc    'kubectl get pvc'
abbr -a kgpvca   'kubectl get pvc --all-namespaces'
abbr -a kgpvcw   'kubectl get pvc --watch'
abbr -a kepvc    'kubectl edit pvc'
abbr -a kdpvc    'kubectl describe pvc'
abbr -a kdelpvc  'kubectl delete pvc'

# ── Service accounts ─────────────────────────────────────────────────

abbr -a kdsa    'kubectl describe sa'
abbr -a kdelsa  'kubectl delete sa'

# ── DaemonSets ───────────────────────────────────────────────────────

abbr -a kgds    'kubectl get daemonset'
abbr -a kgdsw   'kubectl get daemonset --watch'
abbr -a keds    'kubectl edit daemonset'
abbr -a kdds    'kubectl describe daemonset'
abbr -a kdelds  'kubectl delete daemonset'

# ── CronJobs ─────────────────────────────────────────────────────────

abbr -a kgcj    'kubectl get cronjob'
abbr -a kecj    'kubectl edit cronjob'
abbr -a kdcj    'kubectl describe cronjob'
abbr -a kdelcj  'kubectl delete cronjob'

# ── Jobs ─────────────────────────────────────────────────────────────

abbr -a kgj    'kubectl get job'
abbr -a kej    'kubectl edit job'
abbr -a kdj    'kubectl describe job'
abbr -a kdelj  'kubectl delete job'
