def inject(*to_inject):
    def wrapper(fn):
        def wrapper2(*args, **kwargs):
            injectees = []
            for injectee in to_inject:
                injectees.append(getattr(Injector.model, injectee))

            return fn(*args, *injectees, **kwargs)

        return wrapper2
    return wrapper


class Injector:
    model = None

    @classmethod
    def set_model(cls, model):
        cls.model = model

