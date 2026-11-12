extends Node2D

@onready var label: Label = $Label
@onready var timer: Timer = $Timer
@onready var time_label: Label = $Label2
@onready var gem_collect: AudioStreamPlayer = $Audios/gem_collect
@onready var lose: AudioStreamPlayer = $Audios/lose
@onready var restart: AudioStreamPlayer = $Audios/restart
@onready var win: AudioStreamPlayer = $Audios/win

@export var game_time: float = 30

var game_over: bool = false
var collected_gems: int = 0
var total_gems: int = 0

func _ready() -> void:
	_loop_and_connect_signals()
	label.text = _build_label_text(collected_gems)
	timer.start(game_time)
	
	
func _process(delta: float) -> void:
	if Input.is_action_just_pressed("reload_game") and game_over:
		restart.play()
	_show_time_left()
	

func _show_time_left() -> void:
	var time_left: float = timer.time_left
	time_label.text = str(int(time_left))
	
	
func _collected_gem() -> void:
	if game_over:
		return
	
	collected_gems += 1
	
	if collected_gems == total_gems:
		_end_game(true)
	else:
		gem_collect.play()
		label.text = _build_label_text(collected_gems)

func _on_bat_player_touched() -> void:
	_end_game(false)

func _build_label_text(collected_gems_qty: int) -> String:
	return "Gemas: %d / %d" % [collected_gems_qty,total_gems]

func _loop_and_connect_signals() -> void:
	var gems: Array = get_tree().get_nodes_in_group("gem")
	var bats: Array = get_tree().get_nodes_in_group("bat")
	
	total_gems = gems.size()
	
	for gem: Gem in gems:
		gem.collected.connect(_collected_gem)
		
	for bat: Bat in bats:
		bat.player_touched.connect(_on_bat_player_touched)
		
func _stop_nodes() -> void:
	var nodes_array: Array = get_tree().get_nodes_in_group("bat")		
	var player: Player = get_tree().get_first_node_in_group("player")

	if is_instance_valid(player):
		nodes_array.append(player)
	
	for node in nodes_array:
		node.set_physics_process(false)
		node.animated_sprite_2d.stop()
	
func _on_timer_timeout() -> void:
	_end_game(false)

func _end_game(won: bool) -> void:
	if game_over:
		return
	game_over = true
	_stop_nodes()
	timer.paused = true
	if not won:
		label.text = "¡Perdiste!"
		lose.play()
	else:
		label.text = "¡Ganaste!"
		win.play()
	


func _on_restart_finished() -> void:
	get_tree().reload_current_scene()
