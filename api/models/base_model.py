import inspect

class BaseModel:
    def to_dict(self):
        result = {}
        for key, value in self.__dict__.items():
            if not key.startswith("_"):
                if isinstance(value, BaseModel):  # Если поле тоже является BaseModel
                    result[key] = value.to_dict()  # Рекурсивно вызываем to_dict
                else:
                    result[key] = value  # Иначе просто добавляем значение
        return result

    @classmethod
    def from_dict(cls, data):
        # Получаем список параметров конструктора класса
        params = inspect.signature(cls).parameters
        filtered_data = {}

        for key, value in data.items():
            if key in params:
                param_type = params[key].annotation
                # Проверяем, является ли тип параметра подклассом BaseModel
                if inspect.isclass(param_type) and issubclass(param_type, BaseModel):
                    filtered_data[key] = param_type.from_dict(value)  # Рекурсивно создаем объект
                else:
                    filtered_data[key] = value  # Простое значение

        return cls(**filtered_data)
