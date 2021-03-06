# Two_Frame_Truss.py

from StructuralAnalysis import Node, Structure, Section, Material, Solver, Visualization
from StructuralAnalysis.FrameElements import *
import math

steel = Material.Steel(250 * 10 ** 6, 400 * 10 * 6, 200 * 10 ** 6, 0.2)
section = Section.Circle(0.3)
section_2 = Section.Circle(0.6)
section_3 = Section.Rectangle(0.02, 0.06)


def frame_truss(z):
    # this function creates single truss frame at given z coordinate
    angle = 84.96
    upper_chord_1_nodes = []
    upper_chord_2_nodes = []

    for i in range(17):
        x = 185 * math.cos(math.radians(angle))
        y = 185 * math.sin(math.radians(angle)) - (185-18)
        node = Node(x, y, z)
        print(node.id)
        upper_chord_1_nodes.append(node)
        upper_chord_2_nodes.append(Node(x, y, z+6))
        angle += 1.44

    angle = 360/420 * 104
    lower_chord_nodes = []
    for i in range(17):
        x = 305 * math.cos(math.radians(angle)) + 11.5
        y = 305 * math.sin(math.radians(angle)) - (305-13)
        lower_chord_nodes.append(Node(x, y, z+3))
        angle += (360/420)

    elements = []

    # create two upper chords and one lower chord
    for i in range(len(upper_chord_1_nodes)-1):
        start_node_1 = upper_chord_1_nodes[i]
        end_node_1 = upper_chord_1_nodes[i+1]
        start_node_2 = upper_chord_2_nodes[i]
        end_node_2 = upper_chord_2_nodes[i+1]
        start_node_3 = lower_chord_nodes[i]
        end_node_3 = lower_chord_nodes[i+1]
        elements.extend([FrameElement(start_node_1, end_node_1, section, steel),
                         FrameElement(start_node_2, end_node_2, section, steel),
                         FrameElement(start_node_3, end_node_3, section, steel)])

    # create vertical and horizontal truss members
    for i in range(len(upper_chord_1_nodes)):
        start_node_1 = upper_chord_1_nodes[i]
        start_node_2 = upper_chord_2_nodes[i]
        start_node_3 = lower_chord_nodes[i]
        elements.extend([FrameElement(start_node_1, start_node_2, section, steel),
                         TrussElement(start_node_3, start_node_1, section, steel),
                         TrussElement(start_node_3, start_node_2, section, steel)])

    # create diagonal elements in first two bays
    for i in range(2):
        start_node_1 = upper_chord_1_nodes[i+1]
        start_node_2 = upper_chord_2_nodes[i+1]
        start_node_3 = lower_chord_nodes[i]
        elements.extend([TrussElement(start_node_3, start_node_1, section, steel),
                         TrussElement(start_node_3, start_node_2, section, steel)])

    half_range = math.trunc(len(upper_chord_1_nodes)/2)

    # create diagonal elements after first two bays and up to half span
    for i in range(2, half_range):
        start_node_1 = upper_chord_1_nodes[i]
        start_node_2 = upper_chord_2_nodes[i]
        start_node_3 = lower_chord_nodes[i+1]
        elements.extend([TrussElement(start_node_3, start_node_1, section, steel),
                         TrussElement(start_node_3, start_node_2, section, steel)])

    # create diagonal elements from half span to the end except last two bays
    for i in range(half_range, len(upper_chord_1_nodes)-3):
        start_node_1 = upper_chord_1_nodes[i+1]
        start_node_2 = upper_chord_2_nodes[i+1]
        start_node_3 = lower_chord_nodes[i]
        elements.extend([TrussElement(start_node_3, start_node_1, section, steel),
                         TrussElement(start_node_3, start_node_2, section, steel)])

    # create diagonal elements for last two bays
    for i in range(len(upper_chord_1_nodes)-3, len(upper_chord_1_nodes)-1):
        start_node_1 = upper_chord_1_nodes[i]
        start_node_2 = upper_chord_2_nodes[i]
        start_node_3 = lower_chord_nodes[i+1]
        elements.extend([TrussElement(start_node_3, start_node_1, section, steel),
                         TrussElement(start_node_3, start_node_2, section, steel)])

    return elements


def support_elements(x, y, z, nodes):
    # this function creates support consisting of four link member at given x,y,z and connecting four nodes
    elements = []
    node = Node(x, y, z)

    # support is hinged
    node.dof_1.restrained = True
    node.dof_2.restrained = True
    node.dof_3.restrained = True

    for i in range(4):
        elements.append(TrussElement(node, nodes[i], section_2, steel))
    return elements


elements = []
for i in range(0, 100, 20):
    elements += frame_truss(i)

# position of support
x1 = 305 * math.cos(math.radians(360/420 * (104+13))) + 11.5
x2 = 305 * math.cos(math.radians(360/420 * (104+3))) + 11.5
y = 0
z = 13

# create 4 elements for lower support
for i in range(4):
    node_1 = elements[36 + (131 * i) - 1].end_node
    node_2 = elements[42 + (131 * i) - 1].end_node
    node_3 = elements[36 + (131 * (i+1)) - 1].end_node
    node_4 = elements[42 + (131 * (i+1)) - 1].end_node
    elements += support_elements(x1, y, z, [node_1, node_2, node_3, node_4])
    z += 20

# create 4 elements for upper support
y = 5
z = 13
for i in range(4):
    node_1 = elements[6 + (131 * i) - 1].end_node
    node_2 = elements[12 + (131 * i) - 1].end_node
    node_3 = elements[6 + (131 * (i+1)) - 1].end_node
    node_4 = elements[12 + (131 * (i+1)) - 1].end_node
    elements += support_elements(x2, y, z, [node_1, node_2, node_3, node_4])
    z += 20

# create framed purlins
for i in range(17):
    for j in range(4):
        node_1 = elements[49+(131*j)-1 + (3*i)].end_node
        node_2 = elements[180+(131*j)-1 + (3*i)].start_node
        element = FrameElement(node_1, node_2, section_3, steel)
        elements.append(element)

# create structure object
structure = Structure(elements)

# assign loads to first truss upper chord in the z-direction
for j in range(17):
    structure.nodes[1 + (j*2)].dof_3.force = 200

Solver.analyze_first_order_elastic(structure)
Visualization.show_structure(structure)
Visualization.show_deformed_shape(structure, 10, 10)
Visualization.execute_qt()