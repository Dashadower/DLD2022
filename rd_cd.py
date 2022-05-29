from typing import List, Set

class Record:
    binary: str
    used: bool = False
    one_count: int
    representing_numbers: Set[int]

    def __init__(self, binary, representing_numbers):
        self.binary = binary
        self.one_count = self.binary.count("1")
        self.representing_numbers = representing_numbers

    def xor(self, x: str):
        # equivalent to hamming distance
        lhs = self.binary[:]
        rhs = x[:]
        ret_string = ""
        for lhs_char, rhs_str in zip(lhs, rhs):
            if lhs_char == rhs_str:
                ret_string += "0"
            else:
                ret_string += "1"

        return ret_string

    def __repr__(self):
        return f"({self.binary}: {','.join([str(x) for x in sorted(self.representing_numbers)])})"

    def __str__(self):
        return_string = ""
        for index, char in enumerate(self.binary):
            if char == "-": continue
            elif char == "0":
                return_string += f"x{index + 1}'"
            else:
                return_string += f"x{index + 1}"

        return return_string

    def __eq__(self, other):
        return self.binary == other.binary

    def __hash__(self):
        return hash(self.binary)

def find_pi(n_vars, minterms, dont_care_numbers):
    binary_grid = [[]]

    current_grid = binary_grid[-1]

    for term in minterms:
        current_grid.append(Record(str(bin(int(term)))[2:].rjust(n_vars, "0"), {term}))

    while True:
        progress = False
        current_grid = binary_grid[-1]

        if len(current_grid) == 0:
            break

        binary_grid.append([])
        added = set()
        for term_1 in current_grid:
            for term_2 in current_grid:
                if term_1.one_count > term_2.one_count:
                    continue

                xor = term_1.xor(term_2.binary)
                hamming = xor.count("1")

                if hamming == 1:
                    term_1.used = True
                    term_2.used = True
                    new_bin = ""

                    for index, char in enumerate(xor):
                        if char == "1":
                            new_bin += "-"
                        else:
                            new_bin += term_1.binary[index]

                    if new_bin in added:
                        continue

                    binary_grid[-1].append(
                        Record(new_bin, set(term_1.representing_numbers.union(term_2.representing_numbers))))
                    added.add(new_bin)

                    progress = True

        if not progress:
            break

    pi = set()

    for grid in binary_grid:
        for record in grid:
            if not record.used:
                pi.add(record)

    return pi


def find_epi(pis, dont_care_numbers):
    epi_list = {}
    for record in pis:
        if record.used: continue
        for rep_num in record.representing_numbers:
            if rep_num in epi_list:
                epi_list[rep_num] = None
            else:
                epi_list[rep_num] = record

    tmp_array = []
    for integer, record in epi_list.items():
        if integer in dont_care_numbers: continue
        if not record: continue
        tmp_array.append(record)

    epi = set(tmp_array)

    return epi


def column_dominance(pi_records: Set[Record], epi_records: Set[Record], minterms: Set[int], dontcares: Set[int]) -> Set[int]:
    # returns columns to exclude
    epi_covered_terms = set()
    for epi in epi_records:
        epi_covered_terms.update(epi.representing_numbers)

    target_columns = (minterms - dontcares) - epi_covered_terms
    column_dict = {}
    for column in target_columns:
        column_dict[column] = set()
    for pi in pi_records:
        if pi in epi_records: continue
        for number in pi.representing_numbers:
            if number in column_dict and number not in (dontcares.union(epi_covered_terms)):
                column_dict[number].add(pi.binary)

    for col1, cover1 in column_dict.items():
        if not col1: continue
        for col2, cover2 in column_dict.items():
            if col1 == col2: continue
            if not cover2: continue
            if cover2.issubset(cover1):
                print(f"minterm {col1} dominates minterm {col2}")
                if col1 in target_columns:
                    target_columns.remove(col1)

    return (minterms - dontcares) - epi_covered_terms - target_columns


def row_dominance(pi_records: Set[Record], epi_records: Set[Record], minterms: Set[int], dontcares: Set[int]) -> Set[str]:
    # returns binary strings of records to exclude
    epi_covered_numbers = set()
    for epi in epi_records:
        epi_covered_numbers.update(epi.representing_numbers)

    excluded_terms = set()

    for c1_record in pi_records - epi_records:
        for c2_record in pi_records - epi_records:
            if c1_record.binary == c2_record.binary: continue
            c1_cover = (c1_record.representing_numbers - dontcares) - epi_covered_numbers
            c2_cover = (c2_record.representing_numbers - dontcares) - epi_covered_numbers

            if c2_cover.issubset(c1_cover) and c1_record.binary not in excluded_terms:
                print(f"{c1_record} dominates {c2_record}")
                excluded_terms.add(c2_record.binary)

    return excluded_terms

if __name__ == '__main__':
    #n_vars = 4; minterms = {0, 4, 8, 10, 11, 12, 13, 15}; dontcares = {13, 15}
    #n_vars = 4; minterms = {1, 2, 3, 7, 9, 10, 11, 13, 15}; dontcares = {1, 10, 15}
    n_vars = 4; minterms = {0, 2, 5, 6, 7, 8, 10, 12, 13, 14, 15}; dontcares = set()
    keep_running = True
    n_iterations = 0

    pis = find_pi(n_vars, minterms, dontcares)
    epis = set()
    while keep_running:
        print("Iteration", n_iterations)

        #pis = pis.intersection(find_pi(n_vars, minterms, dontcares))

        epis = epis.union(find_epi(pis, dontcares))  # calculate epi

        pis = pis - epis

        epi_covered_numbers = set()
        for epi in epis:
            epi_covered_numbers.update(epi.representing_numbers)

        if (minterms - dontcares).issubset(epi_covered_numbers):  # check if EPI covers all implicants
            pis = set()
            break

        excluded_columns = column_dominance(pis, epis, minterms, dontcares)  # column dominance
        if not excluded_columns: keep_running = False
        dontcares = dontcares.union(excluded_columns)
        excluded_terms = row_dominance(pis, epis, minterms, dontcares)  # row dominance
        for binary in excluded_terms:
            remove_something = None
            for record in pis:
                if record.binary == binary:
                    remove_something = record
                    break

            if remove_something:
                pis.remove(remove_something)

        if not excluded_terms:
            keep_running = keep_running | False

        print("pi:", pis)
        print("epi:", epis)

        n_iterations += 1

    result = (pis - epis).union(epis)
    print("final terms:", result)
    print("standard form: f =", " + ".join([str(x) for x in result]))

