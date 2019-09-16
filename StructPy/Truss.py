from StructPy import structural_classes as sc
from StructPy import cross_sections as xs
from StructPy import materials as ma
import numpy as np
import logging


class TrussNode(sc.Node):

	fixities = {   # x, y
		'free'   :  (1.0, 1.0),
		'pin'    :  (0.0, 0.0),
		'roller' :  (1.0, 0.0),
		'yroller':  (0.0, 1.0),
	}
	
	def __init__(self, x, y, n=None, cost=0, fixity='free'):
		self.x = x
		self.y = y
		self.cost = cost
		self.n = n
		self.fixity = fixity
		
		try:
			self.xfix, self.yfix = self.__class__.fixities[fixity]
		except KeyError:
			self.invalidFixityError()

class TrussMember(sc.Member):
	"""
	Define Truss Member class. Only allows axial loading.
	"""
	
	nDoFPerNode = 2
	
	@property
	def k(self):
		"""Local member stiffness matrix"""

		a = (self.cross.A * self.material.E)/self.length
		
		return a * np.array([
			[1, -1],
			[-1, 1]
		])
	
	@property
	def T(self):
		"""Local to global transformation matrix"""
		l = self.unVec[0]
		m = self.unVec[1]
		return np.array([
			[l, m, 0, 0],
			[0, 0, l, m]
		])


class Truss(sc.Structure):	
	"""This class builds on the structure class adding truss methods"""
	
	#Number of degrees of freedom for this structure type in the global coordinate system
	whatDoF = ['x', 'y']
	nDoFPerNode = len(whatDoF)
	MemberType = TrussMember
	NodeType = TrussNode
	
	def directStiffness(self, loading):
		"""This executes the direct stiffness method"""
		
		self.isStable()
		globalD = self.solve(loading)
				
		for i, node in enumerate(self.nodes):
			node.xdef = globalD[2*node.n]
			node.ydef = globalD[2*node.n + 1]
		
		for i, member in enumerate(self.members):
			
			l = member.unVec[0]
			m = member.unVec[1]
			
			ind = member.DoF
			A = member.cross.A
			E = member.material.E
			L = member.length
			
			member.axial = (A*E)/L * np.array([l, m, -l, -m]) @ np.array(globalD[ind]).T
			
		return globalD
		