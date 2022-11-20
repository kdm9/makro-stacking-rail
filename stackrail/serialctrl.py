import serial

class SerialController(object):

    def __init__(self, ttyusb="/dev/ttyUSB0", baud=115200, **kwargs):
        super().__init__()
        self.con = serial.Serial(ttyusb, baud, **kwargs)
        self.con.timeout = 0.01

    def communicate(self, msg):
        res = self.con.read_until().rstrip()
        bmsg = msg.encode('ascii')
        l = self.con.write(bmsg)
        assert l == len(bmsg)
        self.con.flush()
        res = ""
        while not res.endswith('\n'):
            res += self.con.read_until().decode('ascii')
        if res.startswith("FAIL"):
            raise RuntimeError("Failed to communciate with device")
        assert res.startswith("OK")
        return res.rstrip()
        
    def move(self, movement):
        return self.communicate(f"M{movement}")
            
    def speed(self, speed):
        return self.communicate(f"S{speed}")

    def usteps(self, usteps):
        return self.communicate(f"U{usteps}")
            
