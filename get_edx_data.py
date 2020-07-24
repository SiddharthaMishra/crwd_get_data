import requests
import xmltodict
import json
import re

from bs4 import BeautifulSoup

from db import insert_course, is_uploaded_course


def parse_all_courses():
    # the rss feed will give us a list of courses, along with most of the required data
    xml_response = requests.get("https://www.edx.org/api/v2/report/course-feed/rss")
    
    # convert the XML response from the rss feed to a python dict
    parsed = xmltodict.parse(xml_response.text)
    
    return parsed['rss']['channel']['item']


# the picture and the instructors are not part of the rss feed
def get_picture_and_instructor(page_link):
    page_text = requests.get(page_link).text
    try:
        # parse the instructor and image using regex
        instructor = re.search("Person\",.*?\"name\":\"([^\"]*)\"", page_text).group(1)
        image_url = re.search("ImageObject\",.*?\"url\":\"([^\"]*)\"", page_text).group(1)
    except:
        return None, None

    return image_url, instructor



def main():
    course_list = parse_all_courses()

    to_print = []
    
    for course in course_list:


        if is_uploaded_course(course["title"]):
            continue

        # extract the unique course id from the full node. the node is a shortcut 
        # to the course page in the form https://edx.org/node/<unique id>

        id = course["guid"].split("/")[-1]
        
        # get the professor name and the picture by scrapping the webpage
        picture, professor = get_picture_and_instructor(course["link"])
        if picture is None:
            continue

        title = course["title"]

        required_data = [{
            "link": course["link"], 
            "title": course["title"], 
            "tags": [course["course:subject"]], 
            "description": course["description"],
            "unique_name": f"edx_{id}",
            "professor": professor,
            "picture": picture
            }]
        to_print.append(required_data)

        print(f"course {title} finished")

        insert_course(course["title"], course["link"], [course["course:subject"]],
        professor, picture, course["description"])


if __name__ == "__main__":
    main()