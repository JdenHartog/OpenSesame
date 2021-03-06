#-*- coding:utf-8 -*-

"""
This file is part of OpenSesame.

OpenSesame is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

OpenSesame is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with OpenSesame.  If not, see <http://www.gnu.org/licenses/>.
"""

from libopensesame.exceptions import osexception
from libopensesame import item, debug
from libopensesame.py3compat import *
import openexp.keyboard
from random import *
from math import *

class loop(item.item):

	"""A loop item runs a single other item multiple times"""

	description = u'Repeatedly runs another item'

	def reset(self):

		"""See item."""

		self.var.cycles = 1
		self.var.repeat = 1
		self.var.skip = 0
		self.var.offset = u'no'
		self.matrix = {}
		self.var.order = u'random'
		self.var.item = u''
		self.var.break_if = u'never'

	def from_string(self, string):

		"""
		Creates a loop from a definition in a string.

		Arguments:
		string 		--	An item definition string.
		"""

		self.variables = {}
		self.comments = []
		self.reset()
		if string is None:
			return
		for i in string.split(u'\n'):
			self.parse_variable(i)
			# Extract the item to run
			i = self.syntax.split(i.strip())
			if len(i) > 0:
				if i[0] == u'run' and len(i) > 1:
					self.var.item = i[1]
				if i[0] == u'setcycle' and len(i) > 3:
					cycle = int(i[1])
					var = i[2]
					val = i[3]
					try:
						if int(val) == float(val):
							val = int(val)
						else:
							val = float(val)
					except:
						pass
					if cycle not in self.matrix:
						self.matrix[cycle] = {}
					self.matrix[cycle][var] = val

	def run(self):

		"""Runs the loop."""

		self.set_item_onset()

		# Prepare the break if condition
		if self.var.break_if != u'':
			self._break_if = self.syntax.compile_cond(
				self.var.get(u'break_if', _eval=False))
		else:
			self._break_if = None

		# First generate a list of cycle numbers
		l = []
		# Walk through all complete repeats
		whole_repeats = int(self.var.repeat)
		for j in range(whole_repeats):
			for i in range(self.var.cycles):
				l.append(i)

		# Add the leftover repeats
		partial_repeats = self.var.repeat - whole_repeats
		if partial_repeats > 0:
			all_cycles = range(self.var.cycles)
			_sample = sample(all_cycles, int(len(all_cycles) * partial_repeats))
			for i in _sample:
				l.append(i)

		# Randomize the list if necessary
		if self.var.order == u'random':
			shuffle(l)

		# In sequential order, the offset and the skip are relevant
		else:
			if len(l) < self.var.skip:
				raise osexception( \
					u'The value of skip is too high in loop item "%s":: You cannot skip more cycles than there are.' \
					% self.name)
			if self.var.offset == u'yes':
				l = l[self.var.skip:] + l[:self.var.skip]
			else:
				l = l[self.var.skip:]

		# Create a keyboard to flush responses between cycles
		self._keyboard = openexp.keyboard.keyboard(self.experiment)

		# Make sure the item to run exists
		if self.var.item not in self.experiment.items:
			raise osexception( \
				u"Could not find item '%s', which is called by loop item '%s'" \
				% (self.var.item, self.name))

		# And run!
		while len(l) > 0:
			cycle = l.pop(0)
			self.apply_cycle(cycle)
			if self._break_if is not None and \
				self.python_workspace._eval(self._break_if):
				break
			self.experiment.var.repeat_cycle = 0
			self.experiment.items.execute(self.var.item)
			if self.experiment.var.repeat_cycle:
				debug.msg(u'repeating cycle %d' % cycle)
				l.append(cycle)
				if self.var.order == u'random':
					shuffle(l)

	def apply_cycle(self, cycle):

		"""
		Sets all the loop variables according to the cycle.

		Arguments:
		cycle 		--	The cycle nr.
		"""

		# If the cycle is not defined, we don't have to do anything
		if cycle not in self.matrix:
			return
		# Otherwise apply all variables from the cycle
		for var in self.matrix[cycle]:
			val = self.matrix[cycle][var]
			# By starting with an "=" sign, users can incorporate a
			# Python statement, for example to call functions from
			# the random or math module
			if isinstance(val, basestring) and len(val) > 1 and val[0] == "=":
				try:
					val = eval(val[1:])
				except Exception as e:
					raise osexception( \
						u"Failed to evaluate '%s' in loop item '%s': %s" \
						% (val[1:], self.name, e))
			# Set it!
			self.experiment.var.set(var, val)

	def to_string(self):

		"""
		Creates a definition string for the loop.

		Returns:
		A definition string.
		"""

		s = super(loop, self).to_string()
		for i in self.matrix:
			for var in self.matrix[i]:
				s += u'\tsetcycle %d %s "%s"\n' % (i, var, self.matrix[i][var])
		s += u'\trun %s\n' % self.var.item
		return s

	def var_info(self):

		"""
		Describes the variables specific to the loop.

		Returns:
		A list of (variable name, description) tuples.
		"""

		l = item.item.var_info(self)
		var_list = {}
		for i in self.matrix:
			for var in self.matrix[i]:
				if var not in var_list:
					var_list[var] = []
				var_list[var].append(safe_decode(self.matrix[i][var]))
		for var in var_list:
			l.append( (var, u'[' + u', '.join(var_list[var]) + u']'))
		return l
