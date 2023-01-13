class ImageData:
    def __init__(self, source: str, gps: dict):
        self.source = source
        self.name = source.split('\\')[-1].split('.')[0]
        self.gps = gps

    def isEqual(self, image: 'ImageData') -> bool:
        return (self.name == image.name) and (self.gps == image.gps)