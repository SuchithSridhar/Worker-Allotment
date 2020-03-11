import csv
import pickle
import random
from pprint import pprint as pp

DoctorsListFile = "/home/SuchithSridhar/Python-Code/Duty-Rota/DoctorsListFile.csv"
SavedDoctors = "/home/SuchithSridhar/Python-Code/Duty-Rota/SavedDoctors.pickle"
GenerationFile = "/home/SuchithSridhar/Python-Code/Duty-Rota/ThisMonth.csv"


class Doctor:

    def __init__(self):
        self.name = ""
        self.total_week = 0
        self.total_ends = 0
        self.distrubution = {}

        self.is_available = False
        self.columns = []
        self.absent = []
        self.max_week = 0
        self.max_ends = 0

        self.week = 0
        self.ends = 0
        self.mon_dist = {}
        self.mon_types_week = {}
        self.mon_types_ends = {}
        self.days_since_last_duty = 0

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    def total(self):
        return self.week + self.ends

    def update_month(self, row):
        self.name = row[0]
        self.is_available = int(row[1])
        self.columns = [int(x) for x in row[2].split(',')]
        self.absent = self.calc_absent(row[3])
        self.max_week = int(row[4])
        self.max_ends = int(row[5])
        self.mon_dist = {x: 0 for x in self.columns}
        self.mon_types_week = self.mon_dist.copy()
        self.mon_types_ends = self.mon_dist.copy()

    def confirm_month(self):
        self.total_week += self.week
        self.total_ends += self.ends

        # adding the different columns records into the database
        m = self.mon_dist
        for col, val in self.distrubution:
            if col in m:
                self.distrubution[col] += m[col]

    def calc_absent(self, row):
        # private class
        dates = []
        sections = row.split(",")
        for item in sections:
            if "-" in item:
                dash = item.index("-")
                start = int(item[:dash])
                end = int(item[dash+1:])

                if start > end:
                    raise Exception
                if start < 1 or end > 31:
                    raise Exception
                if start == end:
                    dates.append(start)
                    continue

                x = [x for x in range(start, end+1)]
                dates.extend(x)

            else:
                d = int(item)
                if d < 1 or d > 31:
                    if d == 0:
                        pass
                    else:
                        raise Exception
                else:
                    dates.append(d)
        return dates


class NotPossibleError(Exception):
    pass


def get_doctor_list():
    try:
        with open(SavedDoctors, 'rb') as f:
            data = pickle.load(f)
    except FileNotFoundError:
        data = []
    return data


def sort_doctors_duty(doctor_list):
    n = len(doctor_list)
    for i in range(1, n):
        temp = doctor_list[i]
        j = i-1
        while j >= 0 and doctor_list[j].days_since_last_duty > temp.days_since_last_duty:
            doctor_list[j+1] = doctor_list[j]
            j -= 1
        doctor_list[j+1] = temp


def sort_eligible(eligible, column_number):
    n = len(eligible)
    for i in range(1, n):
        temp = eligible[i]
        j = i-1
        while j >= 0 and eligible[j].mon_dist[column_number] > temp.mon_dist[column_number]:
            eligible[j+1] = eligible[j]
            j -= 1
        eligible[j+1] = temp


def sort_columns(doctors_list):
    n = len(doctors_list)
    for i in range(1, n):
        temp = doctors_list[i]
        j = i-1
        while j >= 0 and len(doctors_list[j].columns) > len(temp.columns):
            doctors_list[j+1] = doctors_list[j]
            j -= 1
        doctors_list[j+1] = temp


def assign_doctor(doctor_list, column_number):
    doctor_list = doctor_list.copy()
    while True:
        eligible = []
        same_duty_count = []
        sort_doctors_duty(doctor_list)
        doctor_list.reverse()
        x = doctor_list[0].days_since_last_duty
        for doctor in doctor_list:
            if doctor.days_since_last_duty == x:
                if column_number in doctor.columns:
                    # this means that the doctor is a potential
                    # doctor for this field
                    eligible.append(doctor)

                # this is a list of all doctors who has the no
                # of completed duties the same
                same_duty_count.append(doctor)

        if eligible == []:
            new = []
            for doctor in doctor_list:
                if doctor not in same_duty_count:
                    new.append(doctor)

            doctor_list = new
            if new == []:
                raise NotPossibleError
            continue

        # --------------------------
        sort_columns(eligible)
        # sorts the doctors by the number of columns they can
        # work in

        eligible_2 = []
        priority_number = len(eligible[0].columns)

        for doctor in eligible:
            if len(doctor.columns) == priority_number:
                eligible_2.append(doctor)

        sort_eligible(eligible_2, column_number)

        eligible_3 = []
        days_col = eligible_2[0].mon_dist[column_number]

        for doctor in eligible_2:
            if doctor.mon_dist[column_number] == days_col:
                eligible_3.append(doctor)

        # once sorted the list will be arranged in the
        # number of times a person has done duty in this field

        # AT this point the doctors in the eligible 2 list:
        # - have gone most days without duty
        # - can work in this column
        # - have least number of columns they can work in
        # - have the least number of days worked in this column

        n = len(eligible_3)
        x = random.randrange(n)
        return eligible_3[x]


