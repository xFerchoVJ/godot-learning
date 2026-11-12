## Builds scenes/level_map.tscn from assets/tiles/level_layout.txt.
## Run (from the project root): Godot --headless --path . --script art-src/build_map.gd
extends SceneTree

const LAYOUT := "res://assets/tiles/level_layout.txt"
const TILESET := "res://assets/tiles/tileset.tres"
const OUT := "res://scenes/level_map.tscn"
const CHAR_TO_ATLAS := {"a": 0, "b": 1, "c": 2, "#": 3, "R": 4}


func _init() -> void:
	var layer := TileMapLayer.new()
	layer.name = "Map"
	layer.tile_set = load(TILESET)

	var lines := FileAccess.get_file_as_string(LAYOUT).strip_edges().split("\n")
	for y in lines.size():
		for x in lines[y].length():
			layer.set_cell(Vector2i(x, y), 0, Vector2i(CHAR_TO_ATLAS[lines[y][x]], 0))

	var scene := PackedScene.new()
	scene.pack(layer)
	var err := ResourceSaver.save(scene, OUT)
	print("saved ", OUT, " err=", err, " cells=", layer.get_used_cells().size())
	quit()
