import numpy as np
import torch
import torch.nn as nn
import matplotlib.pyplot as plt
from math import pi
import argparse
import NEB_Methods
from NEB_Methods import SimpleString, SimpleNEB, plotPerformance

#We Define Our LEPS Potential
class LEPS(nn.Module):
    def __init__(self):
        super(LEPS, self).__init__()
        
    def Q(self, d, r ):
        alpha = 1.942
        r0 = 0.742
        return d*( 3*torch.exp(-2*alpha*(r-r0))/2 - torch.exp(-alpha*(r-r0)) )/2
               
    def J(self, d, r ):
        alpha = 1.942
        r0 = 0.742
        return d*( torch.exp(-2*alpha*(r-r0)) - 6*torch.exp(-alpha*(r-r0)) )/4
        
    def getEnergy(self, r):       
        """
        potential energy as a function of position
        for the LEPS potential on a line
        python version
        """
        x=r[:, 0]
        y=r[:, 1]
        a = 0.05
        b = 0.3
        c = 0.05
        dAB = 4.746
        dBC = 4.746
        dAC = 3.445

        rAB = x
        rBC = y
        rAC = rAB + rBC

        JABred = self.J(dAB, rAB)/(1+a)
        JBCred = self.J(dBC, rBC)/(1+b)
        JACred = self.J(dAC, rAC)/(1+c)
        
        final = self.Q(dAB, rAB)/(1+a) + \
               self.Q(dBC, rBC)/(1+b) + \
               self.Q(dAC, rAC)/(1+c) - \
               torch.sqrt( JABred*JABred + \
                           JBCred*JBCred + \
                           JACred*JACred - \
                           JABred*JBCred - \
                           JBCred*JACred - \
                           JABred*JACred )
        return final
    
    def forward(self, xyz):
        
        return self.getEnergy(xyz)

#The Following Are Hardcoded Variables Meant For NEB Simulations
r = [torch.linspace(0.3, 4.0, 60), torch.linspace(0.3, 4.0, 60)]
bounds = [0.3, 4.0, 0.3, 4.0]
ticks = [ [i/2 for i in range(1, 9)], [i/2 for i in range(1, 9)] ]
levels = 105
initial = torch.FloatTensor([0.75, 4])
final = torch.FloatTensor([4, 0.75])
potential = LEPS()
saddle = torch.FloatTensor([1.15, 0.85])
name = "LEPS"

#We Define The Behavior Of Our Simulation Based On User-Input
if (__name__ == '__main__'):
    
    parser = argparse.ArgumentParser(description = "The Parameters Of Our NEB Simulation")
    parser.add_argument('--images', default = 20, type=int)
    parser.add_argument('--k', default = 1.00, type=float)
    parser.add_argument('--mass', default = 1.00, type=float)
    parser.add_argument('--dt', default = 3e-2, type=float)
    parser.add_argument('--iterations', default = 150, type=int)
    parser.add_argument('-plotting', default = False, action = 'store_true')
    parser.add_argument('-last', default = False, action = 'store_true')
    parser.add_argument('-loss', default = False, action = 'store_true')
    parser.add_argument('-reaction', default = False, action = 'store_true')
    args = parser.parse_args()
    
    #We Define Our Elastic Band
    Band = SimpleString(initial, final, potential, args.images, args.k)
    #We Define Our Simulation And Performance Plot
    NEB = SimpleNEB(Band, levels, r, bounds, ticks, args.mass, args.dt, args.iterations, 
                    plotting = args.plotting, last = args.last, loss = args.loss, reaction = args.reaction)
    plotPerformance( NEB[0], 3, args.images, saddle, [levels, r, bounds, ticks, args.mass, args.dt, args.iterations], name )