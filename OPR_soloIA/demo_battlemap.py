# -*- coding: utf-8 -*-
"""Demo / test manuel de battlemap.py sur un scenario type OPR."""
import matplotlib.pyplot as plt
from shapely.geometry import box as shapely_box
from shapely.geometry import Polygon as shapely_polygon

from battlemap import Battlemap, FieldObject, FieldCategory

bm = Battlemap(width=60, height=44)

# -- decors -----------------------------------------------------------

# Un mur : infranchissable + obstruant
mur = shapely_box(18, 10, 20, 30)
bm.add_object(FieldObject.decor("Mur nord-sud", mur, hauteur=2.0,
                                 infranchissable=True, obstruant=True))

# Une ruine en L (polygone concave) : infranchissable partiel + obstruant
ruine = shapely_box(35, 5, 50, 8).union(shapely_box(47, 5, 50, 20))
bm.add_object(FieldObject.decor("Ruine en L", ruine, hauteur=3.0,
                                 infranchissable=True, obstruant=True))


# Une ruine en L (polygone concave) : infranchissable partiel + obstruant
ruine2 = shapely_box(23, 38, 33, 35).union(shapely_box(33, 35, 30, 20))
bm.add_object(FieldObject.decor("Ruine en L 2", ruine2, hauteur=3.0,
                                 infranchissable=True, obstruant=True))

# Un bois : couvert + difficile (pas infranchissable)
bois = shapely_box(5, 25, 18, 40)
bm.add_object(FieldObject.decor("Bois", bois, hauteur=1.5,
                                 couvert=True, difficile=True))

# -- objectif -----------------------------------------------------------

bm.add_object(FieldObject.objectif("Objectif central", (30, 22), rayon=3.0))

# -- unites --------------------------------------------------------------

# Unite IA de 5 figurines en ligne, DANS le bois (empreinte qui chevauche
# le decor "couvert" -> teste le cas de chevauchement / noding).
socles_ia = [(8 + i * 2.0, 32) for i in range(20)]
archers_unit = FieldObject.unite("Archers IA", FieldCategory.UNIT_AI,
                                 socles_ia, rayon_socle=28/2 * 3/64, hauteur=1.8)
bm.add_object(archers_unit)

# Unite joueur solo (heros), en terrain degage
bm.add_object(FieldObject.unite("Champion joueur", FieldCategory.UNIT_PLAYER,
                                 [(45, 35)], rayon_socle=40/2 * 3/64, hauteur=1.9))

# -- construction + verifs ------------------------------------------------

bm.build_mesh()

bm.move_unit("Archers IA", (28, 33), )

bm.build_mesh()

print(f"Position archers (centroid) : ({archers_unit.polygon.centroid.x:.1f}, {archers_unit.polygon.centroid.y:.1f})")

print(f"Sommets  : {len(bm.points)}")
print(f"Triangles: {len(bm.triangles)}")
print(f"Triangles infranchissables : {bm.tags.infranchissable.sum()}")
print(f"Triangles couvert          : {bm.tags.couvert.sum()}")
print(f"Triangles obstruant        : {bm.tags.obstruant.sum()}")
print(f"Triangles difficile        : {bm.tags.difficile.sum()}")

archers = bm.objects_by_category(FieldCategory.UNIT_AI)[0]
idx = bm.triangle_indices_for(archers)
print(f"Triangles occupes par 'Archers IA' : {len(idx)}")

walkable = bm.walkable_triangle_indices()
print(f"Triangles walkable (non infranchissables) : {len(walkable)} / {len(bm.triangles)}")

fig = bm.plot_all()

plt.show()
print("OK - figure sauvegardee")
