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

SFDU record file. This is the core record for each block of the TRK 2-34 file,
which is a Standard Formatted Data Unit (SFDU)

Author: Dustin Buccino
Email: dustin.r.buccino@jpl.nasa.gov
Affiliation: Planetary Radar and Radio Sciences, Group 332K
             Jet Propulsion Laboratory, California Institute of Technology
Date Created: 23-SEP-2015
Last Modified: 14-SEP-2023

"""

from datetime import datetime, timedelta
from .util import bands, data_descriptions, format_codes
from .components import SFDULabel
from .components import SFDUAggCHDO
from .components import PrimaryCHDO
from .components import UplinkCHDO, DownlinkCHDO, DerivedCHDO, InferometricCHDO, FilteredCHDO
from .components import UplinkCarrierPhaseTrackingCHDO, DownlinkCarrierPhaseTrackingCHDO, UplinkSequentialRangingPhaseTrackingCHDO, DownlinkSequentialRangingPhaseTrackingCHDO, UplinkPnRangingPhaseTrackingCHDO, DownlinkPnRangingPhaseTrackingCHDO, DopplerCountTrackingCHDO, SequentialRangeTrackingCHDO, AngleTrackingCHDO, RampTrackingCHDO, VlbiCHDO, DrvidTrackingCHDO, SmoothedNoiseTrackingCHDO, AllanDeviationTrackingCHDO, PnRangeTrackingCHDO, ToneRangeTrackingCHDO, CarrierFrequencyObservableTrackingCHDO, TotalCountPhaseObservableTrackingCHDO

# ---------------------------------------------------------------------------
class SFDU:
   """
      Read/decode an SFDU
   """

   def __init__(self):
      """ class constructor """
      self.binarydata = ''
      self.number = 0
      self.label = SFDULabel()
      self.agg_chdo = SFDUAggCHDO()
      self.pri_chdo = PrimaryCHDO()
      self.sec_chdo = None
      self.trk_chdo = None
      self.is_decoded = False

   def __str__(self):
      """ print string """
      out = 'TRK2-34 SFDU[%i]:\n' % self.number
      out += 'SFDU_Label = {'
      out += '\n' + self.label.__str__()
      out += '}\nAggregation_CHDO = {'
      out += '\n' + self.agg_chdo.__str__()
      out += '}\nPrimary_CHDO = {'
      out += '\n' + self.pri_chdo.__str__()
      out += '}\nSecondary_CHDO = {'
      out += '\n' + self.sec_chdo.__str__()
      out += '}\nTracking_CHDO = {'
      out += '\n' + self.trk_chdo.__str__()
      out += '}'
      return out

   def timestamp(self):
      """ Return a timestamp (python datetime) of the SFDU """
      return datetime(year=self.sec_chdo.year, month=1, day=1) + \
                timedelta(days=self.sec_chdo.doy - 1, seconds=self.sec_chdo.sec )

   def last_modified(self):
      """ Return the python datetime this SFDU was last modified on """
      return datetime(year=1958, month=1, day=1) + \
                timedelta(days=self.sec_chdo.mod_day, milliseconds=self.sec_chdo.mod_msec)

   def tracking_mode(self):
      """ Return a string of the tracking mode (None, 1W, 2W, 3W/DSS, Invalid) """
      if self.label.data_description_id != 'C123':
         if self.sec_chdo.prdx_mode == 4:
            return 'Invalid'
         elif self.sec_chdo.prdx_mode == 3:
            return '3W/%i' % self.sec_chdo.ul_prdx_stn
         elif self.sec_chdo.prdx_mode == 2:
            return '2W'
         elif self.sec_chdo.prdx_mode == 1:
            return '1W'
         elif self.sec_chdo.prdx_mode == 0:
            return 'None'
      else:
         return 'N/A'

   def dss_id(self):
      """ Return a tuple of (uplink, downlink) DSS ID for the SFDU. """
      if hasattr( self.sec_chdo, 'ul_dss_id' ):
         uplink_id = self.sec_chdo.ul_dss_id
      else:
         uplink_id = 0
      if hasattr( self.sec_chdo, 'dl_dss_id' ):
         dnlink_id = self.sec_chdo.dl_dss_id
      else:
         dnlink_id = 0
      return ( uplink_id, dnlink_id )

   def radio_band(self):
      """ Return a tuple of (uplink, downlink) radiometric band (X,S,L,Ka,etc) """
      if hasattr( self.sec_chdo, 'ul_band' ):
         uplink_band = self.sec_chdo.ul_band
      else:
         uplink_band = 0
      if hasattr( self.sec_chdo, 'dl_band' ):
         dnlink_band = self.sec_chdo.dl_band
      else:
         dnlink_band = 0
      return ( bands[uplink_band], bands[dnlink_band] )

   def decode(self, binarystring, label=True, agg_chdo=True, pri_chdo=True, sec_chdo=True, trk_chdo=True):
      """ decode the SFDU binary string. only decode if the kwargs are True.
             (not decoding sec_chdo and trk_chdo saves lots of time if you only need the header """

      # Store binary data
      self.binarydata = binarystring

      # decode the label
      if label:
         self.label.decode( self.binarydata ) 
      if agg_chdo:
         self.agg_chdo.decode( self.binarydata )

      # decode the primary CHDO
      if pri_chdo:
         self.pri_chdo.decode( self.binarydata )

      # decode the secondary CHDO - first, deterimine the type, then decode
      if sec_chdo:
         if self.label.data_description_id == 'C123':
            self.sec_chdo = UplinkCHDO()
         elif self.label.data_description_id == 'C124':
            self.sec_chdo = DownlinkCHDO()
         elif self.label.data_description_id == 'C125':
            self.sec_chdo = DerivedCHDO()
         elif self.label.data_description_id == 'C126':
            self.sec_chdo = InferometricCHDO()
         elif self.label.data_description_id == 'C127':
            self.sec_chdo = FilteredCHDO()
         else:
            #raise RuntimeError("The secondary CHDO code %s cannot be decoded." % self.label.data_description_id + \
            #    "The TRK 2-34 file is likely corrupted")
            print( "SFDU %d: Warning: Unknown secondary CHDO type %s. Skipping..." % (self.number, self.label.data_description_id) )
            self.is_decoded = False
            return

         self.sec_chdo.decode( self.binarydata )

      # decode the tracking CHDO - first, determine the type, then decode
      if trk_chdo:
         if self.pri_chdo.format_code == 0:
            self.trk_chdo = UplinkCarrierPhaseTrackingCHDO()
         elif self.pri_chdo.format_code == 1:
            self.trk_chdo = DownlinkCarrierPhaseTrackingCHDO()
         elif self.pri_chdo.format_code == 2:
            self.trk_chdo = UplinkSequentialRangingPhaseTrackingCHDO()
         elif self.pri_chdo.format_code == 3:
            self.trk_chdo = DownlinkSequentialRangingPhaseTrackingCHDO()
         elif self.pri_chdo.format_code == 4:
            self.trk_chdo = UplinkPnRangingPhaseTrackingCHDO()
         elif self.pri_chdo.format_code == 5:
            self.trk_chdo = DownlinkPnRangingPhaseTrackingCHDO()
         elif self.pri_chdo.format_code == 6:
            self.trk_chdo = DopplerCountTrackingCHDO()
         elif self.pri_chdo.format_code == 7:
            self.trk_chdo = SequentialRangeTrackingCHDO()
         elif self.pri_chdo.format_code == 8:
            self.trk_chdo = AngleTrackingCHDO()
         elif self.pri_chdo.format_code == 9:
            self.trk_chdo = RampTrackingCHDO()
         elif self.pri_chdo.format_code == 10:
            self.trk_chdo = VlbiCHDO()
         elif self.pri_chdo.format_code == 11:
            self.trk_chdo = DrvidTrackingCHDO()
         elif self.pri_chdo.format_code == 12:
            self.trk_chdo = SmoothedNoiseTrackingCHDO()
         elif self.pri_chdo.format_code == 13:
            self.trk_chdo = AllanDeviationTrackingCHDO()
         elif self.pri_chdo.format_code == 14:
            self.trk_chdo = PnRangeTrackingCHDO()
         elif self.pri_chdo.format_code == 15:
            self.trk_chdo = ToneRangeTrackingCHDO()
         elif self.pri_chdo.format_code == 16:
            self.trk_chdo = CarrierFrequencyObservableTrackingCHDO()
         elif self.pri_chdo.format_code == 17:
            self.trk_chdo = TotalCountPhaseObservableTrackingCHDO()
         else:
            #raise RuntimeError("The trakcing CHDO code %i cannot be decoded." + \
            #    "The TRK 2-34 file is likely corrupted" % \
            #    self.pri_chdo.format_code )
            print( "SFDU %d: Warning: Unknown tracking CHDO type %i. Skipping..." % (self.number, self.pri_chdo.format_code) )
            self.is_decoded = False
            return

         self.trk_chdo.decode( self.binarydata )

      self.is_decoded = True
      
# ---------------------------------------------------------------------------
