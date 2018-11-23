# для работы нужен graphviz
# для запуска выполнить python3 model_to_uml.py
from sqlalchemy_schemadisplay import create_uml_graph
from sqlalchemy.orm import class_mapper

# импортируем нужную модель
import models as model


mappers = []
for attr in dir(model):
    if attr[0] == '_': continue
    try:
        cls = getattr(model, attr)
        mappers.append(class_mapper(cls))
    except:
        pass
print(2)
graph = create_uml_graph(mappers, show_operations=False, show_multiplicity_one=False)
print(3)
# указываем название выходного файла
graph.write_png('model.png')
