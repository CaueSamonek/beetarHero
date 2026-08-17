from gpiozero import AngularServo

servos = {
    "score_servo": {"pin": 23},
    "stars_servo": {"pin": 24}
}

def create(servo_name, min_value, max_value, min_angle=0, max_angle=180):
    s = servos[servo_name]
    s["servo"] = AngularServo(s['pin'], min_angle=min_angle, max_angle=max_angle)
    s['min_value'] = min_value
    s['max_value'] = max_value
    s['min_angle'] = min_angle
    s['max_angle'] = max_angle

def set(servo_name, value):
    s = servos[servo_name]
    min_value = s['min_value']
    max_value = s['max_value']
    max_angle = s['max_angle']

    # normalizacao de valor pra angulo
    angle = (value - min_value) / (max_value - min_value) * max_angle
    
    s["servo"].angle = angle
