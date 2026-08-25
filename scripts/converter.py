"""
Distance Unit Converter - inches/feet <-> cm/meters
==================================================================

WHAT THIS SCRIPT DOES
-----------------------
A small standalone command-line tool for converting flight-planning
distances between imperial units (inches, feet) and the metric units
the CoDrone EDU SDK actually accepts (cm, meters).

Useful when planning a mission in feet/inches (how most people think
about a physical space) but needing to enter cm/meters values into a
mission script's configuration section - see missions/grid_flight_plan.py
and missions/grid_3d_flight_plan.py for examples that use only cm.

PSEUDOCODE
-----------
    loop forever:
        ask: convert FROM which unit? (inches / feet / cm / meters)
        ask: enter the distance value
        based on the FROM unit, convert to BOTH other-system units:
            if FROM is inches or feet -> show result in cm and meters
            if FROM is cm or meters   -> show result in inches and feet
        print the result
        ask: convert another value? (y/n)
        if no: exit loop

CONVERSION FACTORS USED
--------------------------
    1 inch = 2.54 cm (exact, by definition)
    1 foot = 12 inches = 30.48 cm
    1 meter = 100 cm = 39.3701 inches (approx, standard rounding)

Usage:
    python converter.py
    Then follow the on-screen prompts.
"""

INCH_TO_CM = 2.54
FOOT_TO_INCH = 12
CM_TO_INCH = 1 / INCH_TO_CM
M_TO_CM = 100


def inches_to_metric(inches):
    """
    Convert a distance in inches to both cm and meters.

    Pseudocode:
        cm = inches * 2.54
        meters = cm / 100
        return (cm, meters)

    Args:
        inches (float): distance in inches.

    Returns:
        tuple(float, float): (distance_cm, distance_m)
    """
    cm = inches * INCH_TO_CM
    meters = cm / M_TO_CM
    return cm, meters


def feet_to_metric(feet):
    """
    Convert a distance in feet to both cm and meters.

    Pseudocode:
        inches = feet * 12
        cm = inches * 2.54
        meters = cm / 100
        return (cm, meters)

    Args:
        feet (float): distance in feet.

    Returns:
        tuple(float, float): (distance_cm, distance_m)
    """
    inches = feet * FOOT_TO_INCH
    cm, meters = inches_to_metric(inches)
    return cm, meters


def cm_to_imperial(cm):
    """
    Convert a distance in centimeters to both inches and feet.

    Pseudocode:
        inches = cm / 2.54
        feet = inches / 12
        return (inches, feet)

    Args:
        cm (float): distance in centimeters.

    Returns:
        tuple(float, float): (distance_in, distance_ft)
    """
    inches = cm * CM_TO_INCH
    feet = inches / FOOT_TO_INCH
    return inches, feet


def meters_to_imperial(meters):
    """
    Convert a distance in meters to both inches and feet.

    Pseudocode:
        cm = meters * 100
        inches, feet = cm_to_imperial(cm)
        return (inches, feet)

    Args:
        meters (float): distance in meters.

    Returns:
        tuple(float, float): (distance_in, distance_ft)
    """
    cm = meters * M_TO_CM
    inches, feet = cm_to_imperial(cm)
    return inches, feet


def prompt_unit_choice():
    """
    Ask the user which unit they're converting FROM, validating the
    input until it matches one of the accepted options.

    Pseudocode:
        loop:
            print the menu (1=inches, 2=feet, 3=cm, 4=meters)
            read input
            if input matches a valid choice: return it
            else: print an error and loop again

    Returns:
        str: one of "in", "ft", "cm", "m".
    """
    options = {
        "1": "in",
        "2": "ft",
        "3": "cm",
        "4": "m",
    }
    while True:
        print("\nConvert FROM which unit?")
        print("  1) inches")
        print("  2) feet")
        print("  3) centimeters (cm)")
        print("  4) meters (m)")
        choice = input("Enter 1-4: ").strip()
        if choice in options:
            return options[choice]
        print("Invalid choice - please enter 1, 2, 3, or 4.")


def prompt_distance_value():
    """
    Ask the user for the numeric distance to convert, validating that
    it parses as a number before returning it.

    Pseudocode:
        loop:
            read input
            try to convert input to a float
            if successful: return the float
            else: print an error and loop again

    Returns:
        float: the distance value entered.
    """
    while True:
        raw = input("Enter the distance value: ").strip()
        try:
            return float(raw)
        except ValueError:
            print("Invalid number - please enter a numeric value (e.g. 12 or 3.5).")


def convert_and_display(unit, value):
    """
    Convert a distance from the given unit into the other unit
    system and print both results.

    Pseudocode:
        if unit is inches or feet:
            convert to cm and meters
            print both metric results
        else (unit is cm or meters):
            convert to inches and feet
            print both imperial results

    Args:
        unit (str): one of "in", "ft", "cm", "m" - the FROM unit.
        value (float): the distance value in that unit.

    Returns:
        None. Prints the conversion results directly.
    """
    if unit == "in":
        cm, meters = inches_to_metric(value)
        print(f"\n{value} inches = {cm:.2f} cm = {meters:.4f} meters")

    elif unit == "ft":
        cm, meters = feet_to_metric(value)
        print(f"\n{value} feet = {cm:.2f} cm = {meters:.4f} meters")

    elif unit == "cm":
        inches, feet = cm_to_imperial(value)
        print(f"\n{value} cm = {inches:.4f} inches = {feet:.4f} feet")

    elif unit == "m":
        inches, feet = meters_to_imperial(value)
        print(f"\n{value} meters = {inches:.4f} inches = {feet:.4f} feet")


def main():
    """
    Entry point. Runs an interactive loop: ask for a FROM unit, ask
    for a value, convert and display the result, then ask whether to
    convert another value.

    Pseudocode:
        loop:
            unit = prompt_unit_choice()
            value = prompt_distance_value()
            convert_and_display(unit, value)
            ask: convert another? (y/n)
            if answer is not "y": break
        print a closing message
    """
    print("=" * 50)
    print("  Distance Converter: inches/feet <-> cm/meters")
    print("=" * 50)

    while True:
        unit = prompt_unit_choice()
        value = prompt_distance_value()
        convert_and_display(unit, value)

        again = input("\nConvert another value? (y/n): ").strip().lower()
        if again != "y":
            break

    print("\nDone.")


if __name__ == "__main__":
    main()
