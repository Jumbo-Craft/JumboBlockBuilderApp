import builder
from app import App
from pathlib import Path


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    #builder.model2nbt('./output/structure/weathered_copper_bulb_lit.json')

    #builder.model2nbt(".\\input\\jumbo_models\\dirt.json")
    builder.convert_all()

    #App().show()
