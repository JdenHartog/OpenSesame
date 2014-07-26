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

from libqtopensesame.misc.base_component import base_component

class base_subcomponent(base_component):

	"""
	desc:
		A base class for all components that require an experiment and theme
		property.
	"""

	@property
	def experiment(self):

		"""
		returns:
			An experiment object.
		"""

		return self.main_window.experiment

	@property
	def theme(self):

		"""
		returns:
			A theme object.
		"""

		return self.main_window.theme

	@property
	def notify(self):

		"""
		returns:
			The notify function.
		"""

		return self.main_window.experiment.notify
