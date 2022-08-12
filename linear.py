from cmath import log
from fileinput import filename
from math import sqrt
import matplotlib.pyplot as plt
from scipy import stats

should_correct_vds = False

def prompt():
    return input("Which Ids-Vds (Vgs) file do you want to read?")

def get_interval(vgs_average, id_column, interval):
    left = interval[0]
    right = interval[1]

    left_index = 0
    right_index = 0

    for i in range(len(vgs_average)):
        if vgs_average[i] >= left:
            left_index = i
            break

    for i in range(len(vgs_average)):
        if vgs_average[i] >= right:
            right_index = i
            break

    return vgs_average[left_index:right_index], id_column[left_index:right_index]


def calc_average(data):
    result = []
    rows = len(data[0])

    for row in range(rows):
        sum = 0
        for column in range(len(data)):
            sum += data[column][row]
        result.append(sum / len(data))

    return result

def plot(vgs, id_data):
    plt.xlabel("Vgs")
    plt.ylabel("sqrt(Id)")
    plt.title("sqrt(Id) as function of Vgs")
    for i in range(len(id_data)):
        legend_key = "Vgs" + str(i + 1)
        legend_value = round(vds[i], 0)

        legend = legend_key + "=" + str(legend_value) + "V"

        # Plot every graph with its corresponding legend name
        plt.plot(vgs, id_data[i], label=legend)

    plt.legend()
    plt.show()

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

#
# Start op the program
#

file_name = prompt()

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

# Average of each vds column
vgs_average = calc_average(vgs_data)

# Round every item in vds_average to 2 decimal places
vgs_average = [round(x, 2) for x in vgs_average]

# plot(vgs_average, id_data)

# Calculate linear regression for id_data[0]

interval = [20, 35]
choose_a_graph = 2
choose_cox = 38.33 * pow(10, -9)
choose_w = 10000
choose_l = 10

pruned_vgs_average, pruned_id_data = get_interval(vgs_average, id_data[choose_a_graph], interval)



print(pruned_vgs_average)
print(pruned_id_data)

slope, intercept, r, p, std_err = stats.linregress(pruned_vgs_average, pruned_id_data)

vt = -intercept / slope

capacitance = choose_cox * pow(((choose_a_graph * 10) - vt), 2)
ratio = choose_w / (2 * choose_l)
ids = "TODO: IDS value from first set of data based on graph number chosen"

mobility = []

for id in ids:
    mobility.append(id / (ratio * capacitance))

print("Mobility: " + str(mobility))


