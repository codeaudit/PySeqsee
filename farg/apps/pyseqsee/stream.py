from _collections import defaultdict

from farg.apps.pyseqsee.categorization.categorizable import Categorizable
from farg.apps.pyseqsee.workspace import PSWorkspace
from farg.core.controller import Controller
from farg.core.history import History
from farg.core.util import ChooseAboutN
import farg.flags as farg_flags
class PSStream(object):
  def __init__(self, controller):
    self.controller = controller
    self.fringe_element_to_item_to_wt = defaultdict(lambda: defaultdict(float))
    self.last_focus_time = dict()


  def FocusOn(self, focusable, controller):
    fringe = focusable.GetFringe()
    # TODO(amahabal) This way, anything that was ever a fringe element of an item stays that way.
    # But this way is much cheaper than updating everything, and not super wrong...
    # When we choose an object based on fringe overlap, we can recalculate, if we wish...
    for fe, wt in fringe.items():
      self.fringe_element_to_item_to_wt[fe][focusable] = wt
    timestamp = controller.steps_taken
    self.last_focus_time[focusable] = timestamp
    actions = focusable.GetActions()
    prior_overlapping_foci = self.PriorFociWithSimilarFringe(current_focus=focusable,
                                                             timestamp=timestamp)
    if prior_overlapping_foci:
      actions.extend(focusable.GetRemindingBasedActions(prior_overlapping_foci))
      History.Note("In FocusOn: Prior overlapping foci seen")

    if actions:
      selected_actions = ChooseAboutN(2, [(x, x.urgency) for x in actions])
      History.Note("In FocusOn: Total of suggested actions", times=len(actions))
      History.Note("In FocusOn: Total of selected actions", times=len(selected_actions))
      for action in selected_actions:
        controller.coderack.AddCodelet(action,
                                       msg="While focusing on %s" % focusable.BriefLabel(),
                                       parents=())

  def PriorFociWithSimilarFringe(self, *, current_focus, timestamp,
                                 threshold=0.2, decay_factor=0.97):
    """Gets prior items with overlapping fringe."""
    scores = defaultdict(float)
    for fe, wt in current_focus.stored_fringe.items():
      for other_focusable, other_wt in self.fringe_element_to_item_to_wt[fe].items():
        if other_focusable is not current_focus:
          scores[other_focusable] += other_wt * wt
    out = []
    for other_focusable in scores.keys():
      age = max(0, timestamp - self.last_focus_time[other_focusable])
      scores[other_focusable] *= (decay_factor ** age)
      if scores[other_focusable] >= threshold:
        out.append((other_focusable, scores[other_focusable]))
    return sorted(out, reverse=True, key=lambda x: x[1])

class PSController(Controller):
  stream_class = PSStream
  workspace_class = PSWorkspace

  def __init__(self, get_input_from_flags=True, **args):
    Controller.__init__(self, **args)
    if get_input_from_flags:
      self.SetInput(farg_flags.FargFlags.sequence, farg_flags.FargFlags.unrevealed_terms)

  def SetInput(self, sequence, unrevealed_terms):
    self.workspace.InsertElements(sequence)
    self.unrevealed_terms = unrevealed_terms
