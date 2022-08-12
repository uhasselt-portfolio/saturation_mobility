from cmath import log
import matplotlib.pyplot as plt


def prompt():
    should_correct_vds = False
    file_name = input("Which Ids-Vds (Vgs) file do you want to read?")

    input_should_correct = input("Do you want to correct the Vds values? (y/n)")
    if input_should_correct == "y":
        should_correct_vds = True

    return file_name, should_correct_vds


# If next value is bigger than current value, then correct it
# Correction is done by taking the average of the current and second next value
def correct_vds(vds_data):

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

def plot(vds_average, ids_data):
    plt.xlabel("Vds")
    plt.ylabel("Ids")
    plt.title("Ids as function of Vds")
    for i in range(len(ids_data)):
        legend_key = "Vgs" + str(i + 1)
        legend_value = round(vgs[i], 0)
        legend = legend_key + "=" + str(legend_value) + "V"

        # Plot every graph with its corresponding legend name
        plt.plot(vds_average, ids_data[i], label=legend)

    plt.legend()
    plt.show()

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

#
# Start op the program
#

file_name, should_correct_vds = prompt()

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

# Correct vds values
if should_correct_vds:
    vds_data = correct_vds(vds_data)

# Average of each vds column
vds_average = calc_average(vds_data)

# Round every item in vds_average to 1 decimal places
vds_average = [round(x, 1) for x in vds_average]

plot(vds_average, ids_data)