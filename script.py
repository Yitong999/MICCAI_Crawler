import requests
from bs4 import BeautifulSoup
import re
from openpyxl import load_workbook
from tqdm import tqdm

# The base URL containing the list of papers
base_url = 'https://conferences.miccai.org/2023/papers/'
topics = [
    ('self-supervised', 3),
    ('contrastive', 2),
]
wb = load_workbook('valid_urls.xlsx')
ws = wb.active

# Function to fetch the list of papers
def get_paper_links(url):
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to retrieve content: {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    paper_links = [link.get('href') for link in soup.find_all('a', href=True) if 'Paper' in link.get('href')]
    
    # Construct full URLs (if not already complete)
    paper_links = [url + link if not link.startswith('http') else link for link in paper_links]

    return paper_links

def get_paper_topics(url):
    url = url.replace("/2023/papers//2023/papers/", "/2023/papers/") #url of the paper in the conference
    title = ""
    paper_link = ""
    modalities = []
    topics_here = []

    # print(url)
    response = requests.get(url)

    if response.status_code == 200:
        html_content = response.text
        # Parse the HTML content
        soup = BeautifulSoup(html_content, 'html.parser')

        # Find paper link
        for a_tag in soup.find_all('a', href=True):
            if 'https://doi.org' in a_tag['href']:
                paper_link = a_tag['href']
                # print(paper_link)

        # Find the title with class 'h1'
        title_h1 = soup.select('h1')[0]

        if title_h1:
            title = title_h1.get_text(strip=True)
            # print(title)

        # Find the div with class 'post-categories'
        post_categories_div = soup.find('div', class_='post-categories')

        # Check if the div is found
        if post_categories_div:
            # Find all 'a' tags within this div
            category_links = post_categories_div.find_all('a')
            
            # Iterate over each 'a' tag and get its text
            for link in category_links:
                category_name = link.get_text(strip=True)  # strip=True to remove any leading/trailing whitespaces
                if category_name.split(' - ')[0] == 'Modalities':
                    modalities.append(category_name.split(' - ')[1])


        text = soup.get_text()
        for topic in topics:
            word_count = len(re.findall(topic[0], text, re.IGNORECASE)) #case incensitive
            if word_count >= topic[1]:
                topics_here.append(topic[0])


        if len(topics_here) > 0:
            # print(title)
            # print(url)
            # print(paper_link)
            # print(topics_here)
            # print(modalities)
            write_to_excel(wb, title, url, paper_link, topics_here, modalities)
            # print()

            # return title, url, paper_link, topics_here, modalities
            return True

        # print(f"The word 'contrastive' appears {word_count} times on the webpage.")
        else: # Not the topic we want
            return False
    else:
        print("Failed to retrieve the webpage")
        return False

def write_to_excel(wb, title, url, doi, tags, modalities):
 
        # Prepare the data for the fifth column
    self_supervised = 'yes' if 'self-supervised' in tags else 'no'
    contrastive = 'yes' if 'contrastive' in tags else 'no'

    # Prepare the data for the sixth column (splitting by ' | ' is not applicable here as we only have one element)

    if len(modalities) == 0:
        images_modalities = 'not mentioned'
    else:
        images_modalities = ' | '.join(modalities)
    # Write data to the first row
    ws.append([title, url, doi, self_supervised, contrastive, images_modalities])

    # Save the workbook
    # wb.save("output.xlsx")
    



# Main process
if __name__ == '__main__':
    paper_links = get_paper_links(base_url)

    count = 0
    for link in tqdm(paper_links, leave=True):
        if get_paper_topics(link):
            count += 1

    

    wb.save("output.xlsx")
    print(f'find {count} relavant papers from {len(paper_links)} papers')


# https://conferences.miccai.org/2023/papers/001-Paper0829.html
# https://conferences.miccai.org/2023/papers//2023/papers/001-Paper0829.html