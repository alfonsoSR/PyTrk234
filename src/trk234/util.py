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

utilities file. Contains useful id mappings and functions that help when
processing and using TRK 2-34 files.

Author: Dustin Buccino
Email: dustin.r.buccino@jpl.nasa.gov
Affiliation: Planetary Radar and Radio Sciences, Group 332K
             Jet Propulsion Laboratory, California Institute of Technology
Date Created: 23-SEP-2015
Last Modified: 14-SEP-2023

"""

# dict to decode the data description field
data_descriptions = {
   'C123' : 'Uplink types',
   'C124' : 'Downlink types',
   'C125' : 'Derived types',
   'C126' : 'Inferometric types',
   'C127' : 'Filtered types',
}

# dict to decode the format code
format_codes = {
    0 : 'Uplink Carrier Phase',
    1 : 'Downlink Carrier Phase',
    2 : 'Uplink Sequential Ranging Phase',
    3 : 'Downlink Sequential Ranging Phase',
    4 : 'Uplink PN Ranging Phase',
    5 : 'Downlink PN Ranging Phase',
    6 : 'Doppler',
    7 : 'Sequential Ranging',
    8 : 'Angles',
    9 : 'Ramps',
   10 : 'VLBI',
   11 : 'DRVID',
   12 : 'Smoothed Noise',
   13 : 'Allan Deviation',
   14 : 'PN Ranging',
   15 : 'Tone Ranging',
   16 : 'Carrier Observable',
   17 : 'Total Phase Observable',
}

# dict to decode the band
bands = {
   0 : 'Unknown',
   1 : 'S',
   2 : 'X',
   3 : 'Ka',
   4 : 'Ku',
   5 : 'L',
}

# ---------------------------------------------------------------------------
def types(sfdu_list):
   """ return the number of each type of SFDU (0-17) """

   # Loop through each type and determine the number
   n = []
   for i in range(0,18):
      n.append( len([ s for s in sfdu_list if s.pri_chdo.format_code == i ]) )
   
   # return a list whose index corresponds to the data type
   return n
# ---------------------------------------------------------------------------
