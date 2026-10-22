# Contexte projet — PythonParts ALLPLAN
(Chargé à chaque appel : rester court. Détails métier → `brief.md`, ciblé par section.)

## Environnement
- Versions ALLPLAN / Python jamais codées en dur : `pythonparts-local-mcp/get_allplan_info`, `get_python_env_info`.
- Python + XML (`.pyp`). UTF-8 ; CRLF pour les `.pyp`. Jamais `Prg/` ni `Etc/PythonPartsFramework/`.
- Racine de travail = dossier de workspace `Pilotage` : `.github/`, `.vscode/`, `templates/`, `tools/`, `docs/<part>/`. Lancer les outils depuis cette racine.
- `templates/` : `brief.md` (gabarit du brief), `scriptobject/`, `interactor/`. Squelettes uniquement là, jamais ailleurs.
- Déploiement réel (`<std>` via `get_allplan_info`) : code `<std>\PythonPartsScripts\<Part>\{__init__.py, main.py, geometry.py, tests\}` ;
  palette `<std>\Library\PythonParts\<Part>\{<Part>.pyp, <Part>_eng.xml, <Part>_fra.xml}`.

## Passation par fichiers (économie de contexte)
Les agents échangent des **chemins**, jamais du contenu. `docs/<part>/` : `brief.md` (source de vérité),
`api.md` (cache `inspect_symbol`), `review.md` (verdict), `reports/` (pytest.txt, check.md).
1. Prompt de délégation ≤ 10 lignes : tâche, chemin du brief, **sections à lire**, fichiers autorisés.
2. Lecture ciblée : sections listées seulement ; ni brief entier, ni code d'un autre agent, ni autres fichiers `.md`/dossiers du workspace sans nécessité. Recherches : par nom de fichier ou symbole précis, dans `Pilotage` et le dossier du part ; jamais de regex large sur `Std/` ou le framework.
3. Réponse ≤ 10 lignes : `STATUT: OK|BLOQUÉ`, fichiers, bloquants (chemin:ligne) + 1 ligne au Journal §9. Aucune recopie de code ni de sortie brute.
4. `api.md` avant tout `inspect_symbol`. Contrat §6 figé : évolution via orchestrateur → geo-calcul → script.
5. `python tools/check_part.py <package_dir> <pyp> --template <t> --docs docs/<part>` (depuis la racine `Pilotage`), lancé par l'agent producteur (`pp-script`, `pp-geo-calcul`) avant toute relecture. Max 2 essais par anomalie, puis remontée avec le chemin du rapport.

## Règles absolues
1. Aucune API inventée : `inspect_symbol` avant écriture.
2. Aucun fichier livré sans `typecheck_file` à zéro erreur (chemin absolu).
3. Un PythonPart = lot `.pyp` + `.py` (+ langues). `build_ele.<Nom>.value` = `<Name>` XML, casse comprise.
4. Pas de code spéculatif ni de `except` muet. Imports locaux relatifs.
5. Alias : `Settings, ArchElements, BaseElements, BasisElements, Geometry, ElementAdapter, Input, Precast, Reinforcement, Utility`.
6. Entrées framework : scriptobject → `check_allplan_version`, `create_script_object` (+ classe dérivée de `BaseScriptObject`) ; interactor → `check_allplan_version`, `create_preview`, `create_interactor`.
7. `.pyp` : `<Uuid>` non vide, `<Parameters>` par page, `<Interactor>` cohérent.
8. Code/docstrings/commentaires en anglais ; pas de noms courts (`x, res, tmp, obj, val, data`).
9. Unités : mm ; radians dans le calcul, degrés dans la palette, conversion unique dans `pp-script`.
10. Statut final : « typechecké, vérifié par introspection et prêt à tester dans ALLPLAN ».

## Modèles
Source unique : `.github/model-tiers.json` (niveaux `light` / `medium` / `heavy`, `overrides` temporaires).
Après modification : `python tools/sync_models.py` (`--check` pour vérifier).
Répartition : heavy = `pp-orchestrateur` (plan, décision, assemblage ; ni lecture de code ni débogage) ; medium = `pp-geo-calcul`, `pp-script`, `pp-relecteur` ;
light = `pp-palette`, `pp-eclaireur` (recherche/lecture seule). Escalade : 2 échecs d'un agent au contrôle → override d'un niveau pour la tâche, puis retour au défaut.
