# Copyright (C) 2020 University of Glasgow
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import ietfdata.datatracker as DT
import requests_cache

import sqlite3

from typing import Iterator, Optional

class DataTrackerCollector:
    def __init__(self, use_cache=False):
        self.dt = DT.DataTracker()
        self.conn = sqlite3.connect('ietfdata.db')
        self.create_tables()
        if use_cache:
            requests_cache.install_cache("dt_collector_cache")


    def gather_person(self, person: DT.Person):
        try:
            self.conn.execute("INSERT OR REPLACE INTO person VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                            (person.id,
                             person.name,
                             person.name_from_draft,
                             person.ascii,
                             person.ascii_short,
                             person.user,
                             person.time,
                             person.photo,
                             person.photo_thumb,
                             person.biography,
                             person.consent))
            self.conn.commit()
        except Exception as e:
            print("Did not add data about person ID %d [%s]" % (person.id, e))


    def gather_aliases(self, person: DT.Person):
        for alias in self.dt.person_aliases(person):
            try:
                self.conn.execute("INSERT OR REPLACE INTO alias VALUES (?, ?, ?)",
                                 (alias.id,
                                  person.id,
                                  alias.name))
                self.conn.commit()
            except Exception as e:
                print(e)
                print("Did not add alias for person ID %d [%s]" % (person.id, e))


    def gather_emails(self, person: DT.Person):
        for email in self.dt.email_for_person(person):
            try:
                self.conn.execute("INSERT OR REPLACE INTO email VALUES (?, ?, ?, ?, ?, ?)",
                                 (person.id,
                                  email.address,
                                  email.time,
                                  email.origin,
                                  email.primary,
                                  email.active))
                self.conn.commit()
            except Exception as e:
                print(e)
                print("Did not add email data for person ID %d [%s]" % (person.id, e))


    def gather_historical_emails(self, person: DT.Person):
        for historical_email in self.dt.email_history_for_person(person):
            try:
                self.conn.execute("INSERT OR REPLACE INTO historical_email VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                                 (person.id,
                                  historical_email.address,
                                  historical_email.time,
                                  historical_email.origin,
                                  historical_email.primary,
                                  historical_email.active,
                                  historical_email.history_change_reason,
                                  historical_email.history_user,
                                  historical_email.history_id,
                                  historical_email.history_type,
                                  historical_email.history_date))
                self.conn.commit()
            except Exception as e:
                print(e)
                print("Did not add historical email data for person ID %d [%s]" % (person.id, e))


    def gather_historical_people(self, person: DT.Person):
        for historical_person in self.dt.person_history(person):
            try:
                self.conn.execute("INSERT OR REPLACE INTO historical_person VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                                 (person.id,
                                  historical_person.name,
                                  historical_person.name_from_draft,
                                  historical_person.ascii,
                                  historical_person.ascii_short,
                                  historical_person.user,
                                  historical_person.time,
                                  historical_person.photo,
                                  historical_person.photo_thumb,
                                  historical_person.biography,
                                  historical_person.consent,
                                  historical_person.history_change_reason,
                                  historical_person.history_user,
                                  historical_person.history_id,
                                  historical_person.history_type,
                                  historical_person.history_date))
                self.conn.commit()
            except Exception as e:
                print(e)
                print("Did not add historical person data for person ID %d [%s]" % (person.id, e))


    def gather_person_events(self, person: DT.Person):
        for person_event in self.dt.person_events(person):
            try:
                self.conn.execute("INSERT OR REPLACE INTO person_events VALUES (?, ?, ?, ?, ?)",
                                 (person_event.desc,
                                  person_event.id,
                                  person.id,
                                  person_event.time,
                                  person_event.type))
                self.conn.commit()
            except Exception as e:
                print(e)
                print("Did not add person event for person ID %d [%s]" % (person.id, e))


    def gather_people(self):
        for person in self.dt.people():
            print("Gathering data for %d.." % person.id)
            self.gather_person(person)
            self.gather_aliases(person)
            self.gather_emails(person)
            self.gather_historical_emails(person)
            self.gather_historical_people(person)
            self.gather_person_events(person)


    def create_tables(self):
        # Person
        self.conn.execute('''CREATE TABLE IF NOT EXISTS person (id              int  NOT NULL PRIMARY KEY,
                                                                name            text NOT NULL,
                                                                name_from_draft text NOT NULL,
                                                                ascii           text NOT NULL,
                                                                ascii_short     text,
                                                                user            text NOT NULL,
                                                                time            text NOT NULL,
                                                                photo           text NOT NULL,
                                                                photo_thumb     text NOT NULL,
                                                                biography       text NOT NULL,
                                                                consent         bool NOT NULL)''')

        # Alias
        self.conn.execute('''CREATE TABLE IF NOT EXISTS alias (id     int  NOT NULL PRIMARY KEY,
                                                               person int  NOT NULL,
                                                               name   text NOT NULL,
                                                               FOREIGN KEY (person) REFERENCES person(id))''')


        # Email
        self.conn.execute('''CREATE TABLE IF NOT EXISTS email (person     int  NOT NULL,
                                                               address    text NOT NULL PRIMARY KEY,
                                                               time       text NOT NULL,
                                                               origin     text NOT NULL,
                                                               is_primary bool NOT NULL,
                                                               active     bool NOT NULL,
                                                               FOREIGN KEY (person) REFERENCES person(id))''')

        # HistoricalEmail
        self.conn.execute('''CREATE TABLE IF NOT EXISTS historical_email (person                int  NOT NULL,
                                                                          address               text NOT NULL,
                                                                          time                  text NOT NULL,
                                                                          origin                text NOT NULL,
                                                                          is_primary            bool NOT NULL,
                                                                          active                bool NOT NULL,
                                                                          history_change_reason text,
                                                                          history_user          text,
                                                                          history_id            int  NOT NULL PRIMARY KEY,
                                                                          history_type          text NOT NULL,
                                                                          history_date          text NOT NULL,
                                                                          FOREIGN KEY (person) REFERENCES person(id))''')

        # HistoricalPerson
        self.conn.execute('''CREATE TABLE IF NOT EXISTS historical_person (id                    int  NOT NULL,
                                                                           name                  text NOT NULL,
                                                                           name_from_draft       text NOT NULL,
                                                                           ascii                 text NOT NULL,
                                                                           ascii_short           text,
                                                                           user                  text NOT NULL,
                                                                           time                  text NOT NULL,
                                                                           photo                 text NOT NULL,
                                                                           photo_thumb           text NOT NULL,
                                                                           biography             text NOT NULL,
                                                                           consent               bool NOT NULL,
                                                                           history_change_reason text,
                                                                           history_user          text,
                                                                           history_id            int  NOT NULL PRIMARY KEY,
                                                                           history_type          text NOT NULL,
                                                                           history_date          text NOT NULL,
                                                                           FOREIGN KEY (id) REFERENCES person(id))''')

        # PersonEvent
        self.conn.execute('''CREATE TABLE IF NOT EXISTS person_events (desc   text NOT NULL,
                                                                       id     int  NOT NULL PRIMARY KEY,
                                                                       person int  NOT NULL,
                                                                       time   text NOT NULL,
                                                                       type   text NOT NULL,
                                                                       FOREIGN KEY (person) REFERENCES person(id))''')


    def gather(self):
        self.gather_people()
        self.conn.close()


if __name__ == "__main__":
    collector = DataTrackerCollector(use_cache=True)
    collector.gather()
