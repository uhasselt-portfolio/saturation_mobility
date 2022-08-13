
from math import sqrt
import matplotlib.pyplot as plt
from matplotlib.widgets import TextBox
from scipy import stats

def prompt_vds():
    should_correct_vds = False
    file_name = input("Which Ids-Vds (Vgs) file do you want to read?\n")

    input_should_correct = input("Do you want to correct the Vds values? (y/n): ")
    if input_should_correct == "y":
        should_correct_vds = True

    return file_name, should_correct_vds

def prompt_vgs():
    return input("Which Vgs do you want to read? \n")

def prompt_graph_selection():
    volt = input("Specify the voltage you want to examine: ")

    left_interval = input("Specify the interval you want to plot, starting with the left: ")
    right_interval = input("Specify the interval you want to plot, starting with the right: ")

    cox = input("Specify you Cox value (will be multiplied bt 10^-9): ")
    cox = float(cox) * pow(10, -9)

    w = input("Specify you W value: ")
    l = input("Specify you L value: ")

    return [float(left_interval), float(right_interval)], float(cox), int(w), int(l), float(volt)

def prompt_invert():
    choice = input("Do you want to invert the data? (y/n): ")

    if choice == "y":
        return True
    else:
        return False

def print_mobility(mobility, vgs_data):
    print("\n=== Mobility === \n")

    for i in range(len(mobility)):
        print("Vgs: " + str(vgs_data[i]) + " = " + str(mobility[i]) + " cm^2/(V*s) \n")

    print("================= \n")
    print("\n")


# Multiplies all values in a sublist by -1
def invert_data(data, active):

    if active is False:
        return data

    for i in range(len(data)):
        for j in range(len(data[i])):
            data[i][j] = data[i][j] * -1
    return data

def invert_data_flat(data, active):

    if active is False:
        return data

    for i in range(len(data)):
        data[i] = data[i] * -1
    return data

