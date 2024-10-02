#!/usr/bin/python3
# Copyright (c) 2023, California Institute of Technology ("Caltech").
# U.S. Government sponsorship acknowledged. Any commercial use must be 
# negotiated with the Office of Technology Transfer at the California 
# Institute of Technology.
# 
# This software may be subject to U.S. export control laws. By accepting this 
# software, the user agrees to comply with all applicable U.S. export laws 
# and regulations. User has the responsibility to obtain export licenses, or 
# other export authority as may be required before exporting such information 
# to foreign countries or providing access to foreign persons.
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice,
#   this list of conditions and the following disclaimer.
# * Redistributions must reproduce the above copyright notice, this list of
#   conditions and the following disclaimer in the documentation and/or other
#   materials provided with the distribution.
# * Neither the name of Caltech nor its operating division, the Jet Propulsion
#   Laboratory, nor the names of its contributors may be used to endorse or
#   promote products derived from this software without specific prior written
#   permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
"""
TRK234: A module to read TRK 2-34 files

reader file. Contains the core Reader class to read an SFDU.

Author: Dustin Buccino
Email: dustin.r.buccino@jpl.nasa.gov
Affiliation: Planetary Radar and Radio Sciences, Group 332K
             Jet Propulsion Laboratory, California Institute of Technology
Date Created: 23-SEP-2015
Last Modified: 14-SEP-2023

"""

from .ProgressDisplay import ProgressDisplay
from .SFDU import SFDU
import re
import struct

# ---------------------------------------------------------------------------
class Reader:
   """
      Main class to read a TRK 2-34 file

      f = TRK234.Reader(filename)
   """

   # search string
   STARTPACKET = 'NJPL'

   def __init__(self, filename):
      """ class constructor """

      # set basic attributes
      self.filename = filename.split('/')[-1]
      self.sfdu_list = []
      self.is_decoded = False
      
      # read the data and determine the index
      self.binarydata = self.read( filename )
      self.index = self.sfdu_index( self.binarydata )

   def decode(self, progress=False, label=True, agg_chdo=True, pri_chdo=True, sec_chdo=True, trk_chdo=True):
      """ return the SFDUs, processed in SFDU class
            decode based on the function inputs (default=decode all)
      """

      # initialize variable
      sfdus = []

      # want the sfdu index to be one size larger for the loop
      ind = self.index
      #ind.append( len(self.binarydata)+1 )

      # separate out the binary blocks and decode the SFDU
      n = len(ind) - 1
      if progress: p = ProgressDisplay(maxIndex=n)
      for i in range( n ):
         sfdu = SFDU()
         sfdu.number = i
         sfdu.decode( self.binarydata[ ind[i]:ind[i+1] ], label, agg_chdo, pri_chdo, sec_chdo, trk_chdo )
         sfdus.append( sfdu )
         if progress: p.update(i)
      if progress: p.kill()

      self.sfdu_list = sfdus
      self.is_decoded = True
#      return sfdus

   def dump(self):
      """ dump the contents of this TRK 2-34 file to window """
      for s in self.sfdus:
         print( s )

   def read(self, filename):
      """ read the SFDU file and return the binary data """

      # read the file
      with open(filename, 'rb') as f:
          binarydata = f.read()

      # return the binary data
      return binarydata

   def sfdu_index(self, binarystring):
      """ decode binary SFDU string into the start indexes of each SFDU """
      # NJPL search method
      #return [ m.start() for m in re.finditer(self.STARTPACKET, binarystring) ]

      N = len(self.binarydata)
      ind = [0]
      next_ind = 0
      offset = 0
      while(next_ind < N):
         # sfdu_length attribute in "label"
         sfdu_length = struct.unpack('>Q', self.binarydata[offset+12:offset+20])[0]
         next_ind = sfdu_length + 20 + ind[-1]
         offset = next_ind
         ind.append(next_ind)
      return ind

   def get_data_types(self):
      """ decode ONLY the data type from the SFDU and return them """

      # pretty much the same looping code as above from decode(),
      #   but manually unpack the format code, which is blocks 31:32
      j = self.sfdu_index( self.binarydata )
      #j.append( len(self.binarydata)+1 )
      fc = []
      for i in range( len(j)-1 ):
         fc.append( struct.unpack('>B', self.binarydata[ j[i]:j[i+1] ][31:32])[0] )
      return fc

# ---------------------------------------------------------------------------
