class Challenges:
    def __init__(self, **kwargs):
        # Se inicializan todos los atributos con los valores proporcionados en kwargs
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __repr__(self) -> str:
        return f"<Challenges with {len(self.__dict__)} items>"

    def __str__(self) -> str:
        challenges_str = ', '.join([f"{key}={value}" for key, value in self.__dict__.items()])
        return f"Challenges({challenges_str})"
