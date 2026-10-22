# <NomPart> — Brief (source de vérité)
> Propriétaire : pp-orchestrateur. Les autres agents lisent des sections, n'éditent que le §9 (une ligne).

## 0. Statut
`CADRAGE | GELÉ | PRODUCTION | RELECTURE | PRÊT À TESTER` — gel le : <date>

## 0b. Prérequis (fichiers/informations à fournir avant conception)
| Prérequis | Fourni ? (oui/non) | Chemin ou précision | Bloquant ? |
|---|---|---|---|
(Ex. module existant à réutiliser, géométrie de test, norme, règle métier. Un prérequis bloquant non fourni arrête le cadrage : l'orchestrateur le demande une seule fois.)

## 1. Objectif métier
(Criticité : standard | critique — si critique, revue complète par pp-relecteur en heavy, voir orchestrateur.)
## 2. Template retenu (`scriptobject` | `interactor`) + justification (2 lignes)
## 3. Paramètres (figés)
| Nom XML | ValueType | Unité | Défaut | Min/Max | Visibilité | Accès Python | Rôle |
|---|---|---|---|---|---|---|---|
## 4. Fichiers et propriétaires
| Fichier (chemin absolu) | Propriétaire | Rôle | Niveau (light/medium/heavy) + raison |
|---|---|---|---|
(Niveau = difficulté de la tâche, fixée au plan par l'orchestrateur ; ≠ niveau par défaut de l'agent → override temporaire dans model-tiers.json.)

## 5. Algorithme géométrique (étapes, sans code)
## 6. Contrat d'interface calcul pur ↔ script (figé)
| Fonction publique | Entrées (type neutre, unité) | Sortie (type neutre, unité) | Échec | Module |
|---|---|---|---|---|
Conventions : mm ; radians côté calcul / degrés côté palette ; repère direct Z haut ; contours fermés (dernier = premier), sens trigo.
| Type neutre | Type ALLPLAN cible | Conversion (pp-script) |
|---|---|---|
## 7. Localisation (si activée)
| TextId | Texte par défaut | Emplacement `.pyp` | Fichiers de langue |
|---|---|---|---|
## 8a. Exigences de cycle de vie (à trancher avant gel — sources de retours tardifs)
- [ ] Création / aperçu (`create_preview`)
- [ ] Modification : réouverture de la palette (`modify_element_property`, `build_ele` relu depuis le PythonPart)
- [ ] Source externe (ex. mur) supprimée ou modifiée après création : le PythonPart doit-il rester ouvrable ?
- [ ] Données stockées dans le PythonPart (valeurs saisies, références) pour la réouverture
- [ ] Hiérarchie / sélectionnabilité (groupe vs enfants), vues 2D / 3D
- [ ] Points d'API non vérifiables hors ALLPLAN (type retourné, comportement) → test humain ciblé, listé en §10
## 8. Risques et cas limites
## 9. Journal (une ligne par intervention, ajout seulement)
| Date | Agent | Statut | Fichiers | Bloquants / note |
|---|---|---|---|---|

## 10. Consigne de test humain (orchestrateur)
## 11. Évolutions (mode correctif : demande | fichiers | critère de test)
