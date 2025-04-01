import os
import subprocess

SCRIPTS_DIR = "scripts"

# Mapping script directories to their respective scripts and descriptions
SCRIPT_DETAILS = {
    1: ("bjs_scrape", "main.py", "Scrapes data from BJ's Wholesale Club."),
    2: ("costco_scrape", "main.py", "Scrapes data from Costco."),
    3: ("instacart_scrape", "norating.py", "Scrapes data from Instacart (excluding ratings)."),
    4: ("resdepos_scrape", "main.py", "Scrapes data from Resdepos."),
    5: ("sams_scrape", "temp.py", "Scrapes data from Sam's Club."),
    6: ("jobs_scrape", "main.py", "Scrapes job listings from various sources."),
    7: ("instacart_aldi", "aldi.py", "Scrapes instacart-aldi."),
    8: ("instacart_bjs", "bjs.py", "Scrapes instacart-bjs."),
    9: ("instacart_costco", "costco.py", "Scrapes instacart-costco."),
    10: ("instacart_milams", "milams.py", "Scrapes instacart-milams."),
    11: ("instacart_publix", "publix.py", "Scrapes instacart-publix."),
    12: ("instacart_resdept", "restaurant_depot.py", "Scrapes instacart-resdept."),
    13: ("instacart_sabor_tropical", "sabor_tropical.py", "Scrapes instacart-sabor_tropical."),
    14: ("instacart_sams", "sams.py", "Scrapes instacart-sams."),
    15: ("instacart_target", "target.py", "Scrapes instacart-target."),
    16: ("instacart_walmart", "walmart.py", "Scrapes instacart-walmart."),
}

def list_scripts():
    """Lists available scripts with assigned numbers and descriptions."""
    print("\nAvailable scripts:")
    for num, (script, _, desc) in SCRIPT_DETAILS.items():
        print(f"{num}. {script}: {desc}")
    print()  # Adds a blank line for readability

def run_script(script_number):
    """Runs the specified script based on the selected number."""
    if script_number in SCRIPT_DETAILS:
        script_folder, script_file, _ = SCRIPT_DETAILS[script_number]
        script_path = os.path.join(SCRIPTS_DIR, script_folder, script_file)

        if os.path.exists(script_path):
            command = f"cd {SCRIPTS_DIR}/{script_folder} && python {script_file}"
            subprocess.run(command, shell=True)
        else:
            print(f"Error: Script '{script_file}' not found in '{script_folder}'.")
    else:
        print(f"Error: Invalid selection '{script_number}'.")

def main():
    """Main function to handle user input."""
    while True:
        user_input = input("\nEnter a number to run a script, 'list' to see available scripts, or 'exit' to quit: ").strip().lower()

        if user_input == "list":
            list_scripts()
        elif user_input == "exit":
            print("Exiting program.")
            break
        elif user_input.isdigit():
            script_number = int(user_input)
            run_script(script_number)
        else:
            print("Invalid input. Please enter a number corresponding to a script.")

if __name__ == "__main__":
    main()
