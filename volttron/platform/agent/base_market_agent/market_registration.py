# -*- coding: utf-8 -*- {{{
# vim: set fenc=utf-8 ft=python sw=4 ts=4 sts=4 et:

# Copyright (c) 2016, Battelle Memorial Institute
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in
#    the documentation and/or other materials provided with the
#    distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# The views and conclusions contained in the software and documentation
# are those of the authors and should not be interpreted as representing
# official policies, either expressed or implied, of the FreeBSD
# Project.
#
# This material was prepared as an account of work sponsored by an
# agency of the United States Government.  Neither the United States
# Government nor the United States Department of Energy, nor Battelle,
# nor any of their employees, nor any jurisdiction or organization that
# has cooperated in the development of these materials, makes any
# warranty, express or implied, or assumes any legal liability or
# responsibility for the accuracy, completeness, or usefulness or any
# information, apparatus, product, software, or process disclosed, or
# represents that its use would not infringe privately owned rights.
#
# Reference herein to any specific commercial product, process, or
# service by trade name, trademark, manufacturer, or otherwise does not
# necessarily constitute or imply its endorsement, recommendation, or
# favoring by the United States Government or any agency thereof, or
# Battelle Memorial Institute. The views and opinions of authors
# expressed herein do not necessarily state or reflect those of the
# United States Government or any agency thereof.
#
# PACIFIC NORTHWEST NATIONAL LABORATORY
# operated by BATTELLE for the UNITED STATES DEPARTMENT OF ENERGY
# under Contract DE-AC05-76RL01830

# }}}

class MarketRegistration(object):
    def __init__(self, market_name, buyer_seller, reservation_callback, offer_callback,
                 aggregate_callback, price_callback, error_callback):
        self.market_name = market_name
        self.buyer_seller = buyer_seller
        self.reservation_callback = reservation_callback
        self.offer_callback = offer_callback
        self.aggregate_callback = aggregate_callback
        self.price_callback = price_callback
        self.error_callback = error_callback
        self.always_wants_reservation = self.reservation_callback == None
        self.has_reservation = False
        self._validate_callbacks()

    def _validate_callbacks(self):
        if self.offer_callback is None and self.aggregate_callback is None:
            raise TypeError('You must provide either an offer callback or an aggregate callback.')
        if self.offer_callback is not None and self.aggregate_callback is not None:
            raise TypeError('You must only provide an offer callback or an aggregate callback, but not both.')

    def request_reservations(self, timestamp, agent):
        self.has_reservation = False
        if self.reservation_callback is not None:
            wants_reservation_this_time = self.reservation_callback(timestamp, self.market_name, self.buyer_seller)
        else:
            wants_reservation_this_time = self.always_wants_reservation
        if wants_reservation_this_time:
            agent.make_reservation(self.market_name, self.buyer_seller)
            self.has_reservation = True

    def request_offers(self, timestamp, agent):
        if self.has_reservation and self.offer_callback is not None:
            curve = self.offer_callback(timestamp, self.market_name, self.buyer_seller)
            if curve is not None:
                agent.make_offer(self.market_name, self.buyer_seller, curve)

    def report_clear_price(self, timestamp, price, quantity):
        if self.has_reservation and self.price_callback is not None:
            self.price_callback(timestamp, self.market_name, self.buyer_seller, price, quantity)
        self.has_reservation = False

    def report_aggregate(self, timestamp, aggregate_curve):
        if self.has_reservation and self.aggregate_callback is not None:
            self.aggregate_callback(timestamp, self.market_name, self.buyer_seller, aggregate_curve)

    def report_error(self, timestamp, error_message):
        if self.error_callback is not None:
            self.error_callback(timestamp, self.market_name, self.buyer_seller, error_message)