# If next value is bigger than current value, then correct it
# Correction is done by taking the average of the current and second next value
def correct_vds(vds_data, parameter_count):

    corrected_vds = [[] for i in range(parameter_count // 2)]

    for i in range(len(vds_data)):
        for j in range(len(vds_data[i])):
            if j > 0:
                if vds_data[i][j] < vds_data[i][j-1]:
                    corrected_value = (vds_data[i][j - 1] + vds_data[i][j + 1]) / 2
                    corrected_vds[i].append(corrected_value)

                else:
                    corrected_vds[i].append(vds_data[i][j])
            else:
                corrected_vds[i].append(vds_data[i][j])

    return corrected_vds

def plot_process_transfer(vgs, id_data, vds, plot_transfer, should_invert):
    plot_transfer.set_xlabel("Vgs")
    plot_transfer.set_ylabel("sqrt(Id)")
    plot_transfer.title.set_text("sqrt(Id) as function of Vgs")

    invert_data(id_data, should_invert)

    for i in range(len(id_data)):
        legend_key = "Vds" + str(i + 1)
        legend_value = round(vds[i], 0) * -1 if should_invert else round(vds[i], 0)

        legend = legend_key + "=" + str(legend_value) + "V"

        # Plot every graph with its corresponding legend name
        plot_transfer.plot(vgs, id_data[i], label=legend)

    plot_transfer.legend()

    invert_data(id_data, should_invert)


def plot_process_output(vds_average, ids_data, vgs, plot_output, should_invert):
    plot_output.set_xlabel("Vds")
    plot_output.set_ylabel("Ids")
    plot_output.title.set_text("Ids as function of Vds")

    invert_data_flat(vds_average, should_invert)

    for i in range(len(ids_data)):
        legend_key = "Vgs" + str(i + 1)
        legend_value = round(vgs[i], 0) * -1 if should_invert else round(vgs[i], 0)
        legend = legend_key + "=" + str(legend_value) + "V"

        # Plot every graph with its corresponding legend name
        plot_output.plot(vds_average, ids_data[i], label=legend)

    plot_output.legend()

    invert_data_flat(vds_average, should_invert)

def get_interval(vgs_average, id_column, interval, should_invert):
    left = interval[0]
    right = interval[1]

    left_index = 0
    right_index = 0

    for i in range(len(vgs_average)):

        check_left = vgs_average[i] <= left if should_invert else vgs_average[i] >= left
        if check_left:
            print(str(vgs_average[i]) + " >= " + str(left))
            left_index = i
            break

    for i in range(len(vgs_average)):

        check_right = vgs_average[i] <= right if should_invert else vgs_average[i] >= right

        if check_right:
            print(str(vgs_average[i]) + " >= " + str(right))
            right_index = i
            break

    return vgs_average[left_index:right_index], id_column[left_index:right_index]

def calc_magic(ids_data, igs_data):
    rows = len(ids_data[0])
    columns = len(ids_data)

    converted =  []

    for column in range(columns):
        converted_column = []
        for row in range(rows):
            result = ids_data[column][row] + (igs_data[column][row] * 0.5)

            if result < 0:
                result = 0

            result = sqrt(result)
            converted_column.append(result)

        converted.append(converted_column)

    return converted

def calc_average(data):
    result = []
    rows = len(data[0])

    for row in range(rows):
        sum = 0
        for column in range(len(data)):
            sum += data[column][row]
        result.append(sum / len(data))

    return result

# Read content from Ids-Vds-Vgs-W10000-L10 file and print
def convert_headers(line):
    separated_by_space = line.split();

    data = []
    flag = False

    for item in separated_by_space:
        if item == "=":
            flag = True
        elif flag:
            data.append(float(item))
            flag = False

    return data

def process_transfer(file_name, plot_transfer, should_invert):

    file = open(file_name, "r")

    vds_raw = file.readline()

    vds = convert_headers(vds_raw)

    parameter_count = len(vds) * 3

    # Skip column names
    file.readline()

    # Initialize data
    vgs_data = [[] for i in range(parameter_count)]
    ids_data = [[] for i in range(parameter_count)]
    igs_data = [[] for i in range(parameter_count)]


    for line in file:
        data_list = line.split()

        for i in range(parameter_count):

            digit = float(data_list[i])
            if i % 3 == 0:
                vgs_data[i].append(digit)
            elif i % 3 == 1:
                ids_data[i].append(digit)
            else:
                igs_data[i].append(digit)

    # Delete empty sub lists
    vgs_data = [x for x in vgs_data if x]
    ids_data = [x for x in ids_data if x]
    igs_data = [x for x in igs_data if x]

    id_data = calc_magic(ids_data, igs_data)

    invert_data(vgs_data, should_invert)

    # Average of each vds column
    vgs_average = calc_average(vgs_data)

    # Round every item in vds_average to 2 decimal places
    vgs_average = [round(x, 2) for x in vgs_average]

    plot_process_transfer(vgs_average, id_data, vds, plot_transfer, should_invert)

    return id_data, vgs_data

def process_output(file_name, should_correct_vds, plot_output, should_invert):
    file = open(file_name, "r")

    vgs_raw = file.readline()

    vgs = convert_headers(vgs_raw)

    igs_raw = file.readline()

    igs = convert_headers(igs_raw)

    parameter_count = len(vgs) * 2

    # Skip column names
    file.readline()

    # Initialize data
    vds_data = [[] for i in range(parameter_count)]
    ids_data = [[] for i in range(parameter_count)]

    for line in file:
        data_list = line.split()

        for i in range(parameter_count):

            digit = float(data_list[i])
            if i % 2 == 0:
                vds_data[i].append(digit)
            else:
                ids_data[i].append(digit)


    # Delete empty sub lists
    vds_data = [x for x in vds_data if x]
    ids_data = [x for x in ids_data if x]

    invert_data(ids_data, should_invert)

    # Correct vds values
    if should_correct_vds:
        vds_data = correct_vds(vds_data, parameter_count)

    # Average of each vds column
    vds_average = calc_average(vds_data)

    # Round every item in vds_average to 1 decimal places
    vds_average = [round(x, 1) for x in vds_average]

    plot_process_output(vds_average, ids_data, vgs, plot_output, should_invert)

def process_linear(transfer_file_name, should_invert):
    interval, cox, w, l, volt = prompt_graph_selection()

    file = open(transfer_file_name, "r")

    vds_raw = file.readline()

    vds = convert_headers(vds_raw)

    parameter_count = len(vds) * 3

    # Skip column names
    file.readline()

    # Initialize data
    vgs_data = [[] for i in range(parameter_count)]
    ids_data = [[] for i in range(parameter_count)]
    igs_data = [[] for i in range(parameter_count)]


    for line in file:
        data_list = line.split()

        for i in range(parameter_count):

            digit = float(data_list[i])
            if i % 3 == 0:
                vgs_data[i].append(digit)
            elif i % 3 == 1:
                ids_data[i].append(digit)
            else:
                igs_data[i].append(digit)

    # Delete empty sub lists
    vgs_data = [x for x in vgs_data if x]
    ids_data = [x for x in ids_data if x]
    igs_data = [x for x in igs_data if x]

    id_data = calc_magic(ids_data, igs_data)

    invert_data(vgs_data, should_invert)
    invert_data(id_data, should_invert)
    invert_data_flat(vds, should_invert)

    # Average of each vds column
    vgs_average = calc_average(vgs_data)

    # Round every item in vds_average to 2 decimal places
    vgs_average = [round(x, 2) for x in vgs_average]

    # Calculate id_data column index
    # Find the closest vds value to volt and return its index
    vds_index = min(range(len(vds)), key=lambda i: abs(vds[i] - volt))

    # Calculate linear regression for id_data[0]
    pruned_vgs_average, pruned_id_data = get_interval(vgs_average, id_data[vds_index], interval, should_invert)

    print("Pruned vgs average: " + str(pruned_vgs_average))
    print("Pruned id data: " + str(pruned_id_data))

    slope, intercept, r, p, std_err = stats.linregress(pruned_vgs_average, pruned_id_data)

    print("Slope: " + str(slope))
    print("Intercept: " + str(intercept))

    vt = -intercept / slope

    print("Vt: " + str(vt))

    return vt, cox, w, l, vds_index

def process_mobility(vt, cox, w, l, vgs_data, id_data, id_data_column_index, should_invert):
    ratio = w / (2 * l)

    id_data_column = id_data[id_data_column_index]
    id_data_column = [x**2 for x in id_data_column]

    mobility = []

    for i in range(len(id_data_column)):
        voltage = vgs_data[i]
        id = id_data_column[i]
        capacitance = cox * pow((voltage - vt), 2)
        mobility.append(id / (ratio * capacitance))

    print_mobility(mobility, vgs_data)

def __main__():

    fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(10, 6))

    output_file_name, should_correct = prompt_vds()
    transfer_file_name = prompt_vgs()
    should_invert = prompt_invert()

    process_output(output_file_name, should_correct, axes[0], should_invert)
    id_data, vgs_data = process_transfer(transfer_file_name, axes[1], should_invert)

    plt.show()

    vt, cox, w, l, id_data_column_index = process_linear(transfer_file_name, should_invert)

    vgs_data_column = vgs_data[id_data_column_index]

    process_mobility(vt, cox, w, l, vgs_data_column, id_data, id_data_column_index, should_invert)

__main__();