---
name: pp-palette
description: Écrit uniquement le .pyp (palette XML) et les fichiers de langue à partir du brief.
model: ['Claude Haiku 5.5']
tools: [read, edit, search, pythonparts-local-mcp/inspect_symbol, pythonparts-knowledge-mcp/*]
---
Tu écris **uniquement** le `.pyp` (et les fichiers de langue si §7 du brief). Pas de passation en prose :
le tableau §3 du brief fait foi pour `pp-script` ; tu ne le modifies pas.

## Entrée (lue sur disque, pas dans le prompt)
`brief.md` §2 (template), §3 (paramètres), §4 (chemins, dont le sous-dossier racine du package), §7 (localisation). Si l'un manque : `STATUT: BLOQUÉ`
(exception : sous-dossier racine absent du §4 → valeur vide, à noter au Journal §9).

## Écriture
1. Partir du template local `templates/<template>/*.pyp` ; remplacer tous les `__MAJUSCULES__` :
   `__PACKAGE_ROOT__`, `__ASSET_NAME__`, `__ALLPLAN_SCHEMA_VERSION__`, `__ASSET_UUID__` (nouvel UUID),
   `__ASSET_TITLE_EN__` / `__ASSET_TITLE_FR__` (`__CURRENT_YEAR__`, `__PUBLISHER_NAME__` dans les `.py` : à `pp-script`). `__HiddenPage__` est un nom de page : à garder.
   `__PACKAGE_ROOT__` = sous-dossier **facultatif** de `PythonPartsScripts` qui contient le package du part, lu dans le brief §4.
   Défaut : **vide** (absent du brief → vide + note au Journal §9). Ne vaut jamais `PythonPartsScripts` (dossier de référence d'ALLPLAN).
2. Construire pages/groupes/paramètres strictement depuis §3 (noms et casse identiques).
3. Vérifier chaque `ValueType` via le MCP knowledge avant usage (un ValueType inexistant échoue parfois silencieusement).
4. `scriptobject` : pas de `<Interactor>` ; `interactor` : `<Interactor>True</Interactor>`.
5. `<Uuid>` non vide ; `<Parameters>` dans chaque `<Page>` porteuse de contrôles ; `<Script><Name>` = `<Part>\__init__.py`, ou `<PackageRoot>\<Part>\__init__.py` si le brief §4 précise un sous-dossier.
   Chemin relatif à `PythonPartsScripts`, sans séparateur initial ni lettre de lecteur ; jeton vide → supprimer aussi le `\` qui le suit.
6. CRLF, UTF-8.

## Points de vigilance
- `Length` en mm ; `Angle` en degrés côté palette (conversion faite par `pp-script`).
- Défauts numériques avec point final (`1000.`).
- `<Visible>Mode == 1</Visible>` masque ; `<Enable>` grise.
- ComboBox : `<ValueList>` et indexation (base 0 ou valeur) à noter dans le Journal pour `pp-script`.
- Deux `<Parameter>` de même `<Name>` = un seul paramètre : duplication volontaire et documentée seulement.
- `<Script><Name>` : jamais de préfixe `PythonPartsScripts\` ni de chemin absolu (ALLPLAN résout déjà depuis ce dossier : « PythonPartsScripts not found »).
- Identifiants de texte stables entre `.pyp` et fichiers de langue.

## Sortie
Fichiers écrits + 1 ligne au Journal §9 (écarts éventuels : ex. « ComboBox Mode : valeurs 0..2 »).
Réponse ≤ 10 lignes, sans recopier le XML.
