# points

import yaml
import json
import numpy as np


# class Criterion:

#     """

#     Parameters:
#     norm: two numbers specifying the scope of normal values. For example (-5, 5) or (3, 3.5)
#     """
#     def __init__(self, norm):
        
#         self.norm = norm

#         pass



def angle_between_vectors(v1, v2):
    """
    Calculates the angle between two vectors in radians.

    Parameters:
    v1 (np.ndarray): The first vector.
    v2 (np.ndarray): The second vector.

    Returns:
    float: The angle between the vectors in radians.
    """
    # Calculate the dot product
    dot_product = np.dot(v1, v2)

    # Calculate the magnitudes of the vectors
    magnitude_v1 = np.linalg.norm(v1)
    magnitude_v2 = np.linalg.norm(v2)

    # Calculate the cosine of the angle
    # Clip the value to ensure it's within [-1, 1] to avoid potential floating point errors
    cosine_angle = np.clip(dot_product / (magnitude_v1 * magnitude_v2), -1.0, 1.0)

    # Calculate the angle in radians using arccos
    angle_radians = np.arccos(cosine_angle)

    return angle_radians


def chopart_angle_calculate():
    """ Расчет угла Шопарова сустава (alpha1)
    
    """
    lB1S = np.array(points["S"]) - np.array(points["B1"])
    lBS = np.array(points["S"]) - np.array(points["B"])

    angle = np.degrees(angle_between_vectors(lB1S, lBS))

    # print(angle)

    return angle


def first_finger_deviation_caluclate():
    """ Расчет угла отклонения 1-го пальца (alpha2)
    
    """
    lDA1 = np.array(points["D"]) - np.array(points["A1"])
    lA1A = np.array(points["A1"]) - np.array(points["A"])

    angle = np.degrees(angle_between_vectors(lDA1, lA1A))
    # print(angle)

    return angle



def check_value_for_deviation(criterion_name, value):
    criterion = foot_diagnose_table.get(criterion_name)

    if not criterion:
        return -1

    normal = criterion['normal']
    
    if normal['min'] <= value <= normal['max']:
        return 0
    

    if criterion.get('longitudinal_flatfoot'):

        for dev_degree, degree_values in criterion['longitudinal_flatfoot'].items():
            if degree_values['max'] == 'Inf':
                if degree_values['min'] <= value:
                    return degree_values['degree']
            elif degree_values['min'] <= value <= degree_values['max']:
                return degree_values['degree']
        return -1
    
    if criterion.get('forefoot_splay'):

        for dev_degree, degree_values in criterion['forefoot_splay'].items():
            if degree_values['max'] == 'Inf':
                if degree_values['min'] <= value:
                    return degree_values['degree']
            elif degree_values['min'] <= value <= degree_values['max']:
                return degree_values['degree']
        return -1
    
    
def forefoot_spread_calculate():
    """ Расчет коэффициента распластаности переднего отдела стопы (k2).
    
    """
    foot_length = 132.09
    foot_width_bundles = 57.05

    return foot_width_bundles / foot_length

# print(check_value_for_deviation('first_finger_deviation', 11))

def scaphoid_height_calculate():
    """ Значение высоты бугристости ладьевидной кости (G')
    
    """

    return 29.11


def podometric_index_calculate():
    """ Расчет подометрического индекса (p)
    
    p = h / L * 100

    p - подометрический индекс. Измеряется в процентах.
    h - высота до ладьевидной кости
    L - длина стопы
    
    """
    foot_length = 136.94
    scaphoid_height = 48.26

    return scaphoid_height / foot_length * 100

if __name__ == '__main__':
    global points

    points = {}

    with open('foot_diagnose_table.yml', 'r') as f:
        foot_diagnose_table: dict = yaml.safe_load(f)

    
    with open('project-1-at-2025-09-03-20-45-48dde6f7.json') as f:
        fannotations = json.load(f)

        annot_points = fannotations[0]["annotations"][0]["result"]

        for annot_point in annot_points:
            value = annot_point["value"]

            x = int(value["x"])
            y = int(value["y"])
            label = value["keypointlabels"][0]

            points[label] = (x, y)


    print('Угол Шопарова сустава(alpha1):', chopart_angle_calculate())
    print('Подометрический индекс (p)%:', podometric_index_calculate())
    print('Угол отклонения первого пальца(alpha2):', first_finger_deviation_caluclate())
    print('Коэффициент распластаности переднего отдела стопы (k2):', forefoot_spread_calculate())

    print('Диагноз:')

    # Берем два критерия, по которым смотрится наибольшее отклонение - это и есть степень деформации.

    degree = []
    degree.append(check_value_for_deviation('chopart_angle_deviation', chopart_angle_calculate()))
    degree.append(check_value_for_deviation('podometric_index_deviation', podometric_index_calculate()))

    degree_max = max(degree)
    if degree_max == 0:
        print('Деформаций соответствующим продольному плоскостопию на снимках нету.')
    else:
        print(f'Снимку стопы соответствует {degree_max} степень продольного плоскостопия.')


    degree = []
    degree.append(check_value_for_deviation('first_finger_deviation', first_finger_deviation_caluclate()))
    degree.append(check_value_for_deviation('forefoot_spread_deviation', forefoot_spread_calculate()))
    
    degree_max = max(degree)
    if degree_max == 0:
        print('Деформаций соответствующим распластанности переднего отдела стопы на снимках нету.')
    else:
        print(f'Снимку стопы соответствует {degree_max} степень распластанности переднего отдела стопы.')