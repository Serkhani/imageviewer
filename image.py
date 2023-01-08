class Image:
    def __init__(self, source: str, gps):
        self.source = source
        self.name = source.split('//')[-1].split('.')[0]
        self.gps = gps

    def isEqual(image: Image) -> bool:
        return (self.name == image.name) and (self.gps == image.gps)