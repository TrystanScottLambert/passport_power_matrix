"""
Module to scrape the Global Passport Power Ranking html into the ranked list.
"""

from rename import renames


def main():
    """main for scoping"""
    html_file = "power_index.html"

    # power rankings from passportindex.com
    with open(html_file, encoding="utf8") as file:
        lines = file.readlines()

    ranked_countries = [
        line.split("passport/")[1].split("/")[0].capitalize()
        for line in lines
        if "passport/" in line
    ]

    corrected = []
    for country in ranked_countries:
        if country in renames:
            corrected.append(renames[country])
        else:
            corrected.append(country)

    with open("power_index.csv", "w", encoding="utf8") as file:
        file.write("# rank, country_name\n")
        for i, name in enumerate(corrected):
            file.write(f"{i+1},{name}\n")


if __name__ == "__main__":
    main()
