# Workflow multi-agents PythonParts (VS Code + GitHub Copilot)

Configuration pour développer des PythonParts ALLPLAN avec une équipe d'agents Copilot.
Principe : le modèle le plus puissant planifie et tranche, des modèles moins chers produisent, le plus léger fait les tâches simples.

| Agent | Niveau | Rôle |
|---|---|---|
| `pp-orchestrateur` | heavy | Cadrage, plan validé, brief, délégation, décision finale. Ne lit pas de code, ne débogue pas. |
| `pp-geo-calcul` | medium | Calcul géométrique pur (`geometry.py`) et tests pytest. |
| `pp-script` | medium | Assemblage ALLPLAN (`__init__.py`, `main.py`), lance `check_part`. |
| `pp-palette` | light | Fichier `.pyp` et fichiers de langue. |
| `pp-relecteur` | medium (heavy si part critique) | Revue, écrit uniquement `review.md`. |
| `pp-eclaireur` | light | Recherche et lecture seule, réponses de 10 lignes maximum. |

## Contenu

```
.github/
  agents/*.agent.md        # les six agents
  model-tiers.json         # niveaux de modèles (seul fichier à éditer pour changer de modèle)
  copilot-instructions.md  # règles communes, volontairement courtes
.vscode/
  mcp.json                 # serveurs MCP (voir Installation)
templates/
  brief.md                 # gabarit du brief (source de vérité d'un part)
  scriptobject/            # squelette ScriptObject
  interactor/              # squelette Interactor
tools/
  check_part.py            # contrôles déterministes + pytest (sans IA)
  sync_models.py           # applique model-tiers.json aux agents
docs/                      # créé à l'usage, un dossier par part (non partagé)
```

## Installation

1. Copiez ces dossiers à la racine de votre dossier de travail (dans nos exemples `C:\Data\Allplan\PythonPartsDev`).
   Gardez l'arborescence : les agents utilisent des chemins relatifs à cette racine.
2. Ouvrez le dossier dans VS Code comme dossier de workspace nommé `Pilotage`, avec les dossiers ALLPLAN (framework, Std, exemples) en plus.
3. Dans les paramètres du workspace, vérifiez :
   - `chat.agentFilesLocations` : `{ ".github/agents": true }` ;
   - l'interpréteur Python d'ALLPLAN, les chemins `python.analysis.*` et `pylint.args`, qui contiennent des chemins propres à chaque poste.
4. `.vscode/mcp.json` : adaptez `--std-path` et `--usr-path` à votre installation. Le serveur de connaissances est commun.
5. Python 3.10 ou plus avec `pytest` sur le Python système (utilisé par `check_part.py`, qui n'a pas besoin du framework ALLPLAN).
6. Dans `.github/copilot-instructions.md`, corrigez le chemin de la racine si le vôtre diffère.
7. Vérifiez la cohérence :
   ```
   python tools/sync_models.py --check
   ```

## Changer de modèle

1. Modifiez `.github/model-tiers.json` (listes `tiers`, `available`).
2. `python tools/sync_models.py` met à jour la ligne `model:` de chaque agent.
3. `python tools/sync_models.py --check` signale tout écart.

`overrides` permet de changer le niveau d'un agent pour une tâche seulement. L'orchestrateur l'utilise pour les parts critiques, puis le vide.

## Utilisation

1. Appelez `pp-orchestrateur` avec la demande métier. Il pose ses questions en une série, liste les prérequis, puis présente un plan (agents, niveaux, criticité) à valider avant de geler le brief.
2. Les agents échangent des chemins de fichiers, jamais du contenu. Tout passe par `docs/<part>/brief.md`, `api.md`, `review.md` et `reports/`.
3. Les agents producteurs lancent eux-mêmes :
   ```
   python tools/check_part.py <package_dir> <pyp> --template scriptobject|interactor --docs docs/<part>
   ```
4. Part critique : la revue complète passe en heavy (voir `pp-orchestrateur`), puis retour au niveau par défaut.
5. Petite correction, contrat d'interface inchangé : appelez directement l'agent propriétaire du fichier avec la demande, le fichier et le critère de test.

## Bonnes pratiques de coût

- Garder `copilot-instructions.md` court : il est rechargé à chaque appel.
- Ne pas joindre tous les fichiers `.md` à chaque tâche : les agents lisent des sections ciblées.
- Laisser l'orchestrateur décider, pas déboguer : au deuxième échec d'un contrôle, il délègue ou remonte.
- Éviter les recherches larges dans le framework ou Std. Si besoin, ajouter `search.exclude` dans le workspace.

## À ne pas partager

- `docs/<part>/` : briefs, rapports et revues de vos parts (données de projet).
- Les chemins et noms d'utilisateur de votre fichier `.code-workspace`.

## Dépôt Git conseillé

`.gitignore` minimal :

```
docs/
__pycache__/
*.pyc
.pytest_cache/
```
