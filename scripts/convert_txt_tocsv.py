import sys
import os
import csv


# Function to check if the file path is a valid .txt file and exists
def check_txt_extension(file_path: list[str]) -> bool:
    print(f"📂 Files path: {file_path}")

    # Check file extension
    if not file_path.lower().endswith(".txt"):
        print("❌ Invalid file type. Only .txt files are allowed.")
        return

    # Check if file exists
    if not os.path.isfile(file_path):
        print("❌ File not found.")
        return

    return True


# Function to create a CSV file from numbers in "1.txt"
def create_csv_file(name_new_file: str, file_path:str):
    # List of all field names for the CSV
    field_names = [
        "Name Prefix",
        "First Name",
        "Middle Name",
        "Last Name",
        "Name Suffix",
        "Phonetic First Name",
        "Phonetic Middle Name",
        "Phonetic Last Name",
        "Nickname",
        "File As",
        "E-mail 1 - Label",
        "E-mail 1 - Value",
        "Phone 1 - Label",
        "Phone 1 - Value",
        "Address 1 - Label",
        "Address 1 - Country",
        "Address 1 - Street",
        "Address 1 - Extended Address",
        "Address 1 - City",
        "Address 1 - Region",
        "Address 1 - Postal Code",
        "Address 1 - PO Box",
        "Organization Name",
        "Organization Title",
        "Organization Department",
        "Birthday",
        "Event 1 - Label",
        "Event 1 - Value",
        "Relation 1 - Label",
        "Relation 1 - Value",
        "Website 1 - Label",
        "Website 1 - Value",
        "Custom Field 1 - Label",
        "Custom Field 1 - Value",
        "Notes",
        "Labels",
    ]

    # Convert field names to a dictionary with empty values
    dict_field_name = {}
    for filed_name in field_names:
        dict_field_name.update({filed_name: ""})

    # Read numbers from "1.txt" and prepare client data
    with open(file_path, "r") as txt:
        clients = []
        names = ["Cn25"]
        for number in txt.readlines():
            number = number.removesuffix("\n")
            client = dict_field_name.copy()
            client["First Name"] = names[0]
            client["Phone 1 - Value"] = number
            clients.append(client)

    # Write client data to a new CSV file
    with open(f"{name_new_file}.csv", "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=field_names)
        writer.writeheader()
        writer.writerows(clients)


# Main function to run the script from command line
def main():
    if len(sys.argv) < 2:
        print("Usage: python myscript.py <file_path>")
        input(
            "\nDrag and drop a file into the script, or run it with a file path.\nPress Enter to exit..."
        )
        return

    file_path = sys.argv[1]
    # Check if file is valid before creating CSV
    if check_txt_extension(file_path) == True:
        create_csv_file(file_path.split("\\")[-1].split(".")[0], file_path)
    input("\n✅ Done. Press Enter to exit...")


if __name__ == "__main__":
    main()

# -----------------
# Testing reminders:
# - Test check_txt_extension with:
#   - valid .txt file
#   - invalid extension
#   - non-existent file
# - Test create_csv_file:
#   - Prepare a "1.txt" with numbers
#   - Call create_csv_file and check the CSV output
#   - Check headers and values in the CSV
# -----------------
