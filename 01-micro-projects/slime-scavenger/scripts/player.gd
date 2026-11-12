class_name Player extends CharacterBody2D

@onready var animated_sprite_2d: AnimatedSprite2D = $AnimatedSprite2D

@export var speed: float = 100.0
@export var slow_factor: float = 2.0
var direction: Vector2

func _physics_process(delta: float) -> void:
	_apply_movement()
	_change_animation_state()
	_flip_sprite_direction()
	

func _apply_movement() -> void:
	direction = Input.get_vector("move_left", "move_right", "move_up", "move_down")
	if Input.is_action_pressed("slow_walk"):
		velocity = direction * (speed / slow_factor)
	else:
		velocity = direction * speed

	move_and_slide()
	
func _change_animation_state() -> void:
	if direction == Vector2.ZERO:
		animated_sprite_2d.play("idle")
	else:
		animated_sprite_2d.play("walk")
		
func _flip_sprite_direction() -> void:
	if direction.x > 0:
		animated_sprite_2d.flip_h = false
	elif  direction.x < 0:
		animated_sprite_2d.flip_h = true
