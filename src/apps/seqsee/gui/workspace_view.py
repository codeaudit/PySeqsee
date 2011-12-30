from apps.seqsee.gui.viewport import ViewPort
from Tkinter import LAST

class WorkspaceView(ViewPort):
  def __init__(self, canvas, left, bottom, width, height):
    ViewPort.__init__(self, canvas, left, bottom, width, height)
    self.elements_y = height * 0.5
    self.min_gp_height = height * 0.2
    self.max_gp_height = height * 0.4

  def ReDrawView(self, controller):
    ws = controller.ws
    anchors_for_relations = dict()
    revealed_terms = [x.object.magnitude for x in ws.elements]
    space_per_element = self.width / (len(revealed_terms) + 1)
    for idx, element in enumerate(ws.elements):
      x, y = self.CanvasCoordinates((idx + 0.5) * space_per_element,
                                     self.elements_y)
      self.canvas.create_text(
          x, y, text='%d' % element.object.magnitude,
          font='-adobe-helvetica-bold-r-normal--28-140-100-100-p-105-iso8859-4',
          fill='#0000FF')
      anchors_for_relations[element] = (x, y - 20)

    relations_already_drawn = set()
    for element in ws.elements:
      for relation in element.relations:
        if relation not in relations_already_drawn:
          relations_already_drawn.add(relation)
          left_anchor = anchors_for_relations[relation.first]
          right_anchor = anchors_for_relations[relation.second]
          self.canvas.create_line(left_anchor[0], left_anchor[1],
                                  (left_anchor[0] + right_anchor[0]) / 2,
                                  left_anchor[1] - 35,
                                  right_anchor[0], right_anchor[1],
                                  fill='#00FF00', smooth=True, arrow=LAST, width=3.0)
