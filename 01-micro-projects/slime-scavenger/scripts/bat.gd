class_name Bat extends CharacterBody2D

signal player_touched

@onready var animated_sprite_2d: AnimatedSprite2D = $AnimatedSprite2D

@export var speed: float = 100.0
@export var point_a: Vector2
@export var point_b: Vector2

var target: Vector2

func _ready() -> void:
	position = point_a
	target = point_b

func _physics_process(delta: float) -> void:
	# distance to devuelve lo que hace falta por llegar al target en float
	if position.distance_to(target) < 2.0:
		if target == point_b:
			target = point_a
		else: 
			target = point_b
		
	var direction: Vector2 = position.direction_to(target)
	velocity = direction * speed
	move_and_slide()


func _on_hitbox_body_entered(body: Node2D) -> void:
	if body.is_in_group("player"):
		player_touched.emit()