def create_doctor_list():
    flag = 0
    doctor_list = []
    with open(DoctorsListFile, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            if not flag:
                # Skip the heading row
                flag = 1
                continue

            row = [x.strip() if (x.strip() != "") else "0" for x in row]
            if row[1] != "0":
                doc = Doctor()
                doc.update_month(row)
                doctor_list.append(doc)

    return doctor_list


def is_weekend(date, startdate):
    return ((date-startdate) % 7 == 0 or (date-startdate-1) % 7 == 0)


def sort_ends(doctors_list):
    n = len(doctors_list)
    for i in range(1, n):
        temp = doctors_list[i]
        j = i-1
        while j >= 0 and (doctors_list[j].ends) > (temp.ends):
            doctors_list[j+1] = doctors_list[j]
            j -= 1
        doctors_list[j+1] = temp


big_list = []

def sort_total_days(doctors_list):
    n = len(doctors_list)
    for i in range(1, n):
        temp = doctors_list[i]
        j = i-1
        while j >= 0 and (doctors_list[j].total()) > (temp.total()):
            doctors_list[j+1] = doctors_list[j]
            j -= 1
        doctors_list[j+1] = temp


def duty_rota_assign(rows, columns, startdate):
    doctor_list = create_doctor_list()

    for row in range(1, rows+1):
        day = []
        new_list = [x for x in doctor_list if row not in x.absent]

        if not is_weekend(row, startdate):
        # if True:

            for col in range(1, columns+1):
                copy_list = [x for x in new_list]
                while True:
                    sort_total_days(copy_list)

                    a = []
                    min = copy_list[0].total()
                    for doc in copy_list:
                        if doc.total() == min:
                            a.append(doc)


                    try:
                        doc = assign_doctor(a, col)
                    except NotPossibleError:
                        copy_list = [x for x in copy_list if x not in a]
                    else:
                        break

                day.append(doc)


                # Section to be removed ----------------------------------------------------------------------------
                print("Happened on :", row, "for: ", doc, "extent :", doc.days_since_last_duty)


                doc.days_since_last_duty = -1
                doc.mon_dist[col] += 1
                doc.mon_types_week[col] += 1
                doc.week += 1

        else:

            for col in range(1, columns+1):
                new_copy = [x for x in new_list]
                sort_ends(new_copy)
                while True:
                    min = new_copy[0].ends
                    a = []
                    pos = 0
                
                    for doctor in new_copy:
                        if doctor.ends == min:
                            a.append(doctor)
                            pos += 1
                        else:
                            break

                    
                    try:
                        doc = assign_doctor(a, col)
                    except NotPossibleError:
                        print("----------------caught exception-----------------")
                        print("pos")
                        new_copy = new_copy[pos:]
                        if new_copy == []:
                            raise NotPossibleError
                    else:
                        break

                print("Happened on :", row, "for: ", doc, "extent :", doc.days_since_last_duty)

                day.append(doc)
                doc.days_since_last_duty = -1
                doc.mon_dist[col] += 1
                doc.mon_types_ends[col] += 1
                doc.ends += 1

        big_list.append(day+[is_weekend(row, startdate)])
        for doctor in doctor_list:
            doctor.days_since_last_duty += 1

    for d in doctor_list:
        print("-"*50)
        print(d.name)
        print(
            f"last = {d.days_since_last_duty}, week={d.week}, ends={d.ends}, total={d.week+d.ends}")
        # print(doctor.mon_types_ends, "week ends")
        # print(doctor.mon_types_week, "week days")
        print()


duty_rota_assign(31, 4, 6)
pp(big_list)
