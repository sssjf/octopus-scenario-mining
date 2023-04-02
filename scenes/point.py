class Point:
    def __init__(self, obj_id, x, y, sec, ncesc, frame_no, classification, velocity, angle):
        self.id = obj_id
        self.x = x
        self.y = y
        self.sec = sec
        self.nsecs = ncesc
        self.frame_no = frame_no
        self.classification = classification
        self.velocity = velocity
        self.angle = angle
