import requests
import os
import json
import time


from bs4 import BeautifulSoup

from db import insert_course, is_uploaded_course


# Get the limit of elements to be scraped, or 0 or all
LIMIT = os.environ.get("SCRAPE_LIMIT", 200)

fails = 0

# Returns the path to get the slugs of the first 
def get_slug_path(start, n):
    return f"https://api.coursera.org/api/courses.v1?start={start}&limit={n}"


def parse_page_text(page_text):
    global fails
    try:
        # Run the HTML parser through the page text
        soup = BeautifulSoup(page_text, 'html.parser')
        #print(soup.prettify())

        # get the professor name
        professor_class = "instructor-name"
        professor = soup.find(class_=professor_class).string

        # get the course description
        description_class = "description"
        description = soup.find(class_="description").string

        # get tags
        parent_class = "Skills"
        parent = soup.find(class_=parent_class)
        
        tags = list(parent.strings)[1:] if parent else []

        # get picture
        image_class = "m-r-2"
        image_link = soup.find(class_=image_class)["src"]

        # add it to the DB
    except Exception as e:
        print("oops")
        print(e)
        with open(f"fail_page_{fails}.html", "w") as f:
            f.write(page_text)
            fails += 1
            return None, None, None, None

    return professor, description, tags, image_link


def main():

    time.sleep(2)

    # get the slugs for the courses
    slugs = {response["name"]:response["slug"] for response in requests.get(get_slug_path(0, LIMIT)).json()["elements"]}

    # get the data of all the courses, to either convert to json or add to the DB directly
    courses = []

    for course_name, slug in slugs.items():

        if is_uploaded_course(course_name):
            continue

        course_url = f"https://www.coursera.org/learn/{slug}" 
        page_text = requests.get(course_url).text
        professor, description, tags, image_link = parse_page_text(page_text)
        
        if professor is None:
            print(f"course {course_name} failed")
            continue

        insert_course(course_name, course_url, tags, professor, image_link, description)

        print(f"course {course_name} done")




if __name__ == "__main__":
    main()