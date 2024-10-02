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

info file. Contains the Info class, which summarizes the contents of a 
TRK 2-34 file.

Author: Dustin Buccino
Email: dustin.r.buccino@jpl.nasa.gov
Affiliation: Planetary Radar and Radio Sciences, Group 332K
             Jet Propulsion Laboratory, California Institute of Technology
Date Created: 23-SEP-2015
Last Modified: 14-SEP-2023

"""
from .SFDU import SFDU
from .Reader import Reader
from .util import bands, format_codes, data_descriptions, types
from datetime import datetime
import struct

# ---------------------------------------------------------------------------
class Info:
   """Get information about a TRK 2-34 file.
   
   Parses data from a TRK 2-34 file `Reader` instance to provide a summary 
   of information about a TRK 2-34 file. Sample parsed fields include start 
   time, end time, spacecraft ID, type of data (which SFDU types), uplink 
   band, downlink band, uplink station, downlink station, and tracking 
   modes.
   
   Does not parse from the Tracking CHDO portion of an SFDU.
   
   """

   def __init__(self, f, quicklook=False):
      """Initialize the `Info` class. Accepts a `Reader` instance as
      an input.
      """

      # get SFDU list
      if isinstance(f,Reader) and not quicklook:
         if not f.is_decoded:
            f.decode(trk_chdo=False)
      else:
         TypeError('Invalid input to trk234.Info')

      # initalize class variables
      self.numRecords = 0
      """Integer number of records"""
      self.dataTypes = []
      """`list` of unique data types"""
      self.numberDataTypes = []
      """`list` of the count of each type of data"""
      self.startTime = None
      """`datetime` of the earliest record in the file"""
      self.endTime = None
      """`datetime` of the latest record in the file"""
      self.lastModified = None
      """`datetime` of when the file was last modified"""
      self.spacecraftId = []
      """`list` of all spacecraft ID numbers"""
      self.dnlinkDssId = []
      """`list` of all DSN station ID numbers with downlink data"""
      self.uplinkDssId = []
      """`list` of all DSN station ID numbers with uplink data"""
      self.dnlinkBand = []
      """`list` of all downlink bands"""
      self.uplinkBand = []
      """`list` of all uplink bands"""
      self.trackingMode = []
      """`list` of each tracking mode type (e.g. 1W, 2W, 3W/NN)"""
      self.dataDescriptionIds = []
      """`list` of the unique Data Description IDs"""
      self.dopplerCountTime = []
      """`list` of the unique Doppler count times in the Secondary CHDO"""

      # get the info
      if quicklook:
         print( "Running `quicklook` algorithm. This algorithm is fast, but is not as detailed/accurate as the default..." )
         self.quicklook(f)
      else:
         self.get_info(f)
      
      self.filename = f.filename
      """Name of the file"""

   def __str__(self):
      """Return a string containing a summary of the information parsed."""

      # sub function to make things a little cleaner
      lprint = lambda x, y: '%24s: %s\n' % (x, y)
      liststr = lambda x: ', '.join(map(str, x))

      # Create the output string
      out  = ''
      out += lprint('Report for File', self.filename )
      out += lprint('Generation Date', datetime.now().strftime('%Y-%jT%H:%M:%S') )
      out += lprint('Start Time', self.startTime.strftime('%Y-%jT%H:%M:%S') )
      out += lprint('End Time', self.endTime.strftime('%Y-%jT%H:%M:%S') )
      out += lprint('Spacecraft ID', liststr(self.spacecraftId) )
      out += lprint('Downlink DSS ID', liststr(self.dnlinkDssId) )
      out += lprint('Downlink Bands', liststr(self.dnlinkBand) )
      out += lprint('Doppler Count Time', liststr(self.dopplerCountTime) )
      out += lprint('Uplink DSS ID', liststr(self.uplinkDssId) )
      out += lprint('Uplink Bands', liststr(self.uplinkBand) )
      out += lprint('Tracking Mode', liststr(self.trackingMode) )
      out += lprint('Number of Records', self.numRecords )
      out += lprint('Data Description IDs', liststr(self.dataDescriptionIds) )
      out += lprint('Available Data Types', liststr(self.dataTypes) )
      for x in self.dataTypes:
         out += lprint('%02i' % x, '%s - %i' % (format_codes[x], self.numberDataTypes[x]) )
      return out

   def get_info(self, f):
      """Parse the information from the `Reader` class, containing SFDUs in the 
      `Reader.sfdu_list` attribute.
      
      Populates the attributes in `__init__`"""

      # Number of records
      self.numRecords = len(f.sfdu_list)

      # Get the types and number of types
      self.numberDataTypes = types(f.sfdu_list)
      self.dataTypes = [ i for i, e in enumerate( self.numberDataTypes ) if e != 0 ]

      # Compute the time of the first SFDU and last SFDU
      dt = [ x.timestamp() for x in f.sfdu_list if x.is_decoded ]
      self.startTime = min(dt)
      self.endTime = max(dt)

      # Get the last modified date
      dtm = [ x.last_modified() for x in f.sfdu_list if x.is_decoded ]
      self.lastModified = max(dtm)

      # Get the Spacecraft ID(s)
      self.spacecraftId = list(set([ x.sec_chdo.scft_id for x in f.sfdu_list if x.is_decoded ]))

      # Get all data description IDs
      self.dataDescriptionIds = list(set( [ x.label.data_description_id for x in f.sfdu_list ] ))

      # A more complicated loop to find the uplink/downlink bands, DSS IDs, and modes
      #   strategy: create a list of all bands/IDs and then find unique vals 
      #   in each list
      ul_dss_id = []
      dl_dss_id = []
      ul_band = []
      dl_band = []
      trk_mode = []
      loop_bw = []
      for x in f.sfdu_list:
         if x.label.data_description_id == 'C123': # uplink
            ul_dss_id.append( x.sec_chdo.ul_dss_id )
            ul_band.append( x.sec_chdo.ul_band )
         elif x.label.data_description_id == 'C124': # downlink
            dl_dss_id.append( x.sec_chdo.dl_dss_id )
            dl_band.append( x.sec_chdo.dl_band )
            trk_mode.append( x.tracking_mode() )
         elif x.label.data_description_id == 'C125': # derived
#            ul_dss_id.append( x.sec_chdo.ul_dss_id )
            dl_dss_id.append( x.sec_chdo.dl_dss_id )
#            dl_band.append( x.sec_chdo.dl_band )
#            ul_band.append( x.sec_chdo.ul_band )
            trk_mode.append( x.tracking_mode() )
         elif x.label.data_description_id == 'C126': # VLBI
            ul_dss_id.append( x.sec_chdo.ul_dss_id )
            dl_dss_id.append( x.sec_chdo.dl_dss_id )
            dl_dss_id.append( x.sec_chdo.dl_dss_id_2 )
            dl_band.append( x.sec_chdo.dl_band )
            ul_band.append( x.sec_chdo.ul_band )
            trk_mode.append( x.tracking_mode() )
         elif x.label.data_description_id == 'C127': # filtered
            dl_dss_id.append( x.sec_chdo.dl_dss_id )
            dl_band.append( x.sec_chdo.dl_band )
            trk_mode.append( x.tracking_mode() )

      self.dnlinkDssId = list(set( dl_dss_id ))
      self.uplinkDssId = list(set( ul_dss_id ))
      self.dnlinkBand = [ bands[i] for i in list(set( dl_band )) ]
      self.uplinkBand = [ bands[i] for i in list(set( ul_band )) ]
      self.trackingMode = list(set( trk_mode ))

      # Get doppler count time
      self.dopplerCountTime = list(set( x.sec_chdo.cnt_time for x in f.sfdu_list if x.pri_chdo.format_code == 16 ))

   def quicklook(self, f):
      """ do a quick look at the file to determine a subset of metadata.
          this function bascially does almost the same thing as above, but
          manually. its faster but not as maintainable.
      """

      # Number of records, format codes, and data types. copied from above and trk234.util
      print( "Getting data type list..." )
      self.numRecords = len(f.index)-1
      format_codes = f.get_data_types()
      n = []
      for i in range(0,18):
         n.append( len([ s for s in format_codes if s==i ]) )
      self.numberDataTypes = n
      self.dataTypes = [ i for i, e in enumerate( self.numberDataTypes ) if e != 0 ]

      # Find a list of DSN station IDs
      print( "Getting DSS information..." )
      dl_dss_id = []
      dl_band = []
      data_description_id = []
      ul_dss_id = []
      ul_band = []
      prdx_mode = []
      for i in range(len(f.index)-1):
         bindata = f.binarydata[ f.index[i]:f.index[i+1] ]
         ddid = struct.unpack('>4s', bindata[8:12])[0].decode('ascii')
         data_description_id.append( ddid )
         if ddid == 'C124':
            dl_dss_id.append( struct.unpack('>B', bindata[66:67])[0] )
            dl_band.append( struct.unpack('>B', bindata[67:68])[0] )
            prdx_mode.append( struct.unpack('>B', bindata[69:70])[0] )
         if ddid == 'C123':
            ul_dss_id.append( struct.unpack('>B', bindata[66:67])[0] )
            ul_band.append( struct.unpack('>B', bindata[67:68])[0] )
      self.dataDescriptionIds = list(set( data_description_id ))
      self.dnlinkDssId = list(set( dl_dss_id ))
      self.uplinkDssId = list(set( ul_dss_id ))
      self.dnlinkBand = [ bands[i] for i in list(set( dl_band )) ]
      self.uplinkBand = [ bands[i] for i in list(set( ul_band )) ]
      self.trackingMode = [ '%1dW'%x for x in list(set( prdx_mode )) if x in [1,2,3] ]

      # decode the first and last SFDU
      print( "Getting timestamps..." )
      start = SFDU()
      start.decode(f.binarydata[f.index[0]:f.index[1]])
      end = SFDU()
      end.decode(f.binarydata[f.index[-2]:f.index[-1]])

      # Get the essential metadata from the first and last SFDU
      self.startTime = start.timestamp()
      self.endTime = end.timestamp()
      self.lastModified = end.timestamp()
      self.spacecraftId = [start.sec_chdo.scft_id]

# ---------------------------------------------------------------------------
