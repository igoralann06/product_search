# with open("stores1.txt", "r") as file:
#     lines = file.readlines()

# # Step 2: Remove duplicates and strip whitespace/newline characters
# unique_list = list(set(line.strip() for line in lines))

# # Step 3 (Optional): Save the unique list back to the file
# with open("stores2.txt", "w") as file:
#     for item in unique_list:
#         file.write(f"{item}\n")

# print("Duplicates removed and updated in stores2.txt!")



with open("stores5.txt", "r") as file:
    lines = file.readlines()

# Step 2: Remove duplicates and strip whitespace/newline characters
unique_list = list(set(line.strip().split('?')[0] for line in lines))

# Step 3 (Optional): Save the unique list back to the file
with open("stores3.txt", "w") as file:
    for item in unique_list:
        file.write(f"{item}\n")

print("Duplicates removed and updated in stores3.txt!")