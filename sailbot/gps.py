from point import Point
import config
import serial

class AttributeDict(dict):
    """Access elements of the dict as attributes"""
    def __getattr__(self, attr):
        return self[attr]

    def __setattr__(self, attr, value):
        self[attr] = value

def _float_or_none(value):
    if value:
        return float(value)
    else:
        return None

class Gps(object):
    """A GPS receiver"""
    def __init__(self):
        self._gpsSerial = serial.Serial(config.gpsSerialport, 4800, timeout=0.5)

    def position(self):
        """Return a Point containing the current coordinates from the GPS"""
        for i in range(10):
            line = self._gpsSerial.readline(None).strip()
            if line.startswith('$GPGGA'):
                break

        print line
        if self.checksum(line):
            fields = self._name_fields(line)
            if fields.id == 'GPGGA':
                lat = self._parse_degrees(fields.lat)
                long = self._parse_degrees(fields.long)
                return Point(lat, long)
        else:
            raise ValueError('Checksum failed')

    def _parse_degrees(self, strDegrees):
        """
        Return the decimal representation of a combined degree/minute string
        """
        if not strDegrees:
            #return none if the input is empty
            return None

        pointIndex = strDegrees.find('.') - 2
        degrees = _float_or_none(strDegrees[:pointIndex])
        minutes = _float_or_none(strDegrees[pointIndex:])
        return (degrees + minutes / 60)

    def checksum(self, line):
        """Return True if the checksum passed"""
        x = 0
        for c in line[1:-3]:
            x ^= ord(c)
        x = str(hex(x))[2:].upper()
        check_digits = line[-2:].upper()
        return check_digits == x

    def _name_fields(self, line):
        """Return an AttributeDict containing the more important GGA fields"""
        fields = line[1:-3].split(',')[:8]
        names = [
                    'id',
                    'time',
                    'lat',
                    'lat_direction',
                    'long',
                    'long_direction',
                    'fix_quality',
                    'satellite_number',
                    'hdop',
                    'altitude'
                ]
        d = AttributeDict()
        for i in range(len(fields)):
            print i, names[i], fields[i]
            d[names[i]] = fields[i]
        return d

if __name__ == '__main__':
    demoline = '$GPGGA,113245.000,5223.9915,N,00352.1781,W,1,08,1.0,329.0,M,50.9,M,,0000*4A'
    line = '$GPGGA,144143.113,,,,,0,00,,,M,0.0,M,,0000*52'
    gps = Gps()
    print gps.checksum(line)
    d = line.split(',')[2]
    print d
    print gps._parse_degrees(d)
