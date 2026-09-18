# -*- coding: utf-8 -*-
"""
battlemap.py
============

Emplacement suggere dans le projet : OPR_soloIA/battlemap.py

Represente la table de jeu comme un ensemble d'objets a empreinte
polygonale (decors, unites, objectifs) et calcule, a partir de ces
empreintes, un maillage triangulaire (triangulation de Delaunay
contrainte) qui remplace l'ancienne grille cartesienne fine.

Principe general
-----------------
- Chaque `FieldObject` porte un polygone Shapely et des proprietes de
  terrain (infranchissable / couvert / obstruant / difficile), une
  hauteur (utile pour les futurs calculs de ligne de vue), et une
  categorie (decor, objectif, unite IA, unite joueur).

- `Battlemap` collecte les aretes de tous ces polygones (plus le
  contour rectangulaire de la table), les "planarise" (ajoute un
  sommet a chaque intersection, y compris quand deux empreintes se
  chevauchent -- ex: une unite postee dans un bois) via
  `shapely.ops.unary_union`, puis en deduit une triangulation
  contrainte (PSLG) grace a la bibliotheque `triangle`. Si celle-ci
  n'est pas installee, on se replie sur une triangulation de Delaunay
  non contrainte via scipy (les aretes des decors ne sont alors plus
  garanties presentes comme aretes du maillage).

- Chaque triangle du maillage est ensuite "tague" (infranchissable,
  couvert, obstruant, difficile) selon les polygones dans lesquels
  tombe son centre de gravite -- exact equivalent du masque applique
  noeud par noeud sur l'ancienne grille, mais sur un maillage dont la
  resolution s'adapte a la geometrie du terrain plutot qu'a un pas
  fixe.

Perimetre de cette premiere version
------------------------------------
Ce module construit et visualise le maillage. Il expose aussi
`triangle_indices_for` (triangles occupes par un objet donne) comme
point d'ancrage pour les prochaines briques (pathfinding, LoS, champs
de degats), mais n'implemente pas encore ces algorithmes.
"""

from __future__ import annotations

import math
import warnings
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Sequence, Tuple, Union

import numpy as np
from shapely.geometry import LineString, MultiLineString, MultiPolygon, Point, Polygon, box
from shapely.ops import unary_union

import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection, PatchCollection
from matplotlib.patches import Polygon as MplPolygon

try:
    import triangle as _triangle_lib
    _HAS_TRIANGLE = True
except ImportError:
    _HAS_TRIANGLE = False
    from scipy.spatial import Delaunay as _ScipyDelaunay

    warnings.warn(
        "Le paquet 'triangle' n'est pas installe : la triangulation "
        "utilisera un repli scipy.spatial.Delaunay non contraint (les "
        "aretes des decors ne sont pas garanties presentes dans le "
        "maillage). Installer avec : pip install triangle"
    )

DEFAULT_RESOLUTION = 3

GeomLike = Union[Polygon, MultiPolygon]


def _contains_many(geom, xs: np.ndarray, ys: np.ndarray) -> np.ndarray:
    """Teste, pour un unique geom (potentiellement une union de
    plusieurs polygones), quels points (xs[i], ys[i]) sont contenus.
    Utilise shapely.vectorized si disponible (rapide), sinon une
    geometrie preparee + boucle (toujours correct, juste plus lent)."""
    if geom is None or geom.is_empty:
        return np.zeros(len(xs), dtype=bool)
    try:
        import shapely.vectorized as _sv
        return np.asarray(_sv.contains(geom, xs, ys))
    except Exception:
        from shapely.prepared import prep
        prepared = prep(geom)
        return np.array([prepared.contains(Point(x, y)) for x, y in zip(xs, ys)], dtype=bool)


class FieldCategory(Enum):
    """Nature d'un objet pose sur la table."""
    DECOR = "decor"
    OBJECTIVE = "objectif"
    UNIT_AI = "unite_ia"
    UNIT_PLAYER = "unite_joueur"


