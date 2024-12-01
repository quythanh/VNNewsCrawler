class Article:
    def __init__(self, title: str, description, paragraphs, src: str, img: str):
        self.title = title
        self.description = description
        self.paragraphs = paragraphs
        self.src = src
        self.img = img

    def __str__(self):
        _str = self.src + "\n\n"
        _str += (self.img or "https://assets.appsmith.com/widgets/default.png") + "\n\n"
        _str += self.title + "\n\n"

        for p in self.description:
            _str += p + "\n"
        _str += "\n"

        for p in self.paragraphs:
            _str += p + "\n"

        return _str