@dataclass
class FieldObject:
    """
    Un objet pose sur la table, identifie par son empreinte polygonale.

    name             : etiquette libre (affichage / retrouver l'objet)
    category         : decor / objectif / unite IA / unite joueur
    polygon          : empreinte au sol (Polygon ou MultiPolygon shapely ;
                       typiquement l'union des disques de socle pour une
                       unite a plusieurs figurines)
    hauteur          : hauteur en pouces (utile pour la LoS, non
                       exploitee par ce module pour l'instant)
    infranchissable  : bloque le mouvement (et generalement tir/charge
                       au travers)
    couvert          : offre un couvert aux figurines qui s'y trouvent
                       ou sont tirees au travers
    obstruant        : bloque la ligne de vue
    difficile        : ralentit le mouvement sans le bloquer
    """

    name: str
    category: FieldCategory
    polygon: GeomLike
    hauteur: float = 0.0
    infranchissable: bool = False
    couvert: bool = False
    obstruant: bool = False
    difficile: bool = False

    # Rempli uniquement pour les objets construits via FieldObject.unite() :
    # position de chaque socle (centre), rayon commun, et resolution du
    # buffer utilisee pour approximer chaque socle en polygone. Necessaire
    # pour pouvoir repositionner une unite plus tard (cf. Battlemap.move_unit).
    # Par convention, socles[0] est la figurine "centrale" / ancre de l'unite.
    socles: Optional[List[Tuple[float, float]]] = None
    rayon_socle: Optional[float] = None
    resolution: int = DEFAULT_RESOLUTION

    # -- constructeurs pratiques ----------------------------------------

    @classmethod
    def decor(
        cls,
        name: str,
        polygon: GeomLike,
        hauteur: float = 0.0,
        infranchissable: bool = False,
        couvert: bool = False,
        obstruant: bool = False,
        difficile: bool = False,
    ) -> "FieldObject":
        return cls(
            name=name, category=FieldCategory.DECOR, polygon=polygon, hauteur=hauteur,
            infranchissable=infranchissable, couvert=couvert,
            obstruant=obstruant, difficile=difficile,
        )

    @classmethod
    def objectif(cls, name: str, centre: Tuple[float, float], rayon: float = 3.0) -> "FieldObject":
        """Objectif circulaire (rayon standard OPR : 3")."""
        return cls(
            name=name, category=FieldCategory.OBJECTIVE,
            polygon=Point(centre).buffer(rayon, resolution=DEFAULT_RESOLUTION),
        )

    @classmethod
    def unite(
        cls,
        name: str,
        side: FieldCategory,
        socles: Sequence[Tuple[float, float]],
        rayon_socle: float,
        hauteur: float = 0.0,
        infranchissable: bool = True,
        obstruant: bool = True,
        resolution: int = DEFAULT_RESOLUTION,
    ) -> "FieldObject":
        """
        Empreinte d'une unite = union des disques de chaque figurine
        (les socles sont toujours ronds, cf. hypothese du projet).
        `socles` est la liste des centres (x, y) de chaque figurine
        vivante ; pour une unite a 1 figurine, une seule position. Par
        convention, socles[0] est la figurine "centrale" de l'unite.
        `side` doit etre FieldCategory.UNIT_AI ou FieldCategory.UNIT_PLAYER.
        `resolution` regle le nombre de segments par quart de cercle
        utilise pour approximer chaque socle (impacte directement la
        taille du maillage -- a reduire pour des unites nombreuses).
        """
        if side not in (FieldCategory.UNIT_AI, FieldCategory.UNIT_PLAYER):
            raise ValueError("side doit etre FieldCategory.UNIT_AI ou FieldCategory.UNIT_PLAYER")
        socles = list(socles)
        disques = [Point(c).buffer(rayon_socle, resolution=resolution) for c in socles]
        empreinte = unary_union(disques)
        return cls(
            name=name, category=side, polygon=empreinte, hauteur=hauteur,
            infranchissable=infranchissable, obstruant=obstruant,
            socles=socles, rayon_socle=rayon_socle, resolution=resolution,
        )

    # -- utilitaires ---------------------------------------------------

    def rings(self) -> List[List[Tuple[float, float]]]:
        """Genere tous les anneaux (contour exterieur + trous eventuels)
        de toutes les composantes du polygone, sous forme de listes de
        points (sans repeter le point de fermeture)."""
        polys = self.polygon.geoms if isinstance(self.polygon, MultiPolygon) else [self.polygon]
        out = []
        for poly in polys:
            if poly.is_empty:
                continue
            out.append(list(poly.exterior.coords)[:-1])
            for interior in poly.interiors:
                out.append(list(interior.coords)[:-1])
        return out


@dataclass
class TriangleTags:
    """Tags calcules pour chaque triangle du maillage. Tableaux numpy
    booleens alignes sur l'ordre de Battlemap.triangles."""
    infranchissable: np.ndarray
    couvert: np.ndarray
    obstruant: np.ndarray
    difficile: np.ndarray


class Battlemap:
    """
    Table de jeu + ensemble d'objets a empreinte polygonale + maillage
    triangulaire calcule a partir de ces empreintes.
    """

    #: proprietes de terrain -> couleur d'affichage
    _PROPERTY_COLORS = {
        "infranchissable": "#4a4a4a",
        "couvert": "#7fae7f",
        "obstruant": "#8f6a4a",
        "difficile": "#c9a54c",
    }

    _CATEGORY_STYLE = {
        FieldCategory.OBJECTIVE: dict(facecolor="#f2c744", edgecolor="#8a6d00", alpha=0.55),
        FieldCategory.UNIT_AI: dict(facecolor="#e05252", edgecolor="#7a1010", alpha=0.65),
        FieldCategory.UNIT_PLAYER: dict(facecolor="#4c8bf2", edgecolor="#0a2d7a", alpha=0.65),
    }

    def __init__(self, width: float = 60.0, height: float = 44.0):
        self.width = width
        self.height = height
        self.objects: List[FieldObject] = []

        self.points: Optional[np.ndarray] = None       # (N, 2)
        self.triangles: Optional[np.ndarray] = None     # (M, 3) indices dans points
        self.tags: Optional[TriangleTags] = None

    # ------------------------------------------------------------------
    # Gestion des objets
    # ------------------------------------------------------------------

    def add_object(self, obj: FieldObject) -> FieldObject:
        """Ajoute un objet a la table, en le decoupant d'abord aux
        limites du plateau (une empreinte qui deborderait n'a pas de
        sens pour le maillage). Invalide le maillage courant."""
        table = box(0, 0, self.width, self.height)
        clipped = obj.polygon.intersection(table)
        if clipped.is_empty:
            warnings.warn(f"L'objet {obj.name!r} est entierement hors table : ignore.")
            return obj
        obj.polygon = clipped
        self.objects.append(obj)
        self._invalidate_mesh()
        return obj

    def remove_object(self, name: str) -> None:
        self.objects = [o for o in self.objects if o.name != name]
        self._invalidate_mesh()

    def objects_by_category(self, category: FieldCategory) -> List[FieldObject]:
        return [o for o in self.objects if o.category is category]

    def _invalidate_mesh(self) -> None:
        self.points = None
        self.triangles = None
        self.tags = None

    # ------------------------------------------------------------------
    # Construction du maillage
    # ------------------------------------------------------------------

    def build_mesh(self, force: bool = False) -> None:
        """Calcule (ou recalcule) la triangulation contrainte du
        plateau. A appeler apres tout ajout/suppression/deplacement
        d'objet (idempotent tant que rien n'a change, sauf force=True)."""
        if self.triangles is not None and not force:
            return

        points, segments = self._collect_pslg()

        if _HAS_TRIANGLE:
            tri_input = {"vertices": points, "segments": segments}
            result = _triangle_lib.triangulate(tri_input, "p")
            self.points = np.asarray(result["vertices"], dtype=float)
            self.triangles = np.asarray(result["triangles"], dtype=int)
        else:
            delaunay = _ScipyDelaunay(points)
            self.points = points
            self.triangles = delaunay.simplices

        self._classify_triangles()

    def _collect_pslg(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Construit le PSLG (points + segments contraints) a partir du
        contour de la table et de tous les anneaux de tous les objets.

        Les aretes sont d'abord "planarisees" via unary_union (shapely)
        pour garantir qu'aucun segment ne croise un autre sans sommet
        partage -- indispensable des que deux empreintes se
        chevauchent (ex : unite postee dans un bois), sans quoi la
        triangulation contrainte echoue.
        """
        lines: List[LineString] = self._ring_lines(
            [(0, 0), (self.width, 0), (self.width, self.height), (0, self.height)]
        )
        for obj in self.objects:
            for ring_pts in obj.rings():
                lines.extend(self._ring_lines(ring_pts))

        noded = unary_union(MultiLineString(lines))
        noded_lines = list(noded.geoms) if hasattr(noded, "geoms") else [noded]

        index_of: Dict[Tuple[float, float], int] = {}
        points: List[Tuple[float, float]] = []
        segments: List[Tuple[int, int]] = []

        def get_index(xy: Tuple[float, float]) -> int:
            key = (round(xy[0], 4), round(xy[1], 4))
            idx = index_of.get(key)
            if idx is None:
                idx = len(points)
                index_of[key] = idx
                points.append(key)
            return idx

        for line in noded_lines:
            coords = list(line.coords)
            for a, b in zip(coords[:-1], coords[1:]):
                ia, ib = get_index(a), get_index(b)
                if ia != ib:
                    segments.append((ia, ib))

        return np.array(points, dtype=float), np.array(segments, dtype=int)

    @staticmethod
    def _ring_lines(ring_pts: Sequence[Tuple[float, float]]) -> List[LineString]:
        n = len(ring_pts)
        return [LineString([ring_pts[i], ring_pts[(i + 1) % n]]) for i in range(n)]

    def _classify_triangles(self) -> None:
        centroids = self.points[self.triangles].mean(axis=1)
        cx, cy = centroids[:, 0], centroids[:, 1]

        def union_for(prop_name: str):
            geoms = [o.polygon for o in self.objects if getattr(o, prop_name)]
            return unary_union(geoms) if geoms else None

        self.tags = TriangleTags(
            infranchissable=_contains_many(union_for("infranchissable"), cx, cy),
            couvert=_contains_many(union_for("couvert"), cx, cy),
            obstruant=_contains_many(union_for("obstruant"), cx, cy),
            difficile=_contains_many(union_for("difficile"), cx, cy),
        )

    # ------------------------------------------------------------------
    # Acces pratiques (points d'ancrage pour les briques a venir)
    # ------------------------------------------------------------------

    def triangle_indices_for(self, obj: FieldObject) -> np.ndarray:
        """Indices des triangles dont le centre tombe dans l'empreinte
        de `obj` (utile p.ex. pour savoir quels triangles sont occupes
        par une unite ou controles par un objectif)."""
        self.build_mesh()
        centroids = self.points[self.triangles].mean(axis=1)
        mask = _contains_many(obj.polygon, centroids[:, 0], centroids[:, 1])
        return np.nonzero(mask)[0]

    def walkable_triangle_indices(self) -> np.ndarray:
        """Indices des triangles non infranchissables (point d'ancrage
        pour un futur pathfinding sur le maillage)."""
        self.build_mesh()
        return np.nonzero(~self.tags.infranchissable)[0]

    # ------------------------------------------------------------------
    # Repositionnement d'une unite (sans pathfinding)
    # ------------------------------------------------------------------

    def move_unit(
        self,
        name: str,
        target: Tuple[float, float],
        espacement_min: float = 0.2,
        max_anneaux: int = 60,
    ) -> FieldObject:
        """
        Replace toutes les figurines d'une unite deja posee sur la
        table autour du point `target`, sans se soucier du chemin
        parcouru (pas de pathfinding ici : seule la position finale
        compte).

        Regles de placement :
            1. La figurine "centrale" (socles[0]) est posee au plus
               pres possible de `target` (a `target` lui-meme si la
               place y est libre).
            2. Les autres figurines sont ensuite packees le plus pres
               possible de la figurine centrale, sur un maillage
               hexagonal (le pavage le plus dense pour des disques de
               rayon fixe), avec un espacement bord-a-bord d'au moins
               `espacement_min` entre deux figurines.
            3. Aucune figurine ne peut empieter sur un terrain
               infranchissable (y compris l'empreinte d'un AUTRE objet
               marque infranchissable, decor ou unite), et le segment
               reliant chaque figurine a la figurine centrale ne doit
               pas traverser de terrain infranchissable.

        Procede (cf. discussion) :
            1. l'unite est retiree de la liste des objets avant tout
               calcul, pour que sa propre ancienne empreinte n'entrave
               pas son propre repositionnement ;
            2. les nouvelles positions de socles sont calculees ;
            3. l'unite (meme instance, polygone recalcule) est
               reinseree et le maillage est invalide pour etre
               recalcule au prochain build_mesh().

        Leve une erreur si l'unite n'a pas ete construite via
        `FieldObject.unite(...)` (positions de socles inconnues), ou
        si toutes les figurines n'ont pas pu etre placees dans la
        limite de `max_anneaux` anneaux hexagonaux explores.
        """
        obj = next((o for o in self.objects if o.name == name), None)
        if obj is None:
            raise KeyError(f"Aucun objet nomme {name!r} sur la table.")
        if obj.socles is None or obj.rayon_socle is None:
            raise ValueError(
                f"L'objet {name!r} n'a pas ete cree via FieldObject.unite(...) : "
                "positions de socles inconnues, repositionnement impossible."
            )

        nb_figurines = len(obj.socles)
        rayon = obj.rayon_socle
        pas = 2 * rayon + espacement_min

        # 1. Retirer l'unite du maillage / des contraintes de terrain :
        # son ancienne empreinte ne doit pas bloquer son propre
        # repositionnement.
        self.objects.remove(obj)
        table_poly = box(0, 0, self.width, self.height)
        blocage = self._infranchissable_union()

        # 2a. Figurine centrale : target si libre, sinon la case valide
        # la plus proche sur le meme maillage hexagonal.
        centre = self._plus_proche_case_valide(target, rayon, pas, blocage, table_poly, max_anneaux)
        positions = [centre]

        # 2b. Le reste de l'unite : cases hexagonales autour du centre,
        # triees par distance croissante, filtrees par validite +
        # visibilite (non bloquee) depuis la figurine centrale.
        unite_union = None
        if nb_figurines > 1:
            for candidat in self._candidats_hexagonaux(centre, pas, max_anneaux):
                if len(positions) >= nb_figurines:
                    break
                if not self._position_valide(candidat, rayon, blocage, table_poly):
                    continue
                if self._segment_bloque(candidat, centre, blocage):
                    continue
                if unite_union is None :
                    unite_union = Point(candidat).buffer(obj.rayon_socle,resolution = DEFAULT_RESOLUTION)
                else :
                    new_pt = Point(candidat).buffer(obj.rayon_socle,resolution = DEFAULT_RESOLUTION)
                    if unite_union.intersection(new_pt).area < 1e-9 :
                        unite_union = unite_union.union(new_pt)
                    else :
                        continue
                positions.append(candidat)

        if len(positions) < nb_figurines:
            # On remet l'objet tel quel avant d'echouer, pour ne pas
            # perdre l'unite si l'appelant rattrape l'exception.
            self.objects.append(obj)
            self._invalidate_mesh()
            raise RuntimeError(
                f"Impossible de placer les {nb_figurines} figurines de {name!r} "
                f"autour de {target} (seulement {len(positions)} position(s) valide(s) "
                f"trouvee(s) dans un rayon de {max_anneaux} anneaux)."
            )

        # 3. Reappliquer l'unite (meme instance) au maillage.
        obj.socles = positions
        obj.polygon = unary_union(
            [Point(p).buffer(rayon, resolution=obj.resolution) for p in positions]
        )
        self.objects.append(obj)
        self._invalidate_mesh()
        return obj

    def _infranchissable_union(self):
        """Union de tous les objets actuellement marques infranchissable
        (decors ET unites) -- None si aucun."""
        geoms = [o.polygon for o in self.objects if o.infranchissable]
        return unary_union(geoms) if geoms else None

    @staticmethod
    def _position_valide(point, rayon: float, blocage, table_poly) -> bool:
        """Une figurine posee en `point` est valide si son socle reste
        entierement sur la table et ne chevauche pas (en surface) le
        terrain infranchissable. Un simple contact bord-a-bord est
        tolere (test sur l'aire de recouvrement, pas sur l'intersection
        geometrique brute)."""
        socle = Point(point).buffer(rayon, resolution=DEFAULT_RESOLUTION)
        if not table_poly.contains(socle):
            return False
        if blocage is not None and socle.intersection(blocage).area > 1e-9:
            return False
        return True

    @staticmethod
    def _segment_bloque(p1, p2, blocage) -> bool:
        """Vrai si le segment [p1, p2] traverse l'interieur d'un
        terrain infranchissable (un simple contact tangent au bord,
        sans traverser, n'est pas considere comme bloquant)."""
        if blocage is None:
            return False
        segment = LineString([p1, p2])
        return segment.intersects(blocage) and not segment.touches(blocage)

    def _plus_proche_case_valide(self, target, rayon, pas, blocage, table_poly, max_anneaux):
        """Renvoie `target` si une figurine peut s'y poser, sinon la
        case valide la plus proche sur le maillage hexagonal de pas
        `pas` centre sur `target`."""
        if self._position_valide(target, rayon, blocage, table_poly):
            return target
        for candidat in self._candidats_hexagonaux(target, pas, max_anneaux):
            if self._position_valide(candidat, rayon, blocage, table_poly):
                return candidat
        raise RuntimeError(
            f"Aucune position valide trouvee pres de {target} "
            f"(terrain infranchissable ou bord de table) dans un rayon de "
            f"{max_anneaux} anneaux."
        )

    @staticmethod
    def _candidats_hexagonaux(centre: Tuple[float, float], pas: float, max_anneaux: int):
        """
        Genere, anneau par anneau puis triees par distance euclidienne
        croissante au sein de chaque anneau, les positions d'un
        maillage hexagonal de pas `pas` (distance minimale garantie
        entre deux points quelconques du maillage) centre sur `centre`
        -- le pavage le plus dense pour des disques de rayon fixe.
        `centre` lui-meme (anneau 0) n'est jamais produit par ce
        generateur : il est traite a part par l'appelant.
        """
        cx, cy = centre
        sqrt3 = math.sqrt(3)
        sqrt2 = math.sqrt(2)
        # 6 directions axiales d'un maillage hexagonal, dans l'ordre
        # utilise pour parcourir un anneau par cotes successifs.
        directions = [(math.cos(theta), math.sin(theta)) for theta in np.linspace(0,355,144)
                      ]


        for anneau in range(1, max_anneaux + 1):
            # Parcours standard d'un anneau hexagonal de rayon `anneau`
            # (cf. algorithmes de grille hexagonale) : on part d'un
            # sommet de l'anneau puis on avance de cote en cote.
            xc, yc = centre
            points =  []
            for dx, dy in directions:
                xp = xc + anneau * dx * pas
                yp = yc + anneau * dy * pas
                points.append((xp, yp))
            points.sort(key=lambda p: (p[0] - cx) ** 2 + (p[1] - cy) ** 2)
            for p in points:
                yield p

    # ------------------------------------------------------------------
    # Visualisation
    # ------------------------------------------------------------------

    def plot(self, mode: str = "mesh", ax=None, show_mesh: bool = True, title: Optional[str] = None):
        """
        Affiche la table de jeu selon `mode` :
            "mesh"             -> maillage seul
            "infranchissable"  -> maillage + triangles infranchissables
            "couvert"          -> maillage + triangles offrant un couvert
            "obstruant"        -> maillage + triangles obstruant la vue
            "difficile"        -> maillage + triangles de terrain difficile
            "objectifs"        -> maillage + empreintes des objectifs
            "unites_ia"        -> maillage + empreintes des unites IA
            "unites_joueur"    -> maillage + empreintes des unites joueur
        """
        self.build_mesh()
        if ax is None:
            _, ax = plt.subplots(figsize=(self.width / 6, self.height / 6))

        ax.set_xlim(0, self.width)
        ax.set_ylim(0, self.height)
        ax.set_aspect("equal")
        ax.add_patch(
            MplPolygon(
                [(0, 0), (self.width, 0), (self.width, self.height), (0, self.height)],
                closed=True, fill=False, edgecolor="black", linewidth=1.2, zorder=5,
            )
        )

        if show_mesh:
            self._draw_mesh(ax)

        if mode == "mesh":
            pass
        elif mode in self._PROPERTY_COLORS:
            self._draw_triangle_property(ax, mode)
        elif mode == "objectifs":
            self._draw_objects(ax, FieldCategory.OBJECTIVE)
        elif mode == "unites_ia":
            self._draw_objects(ax, FieldCategory.UNIT_AI)
        elif mode == "unites_joueur":
            self._draw_objects(ax, FieldCategory.UNIT_PLAYER)
        else:
            raise ValueError(f"mode inconnu : {mode!r}")

        ax.set_title(title or mode)
        return ax

    def _draw_mesh(self, ax) -> None:
        segs = []
        for tri in self.triangles:
            pts = self.points[tri]
            segs.append([pts[0], pts[1]])
            segs.append([pts[1], pts[2]])
            segs.append([pts[2], pts[0]])
        ax.add_collection(LineCollection(segs, colors="#bbbbbb", linewidths=0.5, zorder=1))

    def _draw_triangle_property(self, ax, prop_name: str) -> None:
        mask = getattr(self.tags, prop_name)
        color = self._PROPERTY_COLORS[prop_name]
        patches = [MplPolygon(self.points[tri], closed=True) for tri in self.triangles[mask]]
        if patches:
            ax.add_collection(PatchCollection(patches, facecolor=color, edgecolor="none", alpha=0.55, zorder=2))

    def _draw_objects(self, ax, category: FieldCategory) -> None:
        style = self._CATEGORY_STYLE[category]
        for obj in self.objects_by_category(category):
            polys = obj.polygon.geoms if isinstance(obj.polygon, MultiPolygon) else [obj.polygon]
            for poly in polys:
                if poly.is_empty:
                    continue
                ax.add_patch(MplPolygon(list(poly.exterior.coords), closed=True, zorder=3, **style))
            cx, cy = obj.polygon.centroid.x, obj.polygon.centroid.y
            ax.annotate(obj.name, (cx, cy), ha="center", va="center", fontsize=8, zorder=4)

    def plot_all(self, figsize: Tuple[float, float] = (18, 9)):
        """Grille de sous-graphiques, un par mode -- pratique pour
        controler visuellement un scenario d'un coup d'oeil."""
        modes = [
            "mesh", "infranchissable", "couvert", "difficile",
            "obstruant", "objectifs", "unites_ia", "unites_joueur",
        ]
        fig, axes = plt.subplots(2, 4, figsize=figsize)
        for mode, ax in zip(modes, axes.flat):
            self.plot(mode=mode, ax=ax, show_mesh=True)
        fig.tight_layout()
        return fig